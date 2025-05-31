from jira import JIRA
from typing import List, Dict, Optional
from app.config import settings
import logging

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
        return {
            "id": str(issue.key),
            "title": issue.fields.summary,
            "description": getattr(issue.fields, 'description', '') or '',
            "status": str(issue.fields.status),
            "assignee": str(issue.fields.assignee) if issue.fields.assignee else 'Unassigned'
        }
    
    def _get_mock_tasks(self, status: Optional[str] = None, assignee: Optional[str] = None, filter_criteria: Optional[FilterCriteria] = None) -> List[Dict]:
        """Fallback mock data when Jira is not configured"""
        mock_tasks = [
            {
                "id": "JIRA-1",
                "title": "Implement login page",
                "description": "Create a responsive login page with email and password fields",
                "status": "In Progress",
                "assignee": "user1@example.com"
            },
            {
                "id": "JIRA-2",
                "title": "Fix navigation bug",
                "description": "Menu doesn't appear correctly on mobile devices",
                "status": "To Do",
                "assignee": "user2@example.com"
            },
            {
                "id": "JIRA-3",
                "title": "Update documentation",
                "description": "Add API documentation for the new endpoints",
                "status": "Done",
                "assignee": "user1@example.com"
            },
            {
                "id": "JIRA-4",
                "title": "Create dashboard widget",
                "description": "Design and implement dashboard widgets for data visualization",
                "status": "To Do",
                "assignee": "user2@example.com"
            },
            {
                "id": "JIRA-5",
                "title": "Fix login authentication",
                "description": "Users unable to login with valid credentials",
                "status": "In Progress",
                "assignee": "user1@example.com"
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
            "assignee": assignee or "Unassigned"
        }
        return new_task

# Global instance
jira_service = JiraService()