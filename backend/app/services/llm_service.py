try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    Llama = None

from typing import Optional, Dict, List, Any, NamedTuple
from app.config import settings
import logging
import os
import re
import json
from huggingface_hub import hf_hub_download

logger = logging.getLogger(__name__)

class FilterCriteria(NamedTuple):
    """Structured filtering criteria extracted from user queries"""
    status: Optional[List[str]] = None
    assignee: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    time_frame: Optional[str] = None
    priority: Optional[str] = None
    task_type: Optional[str] = None
    
class QueryAnalysis(NamedTuple):
    """Analysis of user query for data filtering and visualization"""
    intent: str  # 'filter', 'summarize', 'compare', 'create', 'analyze'
    filter_criteria: FilterCriteria
    visualization_type: Optional[str] = None  # 'pie', 'bar', 'timeline', 'table'
    confidence: float = 0.0

class LLMService:
    """Service for running local LLM models using GGUF files"""
    
    def __init__(self):
        self.llm = None
        self._initialize_model()
    
    def _ensure_model(self):
        """Ensure the GGUF model is present locally, download from Hugging Face if needed."""
        model_path = settings.llm_model_path
        model_repo = getattr(settings, "llm_model_repo", None)
        model_filename = getattr(settings, "llm_model_filename", None)
        if not os.path.exists(model_path) and model_repo and model_filename:
            logger.info(f"Downloading LLM model {model_filename} from repo {model_repo} ...")
            downloaded_path = hf_hub_download(
                repo_id=model_repo,
                filename=model_filename,
                local_dir=os.path.dirname(model_path),
                local_dir_use_symlinks=False,
                resume_download=True,
            )
            logger.info(f"Model downloaded to {downloaded_path}")
            # Optionally, move or symlink to model_path if needed

    def _initialize_model(self):
        """Initialize the LLM model from GGUF file"""
        if not LLAMA_AVAILABLE:
            logger.warning("llama-cpp-python not available. Using fallback responses.")
            return
        
        try:
            self._ensure_model()
            resolved_path = os.path.abspath(settings.llm_model_path) if settings.llm_model_path else None
            logger.info(f"[LLMService] LLM_MODEL_PATH from settings: {settings.llm_model_path}")
            logger.info(f"[LLMService] Resolved absolute model path: {resolved_path}")
            if not settings.llm_model_path or not os.path.exists(settings.llm_model_path):
                logger.warning(f"LLM model not found at {settings.llm_model_path} (absolute: {resolved_path}). Using fallback responses.")
                return
            logger.info(f"Loading LLM model from {settings.llm_model_path} (absolute: {resolved_path})")
            self.llm = Llama(
                model_path=settings.llm_model_path,
                n_ctx=settings.llm_context_size,
                verbose=False,
                n_threads=4  # Adjust based on your system
            )
            logger.info("LLM model loaded successfully")
        except Exception as e:
            import traceback
            logger.error(f"Failed to load LLM model: {e}\nTraceback:\n{traceback.format_exc()}")
            self.llm = None
    
    def analyze_query(self, query: str, context: str = "") -> QueryAnalysis:
        """Analyze a user query to extract filtering criteria and intent"""
        if self.is_available():
            return self._analyze_query_with_llm(query, context)
        else:
            return self._analyze_query_with_patterns(query, context)
    
    def _analyze_query_with_llm(self, query: str, context: str) -> QueryAnalysis:
        """Use LLM to analyze query and extract structured filtering criteria"""
        try:
            analysis_prompt = self._build_analysis_prompt(query, context)
            
            response = self.llm(
                analysis_prompt,
                max_tokens=200,
                temperature=0.1,  # Low temperature for consistent structure
                stop=["Human:", "User:", "\n\n"],
                echo=False
            )
            
            analysis_text = response['choices'][0]['text'].strip()
            return self._parse_llm_analysis(analysis_text, query)
            
        except Exception as e:
            logger.error(f"Error in LLM query analysis: {e}")
            return self._analyze_query_with_patterns(query, context)
    
    def _analyze_query_with_patterns(self, query: str, context: str) -> QueryAnalysis:
        """Fallback pattern-based query analysis"""
        lower_query = query.lower()
        
        # Extract intent
        intent = "filter"
        if any(keyword in lower_query for keyword in ['summary', 'overview', 'total', 'count']):
            intent = "summarize"
        elif any(keyword in lower_query for keyword in ['compare', 'vs', 'versus', 'difference']):
            intent = "compare"
        elif any(keyword in lower_query for keyword in ['create', 'add', 'new']):
            intent = "create"
        elif any(keyword in lower_query for keyword in ['analyze', 'insight', 'trend']):
            intent = "analyze"
        
        # Extract filter criteria using patterns
        filter_criteria = self._extract_filter_criteria_patterns(query)
        
        # Suggest visualization based on intent and criteria
        visualization_type = self._suggest_visualization(intent, filter_criteria, query)
        
        return QueryAnalysis(
            intent=intent,
            filter_criteria=filter_criteria,
            visualization_type=visualization_type,
            confidence=0.7  # Pattern matching confidence
        )
    
    def _extract_filter_criteria_patterns(self, query: str) -> FilterCriteria:
        """Extract filtering criteria using regex patterns"""
        lower_query = query.lower()
        
        # Extract status
        status = []
        status_patterns = {
            'To Do': ['to do', 'todo', 'pending', 'not started'],
            'In Progress': ['in progress', 'working', 'active', 'current'],
            'Done': ['done', 'completed', 'finished', 'closed']
        }
        
        for status_name, keywords in status_patterns.items():
            if any(keyword in lower_query for keyword in keywords):
                status.append(status_name)
        
        # Extract assignee (look for user patterns)
        assignee = []
        
        # Look for explicit assignment patterns
        assignee_match = re.search(r'(?:assigned to|for|by)\s+(\w+(?:@\w+\.\w+)?)', lower_query)
        if assignee_match:
            user = assignee_match.group(1)
            if '@' not in user and user.startswith('user'):
                user = f"{user}@example.com"
            assignee.append(user)
        
        # Look for user mentions (user1, user2, etc.)
        user_matches = re.findall(r'\buser(\d+)\b', lower_query)
        for user_num in user_matches:
            assignee.append(f"user{user_num}@example.com")
        
        # Remove duplicates while preserving order
        assignee = list(dict.fromkeys(assignee))
        
        # Extract keywords (task-related terms, but exclude common words)
        keywords = []
        # Look for specific task-related keywords
        keyword_patterns = re.findall(r'\b(?:login|navigation|documentation|api|bug|feature|dashboard|widget|authentication)\b', lower_query)
        keywords.extend(keyword_patterns)
        
        # Extract time frame
        time_frame = None
        time_match = re.search(r'\b(today|this week|last week|this month)\b', lower_query)
        if time_match:
            time_frame = time_match.group(1)
        
        # Extract priority
        priority = None
        priority_match = re.search(r'\b(high|low|urgent|critical|medium)\s*priority\b', lower_query)
        if priority_match:
            priority = priority_match.group(1)
        
        return FilterCriteria(
            status=status if status else None,
            assignee=assignee if assignee else None,
            keywords=keywords if keywords else None,
            time_frame=time_frame,
            priority=priority
        )
    
    def _suggest_visualization(self, intent: str, criteria: FilterCriteria, query: str) -> Optional[str]:
        """Suggest appropriate visualization type based on intent and criteria"""
        lower_query = query.lower()
        
        # Explicit visualization requests
        if any(term in lower_query for term in ['chart', 'graph', 'pie']):
            return 'pie'
        elif any(term in lower_query for term in ['bar', 'column']):
            return 'bar'
        elif any(term in lower_query for term in ['timeline', 'progress', 'over time']):
            return 'timeline'
        elif any(term in lower_query for term in ['table', 'list']):
            return 'table'
        
        # Intent-based suggestions
        if intent == "summarize":
            if criteria.status:
                return 'pie'  # Status distribution
            else:
                return 'bar'  # General summary
        elif intent == "compare":
            return 'bar'  # Comparison chart
        elif intent == "analyze":
            return 'timeline'  # Trend analysis
        else:
            return 'table'  # Default to table for filtering
    
    def _build_analysis_prompt(self, query: str, context: str) -> str:
        """Build prompt for LLM query analysis"""
        return f"""Analyze the following user query about Jira tasks and extract structured information.

User Query: "{query}"
Context: {context if context else "General task management"}

Extract the following information:
1. Intent: filter, summarize, compare, create, or analyze
2. Filter criteria:
   - Status: to do, in progress, done (if mentioned)
   - Assignee: specific users mentioned
   - Keywords: task-related terms
   - Time frame: relative time periods
   - Priority: high, medium, low, urgent, critical
3. Visualization: pie, bar, timeline, table (suggest best type)

Respond in this format:
Intent: [intent]
Status: [comma-separated statuses or none]
Assignee: [comma-separated assignees or none]  
Keywords: [comma-separated keywords or none]
Time_frame: [time frame or none]
Priority: [priority or none]
Visualization: [suggested type]

Analysis:"""
    
    def _parse_llm_analysis(self, analysis_text: str, original_query: str) -> QueryAnalysis:
        """Parse LLM analysis response into structured QueryAnalysis"""
        try:
            lines = analysis_text.split('\n')
            data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip().lower()] = value.strip()
            
            # Parse filter criteria
            filter_criteria = FilterCriteria(
                status=self._parse_list_field(data.get('status')),
                assignee=self._parse_list_field(data.get('assignee')),
                keywords=self._parse_list_field(data.get('keywords')),
                time_frame=data.get('time_frame') if data.get('time_frame', '').lower() != 'none' else None,
                priority=data.get('priority') if data.get('priority', '').lower() != 'none' else None
            )
            
            return QueryAnalysis(
                intent=data.get('intent', 'filter'),
                filter_criteria=filter_criteria,
                visualization_type=data.get('visualization') if data.get('visualization', '').lower() != 'none' else None,
                confidence=0.9  # High confidence for LLM analysis
            )
            
        except Exception as e:
            logger.error(f"Error parsing LLM analysis: {e}")
            # Fallback to pattern analysis
            return self._analyze_query_with_patterns(original_query, "")
    
    def _parse_list_field(self, field_value: str) -> Optional[List[str]]:
        """Parse comma-separated list field from LLM response"""
        if not field_value or field_value.lower() in ['none', 'null', '']:
            return None
        
        items = [item.strip() for item in field_value.split(',')]
        return [item for item in items if item and item.lower() != 'none']
    
    def is_available(self) -> bool:
        """Check if LLM service is available and working"""
        try:
            if not self.llm:
                logger.warning("LLM model not loaded")
                return False
            
            # Test with a simple query using correct parameter names
            test_response = self.generate_response("Test", max_length=10, temperature=0.1)
            return test_response is not None and len(test_response.strip()) > 0
        except Exception as e:
            logger.error(f"LLM availability check failed: {e}")
            return False
    
    def generate_response(self, prompt: str, max_length: int = 200, temperature: float = 0.7) -> str:
        """Generate response using the loaded model"""
        if not self.llm:
            raise RuntimeError("Model not loaded")
        
        try:
            response = self.llm(
                prompt,
                max_tokens=max_length,
                temperature=temperature,
                echo=False,
                stop=["Human:", "Assistant:", "\n\n"]
            )
            
            return response['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def _build_prompt(self, query: str, context: str, tasks_data: List[Dict[str, Any]]) -> str:
        """Build a comprehensive prompt for the LLM"""
        
        # Task data summary
        if tasks_data:
            total_tasks = len(tasks_data)
            status_counts = {}
            assignee_counts = {}
            
            for task in tasks_data:
                status = task.get('status', 'Unknown')
                assignee = task.get('assignee', 'Unassigned')
                status_counts[status] = status_counts.get(status, 0) + 1
                assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
            
            task_summary = f"""
Current Project Status:
- Total Tasks: {total_tasks}
- Status Breakdown: {', '.join([f'{status}: {count}' for status, count in status_counts.items()])}
- Assignee Distribution: {', '.join([f'{assignee}: {count}' for assignee, count in assignee_counts.items()])}

Recent Tasks:
"""
            for task in tasks_data[:5]:  # Show first 5 tasks
                task_summary += f"- {task['id']}: {task['title']} (Status: {task['status']}, Assignee: {task['assignee']})\n"
        else:
            task_summary = "No task data available."
        
        system_prompt = f"""You are an AI assistant helping with Jira project management. You have access to current project data and should provide helpful, accurate responses about tasks, project status, and team workload.

{task_summary}

Instructions:
- Be helpful and informative
- Provide specific data when available
- Keep responses concise but complete
- If asked to create tasks, provide guidance on the process
- Focus on the most relevant information for the user's query

Context: {context if context else 'General project management inquiry'}

User Query: {query}

Response:"""
        
        return system_prompt
    
    def _clean_response(self, response: str) -> str:
        """Clean and format the LLM response"""
        # Remove any unwanted prefixes or suffixes
        response = response.strip()
        
        # Remove common response prefixes
        prefixes_to_remove = ["Assistant:", "AI:", "Response:", "Answer:"]
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        return response
    
    def _generate_fallback_response(self, prompt: str, tasks_data: List[Dict[str, Any]]) -> str:
        """Generate fallback response when LLM is not available"""
        lower_prompt = prompt.lower()
        
        # Basic pattern matching fallback
        if any(keyword in lower_prompt for keyword in ['summary', 'overview']):
            if tasks_data:
                total = len(tasks_data)
                status_counts = {}
                for task in tasks_data:
                    status = task.get('status', 'Unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                return f"Project Summary: {total} total tasks. " + \
                       ", ".join([f"{status}: {count}" for status, count in status_counts.items()])
            else:
                return "No task data available for summary."
        
        elif any(keyword in lower_prompt for keyword in ['in progress', 'working']):
            in_progress = [task for task in tasks_data if 'progress' in task.get('status', '').lower()]
            if in_progress:
                return f"Found {len(in_progress)} tasks in progress: " + \
                       ", ".join([f"{task['id']}: {task['title']}" for task in in_progress[:3]])
            else:
                return "No tasks currently in progress."
        
        elif any(keyword in lower_prompt for keyword in ['create', 'add', 'new']):
            return "To create a new task, use the POST /tasks endpoint with title, description, and assignee fields."
        
        else:
            return f"I understand you're asking about: '{prompt}'. However, the local LLM model is not available. Please check the model configuration or try a more specific query."

# Global instance
llm_service = LLMService()