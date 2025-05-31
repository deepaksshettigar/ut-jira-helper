from jira import JIRA
from typing import List, Dict, Optional
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
            if not all([settings.jira_server, settings.jira_username, settings.jira_api_token]):
                logger.warning("Jira credentials not configured. Using mock data.")
                return
            
            self.jira_client = JIRA(
                server=settings.jira_server,
                basic_auth=(settings.jira_username, settings.jira_api_token)
            )
            logger.info("Jira client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Jira client: {e}")
            self.jira_client = None
    
    def is_configured(self) -> bool:
        """Check if Jira is properly configured"""
        return self.jira_client is not None
    
    def get_tasks(self, status: Optional[str] = None, assignee: Optional[str] = None, filter_criteria: Optional[FilterCriteria] = None) -> List[Dict]:
        """Get tasks from Jira with optional filtering"""
        if not self.is_configured():
            return self._get_mock_tasks(status, assignee, filter_criteria)
        
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
            
            # Execute search
            issues = self.jira_client.search_issues(jql, maxResults=100, expand='changelog')
            
            tasks = []
            for issue in issues:
                task = self._convert_issue_to_task(issue)
                tasks.append(task)
            
            # Apply additional filtering for criteria not supported by JQL
            if filter_criteria:
                tasks = self._apply_additional_filtering(tasks, filter_criteria)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error fetching tasks from Jira: {e}")
            return self._get_mock_tasks(status, assignee, filter_criteria)
    
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
    
    def _apply_additional_filtering(self, tasks: List[Dict], criteria: FilterCriteria) -> List[Dict]:
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
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Get a specific task by ID"""
        if not self.is_configured():
            return self._get_mock_task_by_id(task_id)
        
        try:
            issue = self.jira_client.issue(task_id)
            return self._convert_issue_to_task(issue)
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {e}")
            return self._get_mock_task_by_id(task_id)
    
    def create_task(self, title: str, description: str = "", assignee: str = "") -> Dict:
        """Create a new task in Jira"""
        if not self.is_configured():
            return self._create_mock_task(title, description, assignee)
        
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
            logger.error(f"Error creating task in Jira: {e}")
            return self._create_mock_task(title, description, assignee)
    
    def _convert_issue_to_task(self, issue) -> Dict:
        """Convert Jira issue to task dictionary"""
        resolved_date = None
        if hasattr(issue.fields, 'resolutiondate') and issue.fields.resolutiondate:
            try:
                resolved_date = datetime.fromisoformat(issue.fields.resolutiondate.replace('Z', '+00:00'))
            except:
                resolved_date = None
        
        created_date = None
        if hasattr(issue.fields, 'created') and issue.fields.created:
            try:
                created_date = datetime.fromisoformat(issue.fields.created.replace('Z', '+00:00'))
            except:
                created_date = None
        
        return {
            "id": str(issue.key),
            "title": issue.fields.summary,
            "description": getattr(issue.fields, 'description', '') or '',
            "status": str(issue.fields.status),
            "assignee": str(issue.fields.assignee) if issue.fields.assignee else 'Unassigned',
            "created_date": created_date.isoformat() if created_date else None,
            "resolved_date": resolved_date.isoformat() if resolved_date else None
        }
    
    def _get_mock_tasks(self, status: Optional[str] = None, assignee: Optional[str] = None, filter_criteria: Optional[FilterCriteria] = None) -> List[Dict]:
        """Fallback mock data when Jira is not configured"""
        # Create dates for realistic timeline - last 4 weeks
        now = datetime.now()
        base_date = now - timedelta(weeks=4)
        
        mock_tasks = [
            {
                "id": "JIRA-1",
                "title": "Implement login page",
                "description": "Create a responsive login page with email and password fields",
                "status": "In Progress",
                "assignee": "user1@example.com",
                "created_date": (base_date + timedelta(days=2)).isoformat(),
                "resolved_date": None
            },
            {
                "id": "JIRA-2",
                "title": "Fix navigation bug",
                "description": "Menu doesn't appear correctly on mobile devices",
                "status": "To Do",
                "assignee": "user2@example.com",
                "created_date": (base_date + timedelta(days=5)).isoformat(),
                "resolved_date": None
            },
            {
                "id": "JIRA-3",
                "title": "Update documentation",
                "description": "Add API documentation for the new endpoints",
                "status": "Done",
                "assignee": "user1@example.com",
                "created_date": (base_date + timedelta(days=1)).isoformat(),
                "resolved_date": (base_date + timedelta(days=8)).isoformat()
            },
            {
                "id": "JIRA-4",
                "title": "Create dashboard widget",
                "description": "Design and implement dashboard widgets for data visualization",
                "status": "To Do",
                "assignee": "user2@example.com",
                "created_date": (base_date + timedelta(days=10)).isoformat(),
                "resolved_date": None
            },
            {
                "id": "JIRA-5",
                "title": "Fix login authentication",
                "description": "Users unable to login with valid credentials",
                "status": "In Progress",
                "assignee": "user1@example.com",
                "created_date": (base_date + timedelta(days=7)).isoformat(),
                "resolved_date": None
            },
            {
                "id": "JIRA-6",
                "title": "Add user profile page",
                "description": "Create user profile management functionality",
                "status": "Done",
                "assignee": "user2@example.com",
                "created_date": (base_date + timedelta(days=3)).isoformat(),
                "resolved_date": (base_date + timedelta(days=14)).isoformat()
            },
            {
                "id": "JIRA-7",
                "title": "Implement search functionality",
                "description": "Add search capability to the application",
                "status": "Done",
                "assignee": "user1@example.com",
                "created_date": (base_date + timedelta(days=6)).isoformat(),
                "resolved_date": (base_date + timedelta(days=15)).isoformat()
            },
            {
                "id": "JIRA-8",
                "title": "Fix responsive design",
                "description": "Improve mobile responsiveness across all pages",
                "status": "Done",
                "assignee": "user2@example.com",
                "created_date": (base_date + timedelta(days=4)).isoformat(),
                "resolved_date": (base_date + timedelta(days=16)).isoformat()
            },
            {
                "id": "JIRA-9",
                "title": "Setup automated testing",
                "description": "Implement unit and integration tests",
                "status": "Done",
                "assignee": "user1@example.com",
                "created_date": (base_date + timedelta(days=9)).isoformat(),
                "resolved_date": (base_date + timedelta(days=21)).isoformat()
            },
            {
                "id": "JIRA-10",
                "title": "Database optimization",
                "description": "Optimize database queries for better performance",
                "status": "Done",
                "assignee": "user2@example.com",
                "created_date": (base_date + timedelta(days=12)).isoformat(),
                "resolved_date": (base_date + timedelta(days=22)).isoformat()
            }
        ]
        
        # Apply filters using either legacy parameters or filter_criteria
        filtered_tasks = mock_tasks
        
        if filter_criteria:
            # Apply structured filtering
            if filter_criteria.status:
                filtered_tasks = [task for task in filtered_tasks 
                                if task["status"] in filter_criteria.status]
            
            if filter_criteria.assignee:
                filtered_tasks = [task for task in filtered_tasks 
                                if task["assignee"] in filter_criteria.assignee]
            
            if filter_criteria.keywords:
                keyword_filtered = []
                for task in filtered_tasks:
                    task_text = f"{task['title']} {task['description']}".lower()
                    if any(keyword.lower() in task_text for keyword in filter_criteria.keywords):
                        keyword_filtered.append(task)
                filtered_tasks = keyword_filtered
        else:
            # Apply legacy filtering
            if status:
                filtered_tasks = [task for task in filtered_tasks if task["status"].lower() == status.lower()]
            if assignee:
                filtered_tasks = [task for task in filtered_tasks if task["assignee"] == assignee]
        
        return filtered_tasks
    
    def _get_mock_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Get mock task by ID"""
        mock_tasks = self._get_mock_tasks()
        for task in mock_tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def _create_mock_task(self, title: str, description: str = "", assignee: str = "") -> Dict:
        """Create mock task"""
        mock_tasks = self._get_mock_tasks()
        new_task = {
            "id": f"JIRA-{len(mock_tasks) + 1}",
            "title": title,
            "description": description,
            "status": "To Do",
            "assignee": assignee or "Unassigned",
            "created_date": datetime.now().isoformat(),
            "resolved_date": None
        }
        return new_task

    def get_weekly_resolved_average(self, assignee: Optional[str] = None, weeks: int = 4) -> Dict:
        """Calculate average resolved tasks per week with optional assignee filter"""
        all_tasks = self.get_tasks()
        
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