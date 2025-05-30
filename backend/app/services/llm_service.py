from llama_cpp import Llama
from typing import Optional, Dict, List
from app.config import settings
import logging
import os

logger = logging.getLogger(__name__)

class LLMService:
    """Service for running local LLM models using GGUF files"""
    
    def __init__(self):
        self.llm = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the LLM model from GGUF file"""
        try:
            if not settings.llm_model_path or not os.path.exists(settings.llm_model_path):
                logger.warning(f"LLM model not found at {settings.llm_model_path}. Using fallback responses.")
                return
            
            logger.info(f"Loading LLM model from {settings.llm_model_path}")
            
            self.llm = Llama(
                model_path=settings.llm_model_path,
                n_ctx=settings.llm_context_size,
                verbose=False,
                n_threads=4  # Adjust based on your system
            )
            
            logger.info("LLM model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load LLM model: {e}")
            self.llm = None
    
    def is_available(self) -> bool:
        """Check if LLM is available"""
        return self.llm is not None
    
    def generate_response(self, prompt: str, context: str = "", tasks_data: List[Dict] = None) -> str:
        """Generate response using the local LLM model"""
        if not self.is_available():
            return self._generate_fallback_response(prompt, tasks_data or [])
        
        try:
            # Build the full prompt with context
            full_prompt = self._build_prompt(prompt, context, tasks_data or [])
            
            # Generate response
            response = self.llm(
                full_prompt,
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                stop=["Human:", "User:", "\n\n"],
                echo=False
            )
            
            # Extract the generated text
            generated_text = response['choices'][0]['text'].strip()
            
            # Clean up the response
            return self._clean_response(generated_text)
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._generate_fallback_response(prompt, tasks_data or [])
    
    def _build_prompt(self, query: str, context: str, tasks_data: List[Dict]) -> str:
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
    
    def _generate_fallback_response(self, prompt: str, tasks_data: List[Dict]) -> str:
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