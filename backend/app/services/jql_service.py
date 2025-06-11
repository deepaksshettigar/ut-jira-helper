import re
from typing import List, Dict, Optional, Tuple
from app.services.llm_service import llm_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class JQLConverter:
    """Service for converting natural language queries to JQL"""
    
    def __init__(self):
        self.llm_service = llm_service
        
        # Keep minimal mappings only for fallback pattern matching
        self.basic_patterns = {
            'status_mappings': {
                'todo': 'To Do',
                'open': 'Open', 
                'progress': 'In Progress',
                'done': 'Done',
                'closed': 'Closed'
            },
            'time_patterns': {
                r'today': 'startOfDay()',
                r'yesterday': 'startOfDay(-1d)',
                r'this week': 'startOfWeek()',
                r'last week': 'startOfWeek(-1w)',
                r'this month': 'startOfMonth()',
                r'last month': 'startOfMonth(-1M)'
            }
        }
    
    def convert_to_jql(self, natural_language: str, context: Optional[str] = None) -> Tuple[str, str]:
        """
        Convert natural language query to JQL
        Returns: (jql_query, explanation)
        """
        logger.info(f"Converting query: '{natural_language}'")
        
        # Check if LLM service is available
        is_llm_available = self.llm_service.is_available()
        logger.info(f"LLM service available: {is_llm_available}")
        
        # Always try LLM first - feed query directly without manipulation
        if is_llm_available:
            try:
                result = self._convert_with_llm(natural_language, context)
                logger.info(f"LLM conversion successful: {result}")
                return result
            except Exception as e:
                logger.warning(f"LLM conversion failed: {e}, falling back to basic pattern matching")
        else:
            logger.info("LLM not available, using pattern matching")
        
        # Only use pattern matching as true fallback when LLM is unavailable
        result = self._convert_with_basic_patterns(natural_language)
        logger.info(f"Pattern matching result: {result}")
        return result
    
    def _convert_with_llm(self, query: str, context: Optional[str]) -> Tuple[str, str]:
        """Convert using LLM model - feed query directly without preprocessing"""
        prompt = self._build_jql_conversion_prompt(query, context)
        logger.info(f"LLM prompt: {prompt[:200]}...")
        
        try:
            # Use correct parameter names: max_length instead of max_tokens
            response = self.llm_service.generate_response(prompt, max_length=300, temperature=0.1)
            logger.info(f"LLM raw response: {response}")
            
            # Parse LLM response to extract JQL and explanation
            jql_query, explanation = self._parse_llm_response(response)
            logger.info(f"Parsed JQL: '{jql_query}', Explanation: '{explanation}'")
            
            # Only do basic validation - don't modify the LLM's output
            if jql_query:
                jql_query = self._basic_validation(jql_query)
                return jql_query, explanation or f"Generated JQL for: {query}"
            else:
                raise ValueError("No valid JQL found in LLM response")
                
        except Exception as e:
            logger.error(f"LLM JQL conversion error: {e}")
            raise
    
    def _parse_llm_response(self, response: str) -> Tuple[str, str]:
        """Parse LLM response to extract JQL and explanation"""
        if not response or not response.strip():
            logger.warning("Empty response from LLM")
            return "", ""
            
        lines = response.strip().split('\n')
        jql_query = ""
        explanation = ""
        
        logger.info(f"Parsing LLM response lines: {lines}")
        
        for line in lines:
            line = line.strip()
            if line.startswith('JQL:'):
                jql_query = line.replace('JQL:', '').strip()
                logger.info(f"Found JQL line: '{jql_query}'")
            elif line.startswith('Explanation:'):
                explanation = line.replace('Explanation:', '').strip()
                logger.info(f"Found explanation: '{explanation}'")
            elif not jql_query and ('=' in line or 'ORDER BY' in line or 'project' in line):
                # If no explicit JQL: prefix, try to identify the JQL line
                jql_query = line
                logger.info(f"Inferred JQL line: '{jql_query}'")
        
        # If still no JQL found, try to extract from the entire response
        if not jql_query:
            # Look for patterns that suggest this is a JQL query
            for line in lines:
                line = line.strip()
                if any(keyword in line.upper() for keyword in ['PROJECT', 'STATUS', 'ASSIGNEE', 'CREATED', 'ORDER BY']):
                    jql_query = line
                    logger.info(f"Found JQL by keyword matching: '{jql_query}'")
                    break
        
        return jql_query, explanation
    
    def _basic_validation(self, jql: str) -> str:
        """Basic JQL validation - minimal cleanup only"""
        if not jql:
            return ""
            
        # Remove extra whitespace
        jql = re.sub(r'\s+', ' ', jql.strip())
        
        # Remove quotes around the entire query if present
        if jql.startswith('"') and jql.endswith('"'):
            jql = jql[1:-1]
        
        # Ensure we have a valid query
        if not jql or jql.lower() in ['none', 'null', 'empty']:
            return ""
        
        # Add ORDER BY if not present
        if 'ORDER BY' not in jql.upper():
            jql += " ORDER BY created DESC"
        
        return jql
    
    def _convert_with_basic_patterns(self, query: str) -> Tuple[str, str]:
        """Enhanced pattern matching fallback when LLM is unavailable"""
        query_lower = query.lower()
        jql_parts = []
        
        logger.info(f"Using pattern matching for: '{query}'")
        
        # Add project filter if configured
        if settings.jira_project_key:
            jql_parts.append(f"project = {settings.jira_project_key}")
        
        # Enhanced status detection
        status_found = False
        for status_word, jql_status in self.basic_patterns['status_mappings'].items():
            if status_word in query_lower:
                jql_parts.append(f"status = '{jql_status}'")
                status_found = True
                logger.info(f"Found status: {jql_status}")
                break
        
        # Enhanced time detection
        time_found = False
        for time_pattern, jql_time in self.basic_patterns['time_patterns'].items():
            if re.search(time_pattern, query_lower):
                jql_parts.append(f"created >= {jql_time}")
                time_found = True
                logger.info(f"Found time pattern: {time_pattern} -> {jql_time}")
                break
        
        # Check for assignee patterns
        if 'unassigned' in query_lower:
            jql_parts.append("assignee is EMPTY")
            logger.info("Found unassigned pattern")
        elif 'my' in query_lower or 'assigned to me' in query_lower:
            jql_parts.append("assignee = currentUser()")
            logger.info("Found 'my tasks' pattern")
        
        # Check for priority
        if 'high priority' in query_lower or 'urgent' in query_lower:
            jql_parts.append("priority = High")
            logger.info("Found high priority pattern")
        
        # Check for issue type
        if 'bug' in query_lower:
            jql_parts.append("issuetype = Bug")
            logger.info("Found bug issue type")
        elif 'task' in query_lower:
            jql_parts.append("issuetype = Task")
            logger.info("Found task issue type")
        
        # Build JQL
        if jql_parts:
            jql_query = " AND ".join(jql_parts) + " ORDER BY created DESC"
        else:
            # If no patterns matched, provide a basic query
            if settings.jira_project_key:
                jql_query = f"project = {settings.jira_project_key} ORDER BY created DESC"
            else:
                jql_query = "ORDER BY created DESC"
        
        explanation = f"Pattern matching found: {', '.join([part.split(' = ')[0] if ' = ' in part else part for part in jql_parts]) if jql_parts else 'no specific patterns'}"
        
        logger.info(f"Final pattern matching result: '{jql_query}'")
        return jql_query, explanation
    
    def _build_jql_conversion_prompt(self, query: str, context: Optional[str]) -> str:
        """Build prompt for LLM JQL conversion"""
        project_filter = f"project = {settings.jira_project_key} AND " if settings.jira_project_key else ""
        
        return f"""Convert this natural language query to valid JQL (Jira Query Language).

Query: "{query}"
Context: {context or "General Jira issue search"}

JQL Guidelines:
- Common fields: project, status, assignee, priority, issuetype, created, updated, summary, description
- Status values: "To Do", "In Progress", "Done", "Open", "Closed", "Resolved"
- Priority values: "Lowest", "Low", "Medium", "High", "Highest"
- Issue types: "Bug", "Task", "Story", "Epic", "Sub-task"
- Time functions: startOfDay(), startOfWeek(), startOfMonth(), startOfYear()
- Time modifiers: startOfDay(-1d) for yesterday, startOfWeek(-1w) for last week
- Text search: summary ~ "keyword" or description ~ "keyword"
- Assignee: assignee = "username" or assignee is EMPTY for unassigned
- Multiple values: status IN ("To Do", "In Progress")

{"Project context: Always include " + project_filter if project_filter else ""}

Examples:
"issues started last month" → {project_filter}created >= startOfMonth(-1M) ORDER BY created DESC
"unassigned high priority bugs" → {project_filter}assignee is EMPTY AND priority = High AND issuetype = Bug ORDER BY created DESC  
"my tasks in progress" → {project_filter}assignee = currentUser() AND status = "In Progress" ORDER BY created DESC

Important: 
- For time queries like "started", "created", "began" use the created field
- For "last month", "this week" etc, use appropriate time functions
- Always end with ORDER BY clause
- Don't include unnecessary text search if the query is about time, status, assignee, etc.

Convert the query and respond in this exact format:
JQL: [your JQL query]
Explanation: [brief explanation]"""
    
    def get_query_suggestions(self, current_query: str) -> List[str]:
        """Generate suggestions for follow-up queries"""
        return [
            "Show unassigned items",
            "Add time filter (this week, last month)",
            "Filter by status (in progress, done)",
            "Filter by priority (high, urgent)",
            "Show my assigned tasks"
        ]

# Global instance
jql_converter = JQLConverter()
