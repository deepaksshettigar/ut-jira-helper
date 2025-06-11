try:
    from jira import JIRA
except ImportError:
    JIRA = None
from typing import List, Dict, Optional, Any
from app.config import settings
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Import FilterCriteria from llm_service to avoid circular imports
try:
    from app.services.llm_service import FilterCriteria
except ImportError:
    # Fallback if circular import occurs
    from typing import NamedTuple
    class FilterCriteria(NamedTuple):
        status: Optional[List[str]] = None
        assignee: Optional[List[str]] = None
        keywords: Optional[List[str]] = None
        time_frame: Optional[str] = None
        priority: Optional[str] = None
        task_type: Optional[str] = None

class JiraService:
    """Service for interacting with Jira API"""
    
    def __init__(self):
        self.jira_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Jira client with credentials"""
        try:
            if JIRA is None:
                logger.warning("Jira library not available. Using mock data.")
                return
                
            if not all([settings.jira_server, settings.jira_username, settings.jira_api_token]):
                logger.warning("Jira credentials not configured. Using mock data.")
                return
            
            self.jira_client = JIRA(
                server=settings.jira_server,
                basic_auth=(settings.jira_username, settings.jira_api_token)
            )
            logger.info("Jira client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Jira client: %s", e)
            self.jira_client = None
    
    def is_configured(self) -> bool:
        """Check if Jira is properly configured"""
        return self.jira_client is not None
    
    def get_tasks(self, status: Optional[str] = None, assignee: Optional[str] = None, filter_criteria: Optional[FilterCriteria] = None, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get tasks from Jira with optional filtering and pagination"""
        if not self.is_configured():
            return []
        
        try:
            # Build JQL query from criteria
            jql_parts = []
            
            if settings.jira_project_key:
                jql_parts.append(f"project = {settings.jira_project_key}")
            
            # Use filter_criteria if provided, otherwise use legacy parameters
            if filter_criteria:
                jql_parts.extend(self._build_jql_from_criteria(filter_criteria))
            else:
                if status:
                    jql_parts.append(f"status = '{status}'")
                if assignee:
                    jql_parts.append(f"assignee = '{assignee}'")
            
            jql = " AND ".join(jql_parts) if jql_parts else "ORDER BY created DESC"
            
            # Execute search with pagination to get all results
            all_tasks = []
            start_at = 0
            batch_size = 50  # Use Jira's default safe batch size
            
            while len(all_tasks) < max_results:
                # Calculate how many more results we need
                remaining_needed = max_results - len(all_tasks)
                current_batch_size = min(batch_size, remaining_needed)
                
                # Execute batch search
                issues = self.jira_client.search_issues(
                    jql, 
                    startAt=start_at, 
                    maxResults=current_batch_size, 
                    expand='changelog'
                )
                
                # Convert issues to tasks for this batch
                batch_tasks = []
                for issue in issues:
                    task = self._convert_issue_to_task(issue)
                    batch_tasks.append(task)
                
                all_tasks.extend(batch_tasks)
                
                # Check if we've retrieved all available issues
                if len(batch_tasks) < current_batch_size or start_at + len(batch_tasks) >= issues.total:
                    break
                
                # Move to next batch
                start_at += len(batch_tasks)
            
            # Apply additional filtering for criteria not supported by JQL
            if filter_criteria:
                all_tasks = self._apply_additional_filtering(all_tasks, filter_criteria)
            
            return all_tasks[:max_results]  # Ensure we don't exceed requested max_results
            
        except Exception as e:
            logger.error("Error fetching tasks from Jira: %s", e)
            return []
    
    def _build_jql_from_criteria(self, criteria: FilterCriteria) -> List[str]:
        """Build JQL query parts from FilterCriteria"""
        jql_parts = []
        
        # Status filtering
        if criteria.status:
            if len(criteria.status) == 1:
                jql_parts.append(f"status = '{criteria.status[0]}'")
            else:
                status_list = "', '".join(criteria.status)
                jql_parts.append(f"status IN ('{status_list}')")
        
        # Assignee filtering
        if criteria.assignee:
            if len(criteria.assignee) == 1:
                jql_parts.append(f"assignee = '{criteria.assignee[0]}'")
            else:
                assignee_list = "', '".join(criteria.assignee)
                jql_parts.append(f"assignee IN ('{assignee_list}')")
        
        # Priority filtering
        if criteria.priority:
            jql_parts.append(f"priority = '{criteria.priority}'")
        
        # Keywords filtering (using text search)
        if criteria.keywords:
            keyword_queries = []
            for keyword in criteria.keywords:
                keyword_queries.append(f"text ~ '{keyword}'")
            jql_parts.append(f"({' OR '.join(keyword_queries)})")
        
        # Time frame filtering
        if criteria.time_frame:
            time_jql = self._convert_time_frame_to_jql(criteria.time_frame)
            if time_jql:
                jql_parts.append(time_jql)
        
        return jql_parts
    
    def _convert_time_frame_to_jql(self, time_frame: str) -> Optional[str]:
        """Convert natural language time frame to JQL"""
        lower_time = time_frame.lower()
        
        if 'today' in lower_time:
            return "created >= startOfDay()"
        elif 'this week' in lower_time:
            return "created >= startOfWeek()"
        elif 'last week' in lower_time:
            return "created >= startOfWeek(-1w) AND created < startOfWeek()"
        elif 'this month' in lower_time:
            return "created >= startOfMonth()"
        
        return None
    
    def _apply_additional_filtering(self, tasks: List[Dict[str, Any]], criteria: FilterCriteria) -> List[Dict[str, Any]]:
        """Apply additional filtering that couldn't be done in JQL"""
        filtered_tasks = tasks
        
        # Additional keyword filtering on task content
        if criteria.keywords:
            keyword_filtered = []
            for task in filtered_tasks:
                task_text = f"{task.get('title', '')} {task.get('description', '')}".lower()
                if any(keyword.lower() in task_text for keyword in criteria.keywords):
                    keyword_filtered.append(task)
            filtered_tasks = keyword_filtered
        
        return filtered_tasks
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task by ID"""
        if not self.is_configured():
            return None
        
        try:
            issue = self.jira_client.issue(task_id)
            return self._convert_issue_to_task(issue)
        except Exception as e:
            logger.error("Error fetching task %s: %s", task_id, e)
            return None
    
    def create_task(self, title: str, description: str = "", assignee: str = "") -> Dict[str, Any]:
        """Create a new task in Jira"""
        if not self.is_configured():
            return {
                "id": f"NO-JIRA-{hash(title) % 1000}",
                "title": title,
                "description": description,
                "status": "To Do",
                "assignee": assignee or "Unassigned",
                "created_date": datetime.now().isoformat(),
                "updated_date": datetime.now().isoformat(),
                "resolved_date": None,
                "start_date": datetime.now().isoformat(),
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "priority": "Medium"
            }
        
        try:
            issue_dict = {
                'project': {'key': settings.jira_project_key},
                'summary': title,
                'description': description,
                'issuetype': {'name': 'Task'},
            }
            
            if assignee:
                issue_dict['assignee'] = {'name': assignee}
            
            new_issue = self.jira_client.create_issue(fields=issue_dict)
            return self._convert_issue_to_task(new_issue)
            
        except Exception as e:
            logger.error("Error creating task in Jira: %s", e)
            return {
                "id": f"NO-JIRA-{hash(title) % 1000}",
                "title": title,
                "description": description,
                "status": "To Do",
                "assignee": assignee or "Unassigned",
                "created_date": datetime.now().isoformat(),
                "updated_date": datetime.now().isoformat(),
                "resolved_date": None,
                "start_date": datetime.now().isoformat(),
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "priority": "Medium"
            }
    
    def _convert_issue_to_task(self, issue: Any) -> Dict[str, Any]:
        """Convert Jira issue to task dictionary"""
        # Debug logging to see what fields are available
        logger.debug(f"Converting issue {issue.key}, available fields: {dir(issue.fields)}")
        if hasattr(issue.fields, 'duedate'):
            logger.debug(f"Due date field value: {issue.fields.duedate}")
        if hasattr(issue.fields, 'priority'):
            logger.debug(f"Priority field value: {issue.fields.priority}")
        
        # Check for start date fields (common variations)
        start_date_fields = ['startdate', 'customfield_10015', 'customfield_10016', 'customfield_10002']
        for field_name in start_date_fields:
            if hasattr(issue.fields, field_name):
                logger.debug(f"Found start date field {field_name}: {getattr(issue.fields, field_name)}")
        
        resolved_date = None
        if hasattr(issue.fields, 'resolutiondate') and issue.fields.resolutiondate:
            try:
                resolved_date = datetime.fromisoformat(issue.fields.resolutiondate.replace('Z', '+00:00'))
            except Exception:
                resolved_date = None
        
        created_date = None
        if hasattr(issue.fields, 'created') and issue.fields.created:
            try:
                created_date = datetime.fromisoformat(issue.fields.created.replace('Z', '+00:00'))
            except Exception:
                created_date = None
        
        # Extract updated date
        updated_date = None
        if hasattr(issue.fields, 'updated') and issue.fields.updated:
            try:
                updated_date = datetime.fromisoformat(issue.fields.updated.replace('Z', '+00:00'))
            except Exception:
                updated_date = None
        
        # Extract start date (try common field names)
        start_date = None
        start_date_fields = ['startdate', 'customfield_10015', 'customfield_10016', 'customfield_10002']
        for field_name in start_date_fields:
            if hasattr(issue.fields, field_name):
                field_value = getattr(issue.fields, field_name)
                if field_value:
                    try:
                        if isinstance(field_value, str):
                            start_date = datetime.fromisoformat(field_value.replace('Z', '+00:00'))
                        else:
                            # Might be a datetime object already
                            start_date = field_value
                        break
                    except Exception:
                        continue
        
        # Extract due date
        due_date = None
        if hasattr(issue.fields, 'duedate') and issue.fields.duedate:
            try:
                due_date = datetime.fromisoformat(issue.fields.duedate.replace('Z', '+00:00'))
            except Exception:
                due_date = None
        
        # Extract priority
        priority = None
        if hasattr(issue.fields, 'priority') and issue.fields.priority:
            priority = str(issue.fields.priority.name) if hasattr(issue.fields.priority, 'name') else str(issue.fields.priority)
        
        return {
            "id": str(issue.key),
            "title": issue.fields.summary,
            "description": getattr(issue.fields, 'description', '') or '',
            "status": str(issue.fields.status),
            "assignee": str(issue.fields.assignee) if issue.fields.assignee else 'Unassigned',
            "created_date": created_date.isoformat() if created_date else None,
            "updated_date": updated_date.isoformat() if updated_date else None,
            "resolved_date": resolved_date.isoformat() if resolved_date else None,
            "start_date": start_date.isoformat() if start_date else None,
            "due_date": due_date.isoformat() if due_date else None,
            "priority": priority or 'Medium'
        }
    


    def get_weekly_resolved_average(self, assignee: Optional[str] = None, weeks: int = 4) -> Dict[str, Any]:
        """Calculate average resolved tasks per week with optional assignee filter"""
        all_tasks = self.get_tasks(max_results=1000)  # Get more tasks for analytics
        
        # Filter by assignee if provided
        if assignee:
            all_tasks = [task for task in all_tasks if task.get("assignee") == assignee]
        
        # Filter only resolved tasks (Done status)
        resolved_tasks = [task for task in all_tasks 
                         if task.get("status") == "Done" and task.get("resolved_date")]
        
        if not resolved_tasks:
            return {
                "average_per_week": 0,
                "total_resolved": 0,
                "weeks_analyzed": weeks,
                "assignee": assignee,
                "weekly_breakdown": {}
            }
        
        # Group tasks by week
        now = datetime.now()
        weekly_counts = {}
        
        for week_offset in range(weeks):
            week_start = now - timedelta(weeks=week_offset + 1)
            week_end = now - timedelta(weeks=week_offset)
            week_key = f"Week {week_offset + 1} ago"
            
            week_count = 0
            for task in resolved_tasks:
                resolved_date = datetime.fromisoformat(task["resolved_date"].replace('Z', '+00:00'))
                if week_start <= resolved_date < week_end:
                    week_count += 1
            
            weekly_counts[week_key] = week_count
        
        total_resolved = sum(weekly_counts.values())
        average_per_week = total_resolved / weeks if weeks > 0 else 0
        
        return {
            "average_per_week": round(average_per_week, 2),
            "total_resolved": total_resolved,
            "weeks_analyzed": weeks,
            "assignee": assignee,
            "weekly_breakdown": weekly_counts
        }

# Global instance
jira_service = JiraService()