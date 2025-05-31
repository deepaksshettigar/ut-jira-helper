from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from app.models.conversation import (
    ConversationQuery, 
    ConversationResponse, 
    ConversationHistory,
    TaskAnalysis
)
from app.models.task import TaskResponse
from app.services.jira_service import jira_service
from app.services.llm_service import llm_service, QueryAnalysis, FilterCriteria
import re
from datetime import datetime
import uuid

# Create router
router = APIRouter(tags=["conversational-ai"])

# Mock conversation history storage
conversation_history: List[ConversationHistory] = []

class ConversationalAI:
    """Enhanced conversational AI processor with LLM integration"""
    
    def __init__(self):
        self.jira_service = jira_service
        self.llm_service = llm_service
    
    def process_query(self, query: str, context: Optional[str] = None) -> ConversationResponse:
        """Process a natural language query using LLM or fallback to pattern matching"""
        
        # First, analyze the query to understand intent and extract filtering criteria
        query_analysis = self.llm_service.analyze_query(query, context or "")
        
        # Get filtered task data based on analysis
        try:
            if query_analysis.filter_criteria and self._has_meaningful_criteria(query_analysis.filter_criteria):
                tasks_data = self.jira_service.get_tasks(filter_criteria=query_analysis.filter_criteria)
            else:
                tasks_data = self.jira_service.get_tasks()
        except Exception:
            tasks_data = []
        
        # Generate response based on the intent and data
        response = self._generate_intelligent_response(query, query_analysis, tasks_data, context)
        
        return response
    
    def _has_meaningful_criteria(self, criteria: FilterCriteria) -> bool:
        """Check if filter criteria contains meaningful filtering information"""
        return any([
            criteria.status,
            criteria.assignee,
            criteria.keywords,
            criteria.time_frame,
            criteria.priority
        ])
    
    def _generate_intelligent_response(self, query: str, analysis: QueryAnalysis, tasks_data: List[dict], context: Optional[str]) -> ConversationResponse:
        """Generate response based on query analysis and filtered data"""
        
        # Handle different intents
        if analysis.intent == "create":
            return self._handle_task_creation(query, tasks_data)
        elif analysis.intent == "summarize":
            return self._handle_summary_with_analysis(query, analysis, tasks_data)
        elif analysis.intent == "compare":
            return self._handle_comparison_query(query, analysis, tasks_data)
        elif analysis.intent == "analyze":
            return self._handle_analysis_query(query, analysis, tasks_data)
        else:  # filter intent
            return self._handle_filter_query(query, analysis, tasks_data)
    
    def _handle_summary_with_analysis(self, query: str, analysis: QueryAnalysis, tasks_data: List[dict]) -> ConversationResponse:
        """Handle summary queries with enhanced analysis"""
        task_analysis = self.analyze_tasks(tasks_data)
        
        # Build response based on filtering criteria
        response_parts = [f"📊 Summary of {len(tasks_data)} filtered tasks:"]
        
        if analysis.filter_criteria.status:
            response_parts.append(f"📌 Status filter: {', '.join(analysis.filter_criteria.status)}")
        
        if analysis.filter_criteria.assignee:
            response_parts.append(f"👤 Assignee filter: {', '.join(analysis.filter_criteria.assignee)}")
        
        if analysis.filter_criteria.keywords:
            response_parts.append(f"🔍 Keywords: {', '.join(analysis.filter_criteria.keywords)}")
        
        response_parts.append("")  # Empty line
        
        for status, count in task_analysis.status_breakdown.items():
            emoji = "✅" if status == "Done" else "🔄" if status == "In Progress" else "📋"
            response_parts.append(f"{emoji} {status}: {count}")
        
        response_parts.append(f"\n🎯 Completion Rate: {task_analysis.completion_percentage:.1f}%")
        
        if task_analysis.insights:
            response_parts.append("\n💡 Insights:")
            for insight in task_analysis.insights:
                response_parts.append(f"• {insight}")
        
        # Add visualization recommendation
        if analysis.visualization_type:
            response_parts.append(f"\n📈 Recommended chart: {analysis.visualization_type.title()} chart")
        
        suggested_actions = ["View detailed breakdown", "Change filters", "Export data"]
        if analysis.visualization_type:
            suggested_actions.insert(0, f"Show {analysis.visualization_type} chart")
        
        return ConversationResponse(
            response="\n".join(response_parts),
            query=query,
            task_count=len(tasks_data),
            suggested_actions=suggested_actions,
            chart_recommendation=analysis.visualization_type
        )
    
    def _handle_filter_query(self, query: str, analysis: QueryAnalysis, tasks_data: List[dict]) -> ConversationResponse:
        """Handle filtering queries with intelligent responses"""
        
        if not tasks_data:
            filter_desc = self._describe_filters(analysis.filter_criteria)
            return ConversationResponse(
                response=f"No tasks found matching your criteria{filter_desc}.",
                query=query,
                task_count=0,
                suggested_actions=["Adjust filters", "View all tasks", "Try different search"]
            )
        
        # Build response describing what was found
        response_parts = []
        filter_desc = self._describe_filters(analysis.filter_criteria)
        
        if filter_desc:
            response_parts.append(f"Found {len(tasks_data)} tasks{filter_desc}:")
        else:
            response_parts.append(f"Found {len(tasks_data)} tasks:")
        
        response_parts.append("")  # Empty line
        
        # Show tasks grouped by status if multiple statuses
        status_groups = {}
        for task in tasks_data:
            status = task.get('status', 'Unknown')
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(task)
        
        for status, tasks in status_groups.items():
            emoji = "✅" if status == "Done" else "🔄" if status == "In Progress" else "📋"
            response_parts.append(f"{emoji} **{status}** ({len(tasks)} tasks):")
            for task in tasks[:3]:  # Show first 3 tasks per status
                response_parts.append(f"  • {task['id']}: {task['title']}")
            if len(tasks) > 3:
                response_parts.append(f"  ... and {len(tasks) - 3} more")
            response_parts.append("")
        
        # Add chart recommendation
        if analysis.visualization_type:
            response_parts.append(f"📈 Suggested visualization: {analysis.visualization_type.title()} chart")
        
        suggested_actions = ["View task details", "Refine filters", "Change grouping"]
        if analysis.visualization_type:
            suggested_actions.insert(0, f"Show {analysis.visualization_type} chart")
        
        return ConversationResponse(
            response="\n".join(response_parts),
            query=query,
            task_count=len(tasks_data),
            suggested_actions=suggested_actions,
            chart_recommendation=analysis.visualization_type
        )
    
    def _handle_comparison_query(self, query: str, analysis: QueryAnalysis, tasks_data: List[dict]) -> ConversationResponse:
        """Handle comparison queries"""
        # For comparison, we typically want to compare different groups
        response_parts = [f"📊 Comparison based on {len(tasks_data)} tasks:"]
        
        # Compare by status
        status_breakdown = {}
        assignee_breakdown = {}
        
        for task in tasks_data:
            status = task.get('status', 'Unknown')
            assignee = task.get('assignee', 'Unassigned')
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
            assignee_breakdown[assignee] = assignee_breakdown.get(assignee, 0) + 1
        
        response_parts.append("\n🏷️ **Status Distribution:**")
        for status, count in sorted(status_breakdown.items()):
            percentage = (count / len(tasks_data)) * 100
            response_parts.append(f"  • {status}: {count} tasks ({percentage:.1f}%)")
        
        response_parts.append("\n👥 **Assignee Distribution:**")
        for assignee, count in sorted(assignee_breakdown.items()):
            percentage = (count / len(tasks_data)) * 100
            response_parts.append(f"  • {assignee}: {count} tasks ({percentage:.1f}%)")
        
        return ConversationResponse(
            response="\n".join(response_parts),
            query=query,
            task_count=len(tasks_data),
            suggested_actions=["Show bar chart", "View details", "Export comparison"],
            chart_recommendation="bar"
        )
    
    def _handle_analysis_query(self, query: str, analysis: QueryAnalysis, tasks_data: List[dict]) -> ConversationResponse:
        """Handle analysis queries with insights"""
        task_analysis = self.analyze_tasks(tasks_data)
        
        response_parts = [f"🔍 Analysis of {len(tasks_data)} tasks:"]
        
        # Add workload analysis
        assignee_workload = {}
        for task in tasks_data:
            assignee = task.get('assignee', 'Unassigned')
            assignee_workload[assignee] = assignee_workload.get(assignee, 0) + 1
        
        if len(assignee_workload) > 1:
            response_parts.append("\n⚖️ **Workload Balance:**")
            avg_workload = len(tasks_data) / len(assignee_workload)
            for assignee, count in sorted(assignee_workload.items()):
                if count > avg_workload * 1.5:
                    response_parts.append(f"  • {assignee}: {count} tasks ⚠️ (Above average)")
                elif count < avg_workload * 0.5:
                    response_parts.append(f"  • {assignee}: {count} tasks 📉 (Below average)")
                else:
                    response_parts.append(f"  • {assignee}: {count} tasks ✅ (Balanced)")
        
        response_parts.append(f"\n📈 **Progress Metrics:**")
        response_parts.append(f"  • Completion Rate: {task_analysis.completion_percentage:.1f}%")
        
        if task_analysis.insights:
            response_parts.append("\n💡 **Key Insights:**")
            for insight in task_analysis.insights:
                response_parts.append(f"  • {insight}")
        
        return ConversationResponse(
            response="\n".join(response_parts),
            query=query,
            task_count=len(tasks_data),
            suggested_actions=["Show timeline chart", "View trends", "Export analysis"],
            chart_recommendation="timeline"
        )
    
    def _describe_filters(self, criteria: FilterCriteria) -> str:
        """Create a human-readable description of applied filters"""
        filter_parts = []
        
        if criteria.status:
            if len(criteria.status) == 1:
                filter_parts.append(f"with status '{criteria.status[0]}'")
            else:
                filter_parts.append(f"with status in {criteria.status}")
        
        if criteria.assignee:
            if len(criteria.assignee) == 1:
                filter_parts.append(f"assigned to {criteria.assignee[0]}")
            else:
                filter_parts.append(f"assigned to {', '.join(criteria.assignee)}")
        
        if criteria.keywords:
            filter_parts.append(f"containing '{', '.join(criteria.keywords)}'")
        
        if criteria.time_frame:
            filter_parts.append(f"from {criteria.time_frame}")
        
        if criteria.priority:
            filter_parts.append(f"with {criteria.priority} priority")
        
        if filter_parts:
            return " " + " and ".join(filter_parts)
        
        return ""
    
    def _process_with_llm(self, query: str, context: Optional[str], tasks_data: List[dict]) -> ConversationResponse:
        """Process query using local LLM model - Legacy method for backward compatibility"""
        # Use the new intelligent processing
        query_analysis = self.llm_service.analyze_query(query, context or "")
        return self._generate_intelligent_response(query, query_analysis, tasks_data, context)
    
    def _process_with_patterns(self, query: str, context: Optional[str], tasks_data: List[dict]) -> ConversationResponse:
        """Fallback pattern matching processing - Legacy method for backward compatibility"""
        # Use new analysis but with pattern-based approach
        query_analysis = self.llm_service.analyze_query(query, context or "")
        return self._generate_intelligent_response(query, query_analysis, tasks_data, context)
    
    def _get_suggested_actions(self, query: str, tasks_data: List[dict]) -> List[str]:
        """Generate suggested actions based on query"""
        lower_query = query.lower()
        
        if 'create' in lower_query or 'add' in lower_query:
            return ["Set assignee", "Add description", "Create task via API"]
        elif 'summary' in lower_query or 'overview' in lower_query:
            return ["View detailed breakdown", "Check assignee workload", "Export report"]
        elif 'in progress' in lower_query:
            return ["View task details", "Mark task as done", "Update status"]
        elif 'workload' in lower_query:
            return ["Balance workload", "Reassign tasks", "View individual assignments"]
        else:
            return ["View task details", "Try different query", "Ask for help"]
    
    def _count_relevant_tasks(self, query: str, tasks_data: List[dict]) -> int:
        """Count tasks relevant to the query"""
        lower_query = query.lower()
        
        if 'in progress' in lower_query:
            return len([t for t in tasks_data if 'progress' in t.get('status', '').lower()])
        elif 'to do' in lower_query or 'todo' in lower_query:
            return len([t for t in tasks_data if 'to do' in t.get('status', '').lower()])
        elif 'done' in lower_query or 'completed' in lower_query:
            return len([t for t in tasks_data if 'done' in t.get('status', '').lower()])
        else:
            return len(tasks_data)
    
    def _search_tasks(self, query: str, tasks_data: List[dict]) -> List[dict]:
        """Search tasks based on query"""
        return [task for task in tasks_data if 
                query.lower() in task.get('title', '').lower() or
                query.lower() in task.get('description', '').lower() or
                query.lower() in task.get('id', '').lower() or
                query.lower() in task.get('status', '').lower() or
                query.lower() in task.get('assignee', '').lower()]
    
    def _handle_task_creation(self, query: str, tasks_data: List[dict]) -> ConversationResponse:
        """Handle task creation queries"""
        # Extract potential task title
        patterns = [
            r'create task[:\s]+([^.!?]*)',
            r'add task[:\s]+([^.!?]*)',
            r'new task[:\s]+([^.!?]*)',
            r'create[:\s]+([^.!?]*)'
        ]
        
        task_title = ''
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                task_title = match.group(1).strip()
                break
        
        if task_title:
            response = f"""I can help you create a task with the title: "{task_title}"

To create this task in the system, you would use the POST /tasks endpoint with the following structure:
- Title: {task_title}
- Status: To Do (default)
- Assignee: (to be specified)

Would you like me to help with additional details like assignee or description?"""
            
            return ConversationResponse(
                response=response,
                query=query,
                task_count=0,
                suggested_actions=["Set assignee", "Add description", "Create task via API"]
            )
        else:
            return ConversationResponse(
                response="I can help you create a new task! Please specify the task title, for example: 'Create task: Fix login bug'",
                query=query,
                task_count=0,
                suggested_actions=["Specify task title", "View existing tasks"]
            )
    
    def _handle_status_query(self, status: str, query: str, tasks_data: List[dict]) -> ConversationResponse:
        """Handle queries about tasks with specific status"""
        filtered_tasks = [task for task in tasks_data if task.get('status') == status]
        
        if not filtered_tasks:
            response = f"There are no tasks currently marked as '{status}'."
            return ConversationResponse(
                response=response,
                query=query,
                task_count=0,
                suggested_actions=["View all tasks", "Check other statuses"]
            )
        
        task_list = "\n".join([f"• {task['id']}: {task['title']}" for task in filtered_tasks])
        response = f"Found {len(filtered_tasks)} task{'s' if len(filtered_tasks) != 1 else ''} with status '{status}':\n\n{task_list}"
        
        actions = ["View task details", "Update task status"]
        if status == "To Do":
            actions.append("Start working on task")
        elif status == "In Progress":
            actions.append("Mark task as done")
        
        return ConversationResponse(
            response=response,
            query=query,
            task_count=len(filtered_tasks),
            suggested_actions=actions
        )
    
    def _handle_summary_query(self, query: str, tasks_data: List[dict]) -> ConversationResponse:
        """Handle project summary queries"""
        analysis = self.analyze_tasks(tasks_data)
        
        response = f"""📊 Project Overview:

Total Tasks: {analysis.total_tasks}
"""
        
        for status, count in analysis.status_breakdown.items():
            emoji = "✅" if status == "Done" else "🔄" if status == "In Progress" else "📋"
            response += f"{emoji} {status}: {count}\n"
        
        response += f"\n🎯 Completion Rate: {analysis.completion_percentage:.1f}%"
        
        if analysis.insights:
            response += f"\n\n💡 Insights:\n" + "\n".join([f"• {insight}" for insight in analysis.insights])
        
        return ConversationResponse(
            response=response,
            query=query,
            task_count=analysis.total_tasks,
            suggested_actions=["View detailed breakdown", "Check assignee workload", "Export report"],
            chart_recommendation="pie"
        )
    
    def _handle_assignee_query(self, assignee: str, query: str, tasks_data: List[dict]) -> ConversationResponse:
        """Handle queries about specific assignee's tasks"""
        user_tasks = [task for task in tasks_data if task.get('assignee') == assignee]
        
        if not user_tasks:
            return ConversationResponse(
                response=f"{assignee} doesn't have any tasks assigned currently.",
                query=query,
                task_count=0,
                suggested_actions=["Assign new task", "View all assignees"]
            )
        
        status_counts = {}
        for task in user_tasks:
            status = task.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        response = f"{assignee} has {len(user_tasks)} task{'s' if len(user_tasks) != 1 else ''} assigned:\n\n"
        for status, count in status_counts.items():
            response += f"• {count} {status}\n"
        
        return ConversationResponse(
            response=response,
            query=query,
            task_count=len(user_tasks),
            suggested_actions=["View task details", "Reassign tasks", "Check workload balance"]
        )
    
    def _handle_workload_query(self, query: str, tasks_data: List[dict]) -> ConversationResponse:
        """Handle workload distribution queries"""
        assignee_counts = {}
        for task in tasks_data:
            assignee = task.get('assignee', 'Unassigned')
            assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
        
        if not assignee_counts:
            return ConversationResponse(
                response="No tasks are currently assigned.",
                query=query,
                task_count=0,
                suggested_actions=["Assign tasks", "Create new tasks"]
            )
        
        response = "📊 Current workload distribution:\n\n"
        for assignee, count in sorted(assignee_counts.items()):
            response += f"• {assignee}: {count} task{'s' if count != 1 else ''}\n"
        
        return ConversationResponse(
            response=response,
            query=query,
            task_count=len(tasks_data),
            suggested_actions=["Balance workload", "Reassign tasks", "View individual assignments"]
        )
    
    def _handle_help_query(self, query: str, tasks_data: List[dict]) -> ConversationResponse:
        """Handle help requests"""
        model_status = "✅ Local LLM Active" if self.llm_service.is_available() else "⚠️ Using Pattern Matching"
        jira_status = "✅ Jira API Connected" if self.jira_service.is_configured() else "⚠️ Using Mock Data"
        
        response = f"""🤖 AI Assistant Help

{model_status} | {jira_status}

I can help you with:

📋 **Task Information:**
• "What's in progress?" - Current work status
• "What needs to be done?" - Pending tasks
• "Show completed tasks" - Finished work
• "Give me a summary" - Project overview

👥 **Team Insights:**
• "What's [user] working on?" - Individual workload
• "Show workload distribution" - Team balance

🔍 **Search & Analysis:**
• Search by task ID, title, or keywords
• "How many tasks are done?" - Status counts
• "Who is assigned to [task]?" - Assignment info

💬 **Task Management:**
• "Create task: [description]" - Task creation guidance
• Natural language queries about your project

{("This AI assistant uses a local LLM model for enhanced responses." if self.llm_service.is_available() else "Enhanced with local LLM support when configured.")}"""
        
        return ConversationResponse(
            response=response,
            query=query,
            task_count=len(tasks_data),
            suggested_actions=["Try a sample query", "View task summary", "Create new task"]
        )
    
    def _handle_search_results(self, query: str, results: List[dict]) -> ConversationResponse:
        """Handle search result responses"""
        if len(results) == 1:
            task = results[0]
            response = f"""Found 1 task matching "{query}":

{task['id']}: {task['title']}
Status: {task['status']}
Assignee: {task.get('assignee', 'Unassigned')}
Description: {task.get('description', 'No description available')}"""
        else:
            task_list = "\n".join([f"• {task['id']}: {task['title']} ({task['status']})" 
                                  for task in results[:5]])
            remaining = f"\n...and {len(results) - 5} more" if len(results) > 5 else ""
            response = f"Found {len(results)} tasks matching \"{query}\":\n\n{task_list}{remaining}"
        
        return ConversationResponse(
            response=response,
            query=query,
            task_count=len(results),
            suggested_actions=["View task details", "Refine search", "Filter results"]
        )
    
    def _handle_default_query(self, query: str, tasks_data: List[dict]) -> ConversationResponse:
        """Handle queries that don't match specific patterns"""
        return ConversationResponse(
            response=f"I'm not sure how to help with \"{query}\" specifically. Try asking about task status, assignments, or project summaries. Type 'help' to see what I can do!",
            query=query,
            task_count=0,
            suggested_actions=["Ask for help", "Try different query", "View all tasks"]
        )
    
    def analyze_tasks(self, tasks_data: List[dict]) -> TaskAnalysis:
        """Analyze current tasks and provide insights"""
        total_tasks = len(tasks_data)
        
        # Status breakdown
        status_breakdown = {}
        for task in tasks_data:
            status = task.get('status', 'Unknown')
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
        
        # Assignee breakdown
        assignee_breakdown = {}
        for task in tasks_data:
            assignee = task.get('assignee', 'Unassigned')
            assignee_breakdown[assignee] = assignee_breakdown.get(assignee, 0) + 1
        
        # Completion percentage
        completed_tasks = status_breakdown.get('Done', 0)
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Generate insights
        insights = []
        if completion_percentage < 30:
            insights.append("Project is in early stages with most tasks still pending")
        elif completion_percentage > 70:
            insights.append("Project is nearing completion with most tasks done")
        
        if len(assignee_breakdown) == 1:
            insights.append("All tasks are assigned to a single person")
        elif 'Unassigned' in assignee_breakdown:
            insights.append(f"{assignee_breakdown['Unassigned']} tasks need to be assigned")
        
        in_progress = status_breakdown.get('In Progress', 0)
        if in_progress > total_tasks * 0.5:
            insights.append("High number of tasks in progress - consider focusing efforts")
        
        return TaskAnalysis(
            total_tasks=total_tasks,
            status_breakdown=status_breakdown,
            assignee_breakdown=assignee_breakdown,
            completion_percentage=completion_percentage,
            insights=insights
        )

@router.post("/ai/query", response_model=ConversationResponse)
async def process_conversation_query(query_data: ConversationQuery):
    """
    Process a natural language query about tasks using AI.
    This endpoint provides conversational AI capabilities for task management.
    Enhanced with local LLM support when configured.
    """
    try:
        ai = ConversationalAI()
        response = ai.process_query(query_data.query, query_data.context)
        
        # Store in conversation history
        conversation_id = str(uuid.uuid4())
        history_entry = ConversationHistory(
            id=conversation_id,
            query=query_data.query,
            response=response.response,
            timestamp=datetime.now()
        )
        conversation_history.append(history_entry)
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing conversational query: {str(e)}"
        )

@router.get("/ai/analyze", response_model=TaskAnalysis)
async def analyze_project_tasks():
    """
    Get AI-powered analysis of current project tasks.
    Provides insights, statistics, and recommendations.
    """
    try:
        ai = ConversationalAI()
        # Get current tasks
        tasks_data = jira_service.get_tasks()
        analysis = ai.analyze_tasks(tasks_data)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing tasks: {str(e)}"
        )

@router.get("/ai/history", response_model=List[ConversationHistory])
async def get_conversation_history(limit: int = 20):
    """
    Get recent conversation history with the AI assistant.
    """
    # Return most recent conversations, limited by the specified amount
    return sorted(conversation_history, key=lambda x: x.timestamp, reverse=True)[:limit]

@router.delete("/ai/history")
async def clear_conversation_history():
    """
    Clear all conversation history.
    """
    global conversation_history
    conversation_history.clear()
    return {"message": "Conversation history cleared successfully"}

@router.get("/ai/status")
async def get_ai_status():
    """
    Get the current status of AI services (LLM and Jira integration).
    """
    return {
        "llm_available": llm_service.is_available(),
        "llm_model_path": settings.llm_model_path,
        "jira_configured": jira_service.is_configured(),
        "jira_server": settings.jira_server,
        "status": "ready"
    }