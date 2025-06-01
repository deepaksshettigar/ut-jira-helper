import re
from typing import List, Optional, Tuple
from app.services.llm_service import llm_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class JQLConverter:
    """Service for converting natural language queries to JQL"""
    
    def __init__(self):
        self.llm_service = llm_service
        
        # Common JQL mappings
        self.status_mappings = {
            'todo': 'To Do',
            'to do': 'To Do',
            'pending': 'To Do',
            'open': 'Open',
            'in progress': 'In Progress',
            'working': 'In Progress',
            'progress': 'In Progress',
            'doing': 'In Progress',
            'done': 'Done',
            'completed': 'Done',
            'finished': 'Done',
            'resolved': 'Resolved',
            'closed': 'Closed'
        }
        
        self.priority_mappings = {
            'low': 'Low',
            'medium': 'Medium', 
            'high': 'High',
            'urgent': 'High',
            'critical': 'Highest',
            'highest': 'Highest',
            'lowest': 'Lowest'
        }
        
        self.issue_type_mappings = {
            'bug': 'Bug',
            'task': 'Task',
            'story': 'Story',
            'epic': 'Epic',
            'subtask': 'Sub-task',
            'improvement': 'Improvement'
        }
        
        # Special assignee patterns
        self.assignee_patterns = {
            'unassigned': 'assignee is EMPTY',
            'no assignee': 'assignee is EMPTY',
            'not assigned': 'assignee is EMPTY',
            'without assignee': 'assignee is EMPTY',
            'nobody assigned': 'assignee is EMPTY',
            'no one assigned': 'assignee is EMPTY'
        }
        
        # Special status patterns
        self.status_patterns = {
            'not done': 'status != "Done"',
            'incomplete': 'status != "Done"',
            'active': 'status IN ("To Do", "In Progress", "Open")',
            'outstanding': 'status != "Done"',
            'pending work': 'status IN ("To Do", "In Progress")',
            'open items': 'status IN ("To Do", "Open")',
            'work in progress': 'status = "In Progress"',
            'completed': 'status IN ("Done", "Resolved", "Closed")'
        }
        
        self.time_patterns = {
            r'today': 'startOfDay()',
            r'yesterday': 'startOfDay(-1d)',
            r'this week': 'startOfWeek()',
            r'last week': 'startOfWeek(-1w)',
            r'this month': 'startOfMonth()',
            r'last month': 'startOfMonth(-1M)',
            r'(\d+)\s*days?\s*ago': r'startOfDay(-\1d)',
            r'(\d+)\s*weeks?\s*ago': r'startOfWeek(-\1w)',
            r'(\d+)\s*months?\s*ago': r'startOfMonth(-\1M)'
        }
    
    def convert_to_jql(self, natural_language: str, context: Optional[str] = None) -> Tuple[str, str]:
        """
        Convert natural language query to JQL using LLM
        Returns: (jql_query, explanation)
        """
        # Always try LLM conversion first if available
        llm_available = self.llm_service.is_available()
        print(f"[DEBUG] LLM service object: {self.llm_service}")
        print(f"[DEBUG] LLM service.llm: {self.llm_service.llm}")
        print(f"[DEBUG] LLM available: {llm_available}")
        logger.info(f"LLM available: {llm_available}")
        
        if llm_available:
            try:
                print(f"[DEBUG] Using LLM conversion for query: {natural_language}")
                logger.info(f"Using LLM conversion for query: {natural_language}")
                return self._convert_with_llm(natural_language, context)
            except Exception as e:
                print(f"[DEBUG] LLM conversion failed: {e}, falling back to basic JQL")
                logger.warning(f"LLM conversion failed: {e}, falling back to basic JQL")
                # Simple fallback without pattern matching
                return self._create_basic_fallback_jql(natural_language)
        else:
            print(f"[DEBUG] LLM not available, using basic fallback")
            logger.warning("LLM not available, using basic fallback")
            return self._create_basic_fallback_jql(natural_language)
    
    def _should_use_pattern_matching(self, query: str) -> bool:
        """Check if query should be handled by pattern matching for high confidence"""
        # High confidence patterns that work better with pattern matching
        high_confidence_patterns = [
            # Unassigned patterns - these are very specific
            'unassigned', 'no assignee', 'not assigned', 'without assignee', 
            'nobody assigned', 'no one assigned',
            # Simple status patterns
            'todo', 'to do', 'pending', 'open', 'in progress', 'done', 'resolved', 'closed',
            # Simple priority patterns  
            'highest', 'high', 'medium', 'low', 'lowest',
            # Simple issue type patterns
            'bug', 'task', 'story', 'epic', 'subtask',
            # Simple time patterns
            'today', 'yesterday', 'this week', 'last week', 'this month', 'last month',
        ]
        
        # If query is very simple (contains high confidence patterns), use pattern matching
        simple_word_count = len([word for word in query.split() if word not in ['show', 'me', 'all', 'the', 'find', 'get', 'list', 'items', 'issues', 'tasks']])
        
        return (any(pattern in query for pattern in high_confidence_patterns) and 
                simple_word_count <= 3)
    
    def _convert_with_llm(self, query: str, context: Optional[str]) -> Tuple[str, str]:
        """Convert using LLM model"""
        print(f"[DEBUG] _convert_with_llm called with query: {query}")
        prompt = self._build_jql_conversion_prompt(query, context)
        print(f"[DEBUG] Generated prompt: {prompt}")
        
        try:
            print(f"[DEBUG] Calling LLM with prompt...")
            response = self.llm_service.llm(
                prompt,
                max_tokens=150,  # Reduced to encourage concise responses
                temperature=0.1,  # Lower temperature for more deterministic output
                stop=["Query:", "\nQuery:", "Q:", "\nQ:", "\n\n"],  # Better stop conditions
                echo=False,
                top_p=0.95,  # Add nucleus sampling for better quality
                repeat_penalty=1.1  # Reduce repetition
            )
            
            # Extract the generated text
            response_text = response['choices'][0]['text'].strip()
            print(f"[DEBUG] Full LLM response object: {response}")
            print(f"[DEBUG] Raw LLM response text: {repr(response_text)}")
            print(f"[DEBUG] Response text length: {len(response_text)}")
            logger.info(f"Raw LLM response: {repr(response_text)}")
            
            # Parse LLM response to extract JQL
            lines = response_text.split('\n')
            jql_query = ""
            explanation = ""
            
            # Handle phi-2 specific responses - look for JQL format
            for line in lines:
                line = line.strip()
                logger.info(f"Processing line: {repr(line)}")
                
                # Remove common prefixes that phi-2 might add
                prefixes_to_remove = ['Assistant:', 'JQL:', 'Query:', 'Response:', 'A:']
                for prefix in prefixes_to_remove:
                    if line.startswith(prefix):
                        line = line.replace(prefix, '').strip()
                
                # If this looks like a JQL query, use it
                if line and self._looks_like_jql(line):
                    jql_query = line
                    break
                # Or if it contains JQL keywords but doesn't start with common non-JQL words
                elif (line and 
                      any(keyword in line.lower() for keyword in ['project', 'assignee', 'status', 'priority', 'order by', 'text ~', 'issuetype']) and
                      not line.lower().startswith(('convert', 'natural', 'query', 'the jql', 'jql format', 'here'))):
                    jql_query = line
                    break
            
            # If we still don't have JQL, try the first non-empty meaningful line
            if not jql_query:
                for line in lines:
                    line = line.strip()
                    # Skip common prompt-related text and empty lines
                    skip_patterns = ['Query:', 'Context:', 'Common', 'JQL format', '-', 'Rules:', 'Convert', 'Return', 'Natural', 'Here', 'The']
                    should_skip = any(line.startswith(pattern) for pattern in skip_patterns)
                    
                    if line and not should_skip:
                        # Remove any remaining prefixes
                        for prefix in ['Assistant:', 'JQL:', 'Query:', 'Response:', 'A:']:
                            if line.startswith(prefix):
                                line = line.replace(prefix, '').strip()
                        if line:
                            jql_query = line
                            break
            
            logger.info(f"Extracted JQL: {repr(jql_query)}")
            logger.info(f"Extracted explanation: {repr(explanation)}")
            
            # Validate and clean up the JQL
            if jql_query:
                jql_query = self._validate_and_clean_jql(jql_query)
                if not explanation:
                    explanation = f"Generated JQL query for: {query}"
                return jql_query, explanation
            else:
                raise ValueError("No valid JQL found in LLM response")
                
        except Exception as e:
            logger.error(f"LLM JQL conversion error: {e}")
            raise
    
    def _convert_with_patterns(self, query: str) -> Tuple[str, str]:
        """Convert using pattern matching as fallback"""
        query_lower = query.lower()
        jql_parts = []
        explanation_parts = []
        
        # Add project filter if configured
        if settings.jira_project_key:
            jql_parts.append(f"project = {settings.jira_project_key}")
            explanation_parts.append(f"filtering by project {settings.jira_project_key}")
        
        # Extract status
        status_matches = self._extract_status(query_lower)
        if status_matches:
            if len(status_matches) == 1 and status_matches[0].startswith('status'):
                # This is a special status pattern like "status != 'Done'"
                jql_parts.append(status_matches[0])
                if 'Done' in status_matches[0] and '!=' in status_matches[0]:
                    explanation_parts.append("excluding completed items")
                elif 'IN' in status_matches[0]:
                    explanation_parts.append("with specific status conditions")
                else:
                    explanation_parts.append("with status condition")
            elif len(status_matches) == 1:
                jql_parts.append(f"status = '{status_matches[0]}'")
                explanation_parts.append(f"status is {status_matches[0]}")
            else:
                status_list = "', '".join(status_matches)
                jql_parts.append(f"status IN ('{status_list}')")
                explanation_parts.append(f"status is one of: {', '.join(status_matches)}")
        
        # Extract assignee
        assignee = self._extract_assignee(query_lower)
        if assignee:
            if assignee.startswith('assignee is'):
                # This is a special JQL clause like "assignee is EMPTY"
                jql_parts.append(assignee)
                if 'EMPTY' in assignee:
                    explanation_parts.append("with no assignee")
                else:
                    explanation_parts.append("with specific assignee condition")
            else:
                # This is a regular username
                jql_parts.append(f"assignee = '{assignee}'")
                explanation_parts.append(f"assigned to {assignee}")
        
        # Extract priority
        priority = self._extract_priority(query_lower)
        if priority:
            jql_parts.append(f"priority = '{priority}'")
            explanation_parts.append(f"priority is {priority}")
        
        # Extract issue type
        issue_type = self._extract_issue_type(query_lower)
        if issue_type:
            jql_parts.append(f"issuetype = '{issue_type}'")
            explanation_parts.append(f"issue type is {issue_type}")
        
        # Extract time constraints
        time_jql, time_explanation = self._extract_time_constraints(query_lower)
        if time_jql:
            jql_parts.append(time_jql)
            explanation_parts.append(time_explanation)
        
        # Extract keywords for text search
        keywords = self._extract_keywords(query_lower)
        if keywords:
            keyword_queries = [f"text ~ '{keyword}'" for keyword in keywords]
            jql_parts.append(f"({' OR '.join(keyword_queries)})")
            explanation_parts.append(f"containing keywords: {', '.join(keywords)}")
        
        # Build final JQL
        if jql_parts:
            jql_query = " AND ".join(jql_parts) + " ORDER BY created DESC"
        else:
            jql_query = "ORDER BY created DESC"
            explanation_parts.append("all issues ordered by creation date")
        
        explanation = "Finding issues " + ", ".join(explanation_parts) if explanation_parts else "Finding all issues"
        
        return jql_query, explanation
    
    def _extract_status(self, query: str) -> List[str]:
        """Extract status values from query"""
        statuses = []
        
        # First check for special status patterns
        for pattern, jql_clause in self.status_patterns.items():
            if pattern in query:
                return [jql_clause]  # Return the full JQL clause
        
        # Then check for regular status mappings
        for pattern, status in self.status_mappings.items():
            if pattern in query:
                if status not in statuses:
                    statuses.append(status)
        return statuses
    
    def _extract_assignee(self, query: str) -> Optional[str]:
        """Extract assignee from query"""
        # First check for special assignee patterns (unassigned, etc.)
        for pattern, jql_clause in self.assignee_patterns.items():
            if pattern in query:
                return jql_clause  # Return the full JQL clause like "assignee is EMPTY"
        
        # Look for patterns like "assigned to john", "john's tasks", "by user1"
        user_patterns = [
            r'assigned to (\w+)',
            r'(\w+)\'s tasks?',
            r'by (\w+)',
            r'for (\w+)',
            r'user (\w+)'
        ]
        
        for pattern in user_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)  # Return just the username
        
        return None
    
    def _extract_priority(self, query: str) -> Optional[str]:
        """Extract priority from query"""
        for pattern, priority in self.priority_mappings.items():
            if pattern in query:
                return priority
        return None
    
    def _extract_issue_type(self, query: str) -> Optional[str]:
        """Extract issue type from query"""
        for pattern, issue_type in self.issue_type_mappings.items():
            if pattern in query:
                return issue_type
        return None
    
    def _extract_time_constraints(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract time constraints from query"""
        for pattern, jql_time in self.time_patterns.items():
            match = re.search(pattern, query)
            if match:
                if '\\1' in jql_time:  # Handle capture groups
                    jql_time = jql_time.replace('\\1', match.group(1))
                
                if 'created' in query or 'made' in query or 'added' in query:
                    return f"created >= {jql_time}", f"created since {match.group(0)}"
                elif 'updated' in query or 'modified' in query:
                    return f"updated >= {jql_time}", f"updated since {match.group(0)}"
                else:
                    return f"created >= {jql_time}", f"created since {match.group(0)}"
        
        return None, None
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords for text search"""
        # Remove common query words and extract meaningful terms
        stop_words = {
            'show', 'me', 'all', 'the', 'find', 'get', 'list', 'tasks', 'issues',
            'assigned', 'to', 'with', 'for', 'by', 'in', 'on', 'at', 'is', 'are',
            'that', 'which', 'where', 'when', 'how', 'what', 'who', 'and', 'or',
            'but', 'created', 'updated', 'status', 'priority', 'high', 'low', 'medium',
            'items'  # Generic word that doesn't need text search
        }
        
        # Words that are handled by special patterns (assignee, status, etc.)
        handled_pattern_words = set()
        
        # Add assignee pattern words
        for pattern in self.assignee_patterns.keys():
            handled_pattern_words.update(pattern.split())
        
        # Add status pattern words
        for pattern in self.status_patterns.keys():
            handled_pattern_words.update(pattern.split())
            
        # Add all status mapping keys
        handled_pattern_words.update(self.status_mappings.keys())
        
        # Add all priority mapping keys
        handled_pattern_words.update(self.priority_mappings.keys())
        
        # Add all issue type mapping keys
        handled_pattern_words.update(self.issue_type_mappings.keys())
        
        # Add common user assignment words
        handled_pattern_words.update(['assigned', 'assignee', 'bugs', 'bug', 'tasks', 'task', 'story', 'stories'])
        
        # Add time-related words that are handled by time patterns
        handled_pattern_words.update(['today', 'yesterday', 'week', 'this', 'last', 'month', 'day', 'days', 'weeks', 'months', 'ago'])
        
        # Look for user names mentioned in the query and add them to handled words
        user_patterns = [
            r'assigned to (\w+)',
            r'(\w+)\'s tasks?',
            r'by (\w+)',
            r'for (\w+)',
            r'user (\w+)'
        ]
        for pattern in user_patterns:
            matches = re.findall(pattern, query.lower())
            for match in matches:
                handled_pattern_words.add(match)
        
        # Extract quoted strings first
        quoted_matches = re.findall(r'"([^"]+)"', query)
        keywords = quoted_matches.copy()
        
        # Remove quoted strings from query for further processing
        query_without_quotes = re.sub(r'"[^"]+"', '', query)
        
        # Extract remaining meaningful words
        words = re.findall(r'\b\w+\b', query_without_quotes.lower())
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Filter out words that are already captured in other fields
        filtered_words = []
        for word in meaningful_words:
            if (word not in self.status_mappings and 
                word not in self.priority_mappings and 
                word not in self.issue_type_mappings and
                word not in handled_pattern_words):
                filtered_words.append(word)
        
        keywords.extend(filtered_words[:3])  # Limit to 3 keywords
        return list(set(keywords))  # Remove duplicates
    
    def _validate_and_clean_jql(self, jql: str) -> str:
        """Enhanced JQL validation and cleanup for phi-2 responses"""
        # Remove extra whitespace
        jql = re.sub(r'\s+', ' ', jql.strip())
        
        # Basic syntax validation
        if not jql:
            return "ORDER BY created DESC"
        
        # Handle incomplete assignee clauses (common phi-2 issue)
        # Pattern: "assignee = ORDER BY" -> need to fix missing value
        if re.search(r'assignee\s*=\s*ORDER\s+BY', jql, re.IGNORECASE):
            # This is incomplete - try to extract the original query intent
            logger.warning(f"Detected incomplete assignee clause in JQL: {jql}")
            # For now, fall back to a basic search
            return "ORDER BY created DESC"
        
        # Handle incomplete status clauses
        if re.search(r'status\s*=\s*ORDER\s+BY', jql, re.IGNORECASE):
            logger.warning(f"Detected incomplete status clause in JQL: {jql}")
            return "ORDER BY created DESC"
        
        # Handle incomplete priority clauses  
        if re.search(r'priority\s*=\s*ORDER\s+BY', jql, re.IGNORECASE):
            logger.warning(f"Detected incomplete priority clause in JQL: {jql}")
            return "ORDER BY created DESC"
        
        # Fix incorrect empty assignee patterns: assignee = "" -> assignee is EMPTY
        jql = re.sub(r'assignee\s*=\s*""', 'assignee is EMPTY', jql, flags=re.IGNORECASE)
        jql = re.sub(r'assignee\s*=\s*\'\'', 'assignee is EMPTY', jql, flags=re.IGNORECASE)
        
        # Ensure proper quoting for text values
        # Fix patterns like: assignee = john -> assignee = "john"
        jql = re.sub(r'assignee\s*=\s*(\w+)(?!\s*")', r'assignee = "\1"', jql)
        jql = re.sub(r'status\s*=\s*([^"\s]+)(?!\s*")', r'status = "\1"', jql)
        jql = re.sub(r'priority\s*=\s*([^"\s]+)(?!\s*")', r'priority = "\1"', jql)
        
        # Ensure ORDER BY is at the end
        if 'ORDER BY' not in jql.upper():
            jql += " ORDER BY created DESC"
        
        return jql
    
    def _build_jql_conversion_prompt(self, query: str, context: Optional[str]) -> str:
        """Build prompt for LLM JQL conversion"""
        
        # Enhanced prompt with more examples and clearer patterns for phi-2
        return f"""Convert natural language to JQL format. Always include quoted values for names and exact field matches.

Query: show me bugs assigned to john
JQL: assignee = "john" AND issuetype = Bug ORDER BY created DESC

Query: all open tasks
JQL: status = "Open" ORDER BY created DESC

Query: high priority items
JQL: priority = "High" ORDER BY created DESC

Query: tasks assigned to sarah
JQL: assignee = "sarah" ORDER BY created DESC

Query: bugs with high priority
JQL: issuetype = Bug AND priority = "High" ORDER BY created DESC

Query: unassigned bugs
JQL: assignee is EMPTY AND issuetype = Bug ORDER BY created DESC

Query: {query}
JQL:"""
    
    def _looks_like_jql(self, text: str) -> bool:
        """Check if text looks like a valid JQL query"""
        jql_keywords = [
            'project', 'assignee', 'status', 'priority', 'issuetype', 'type',
            'created', 'updated', 'resolved', 'text', 'summary', 'description',
            'AND', 'OR', 'NOT', 'ORDER BY', 'EMPTY', '='
        ]
        text_upper = text.upper()
        return any(keyword.upper() in text_upper for keyword in jql_keywords)
    
    def get_query_suggestions(self, current_query: str) -> List[str]:
        """Generate suggestions for follow-up queries"""
        suggestions = []
        query_lower = current_query.lower()
        
        # Suggest status refinements
        if 'status' not in query_lower:
            suggestions.extend([
                "Add status filter (e.g., 'in progress only')",
                "Show only completed tasks",
                "Include pending items"
            ])
        
        # Suggest assignee refinements  
        if 'assigned' not in query_lower and 'by' not in query_lower:
            suggestions.extend([
                "Filter by assignee",
                "Show unassigned items",
                "Group by team member"
            ])
        
        # Suggest time refinements
        if not any(time_word in query_lower for time_word in ['today', 'week', 'month', 'day']):
            suggestions.extend([
                "Add time filter (e.g., 'this week')",
                "Show recent items only",
                "Include last month's items"
            ])
        
        # Suggest priority refinements
        if 'priority' not in query_lower and not any(p in query_lower for p in ['high', 'low', 'urgent', 'critical']):
            suggestions.extend([
                "Filter by priority",
                "Show high priority items",
                "Include urgent tasks only"
            ])
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _create_basic_fallback_jql(self, query: str) -> Tuple[str, str]:
        """Create a basic JQL query as fallback when LLM is not available"""
        jql_parts = []
        explanation_parts = []
        
        # Add project filter if configured
        if settings.jira_project_key:
            jql_parts.append(f"project = {settings.jira_project_key}")
            explanation_parts.append(f"filtering by project {settings.jira_project_key}")
        
        # Simple text search for the entire query
        jql_parts.append(f"text ~ '{query}'")
        explanation_parts.append(f"containing text: {query}")
        
        # Build final JQL
        jql_query = " AND ".join(jql_parts) + " ORDER BY created DESC"
        explanation = "Finding issues " + ", ".join(explanation_parts)
        
        return jql_query, explanation

# Global instance
jql_converter = JQLConverter()
