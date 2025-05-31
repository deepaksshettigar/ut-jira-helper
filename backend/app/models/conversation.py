from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ConversationQuery(BaseModel):
    """Model for conversational AI queries"""
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query about tasks")
    context: Optional[str] = Field(None, description="Additional context for the query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What tasks are in progress?",
                "context": "Current sprint planning"
            }
        }

class ConversationResponse(BaseModel):
    """Model for conversational AI responses"""
    response: str = Field(..., description="AI-generated response to the query")
    query: str = Field(..., description="Original query that was processed")
    task_count: Optional[int] = Field(None, description="Number of tasks referenced in response")
    suggested_actions: Optional[List[str]] = Field(default_factory=list, description="Suggested follow-up actions")
    chart_recommendation: Optional[str] = Field(None, description="Recommended chart type for visualization")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Currently, there are 2 tasks in progress: JIRA-1 (Implement login page) and JIRA-4 (Update API documentation).",
                "query": "What tasks are in progress?",
                "task_count": 2,
                "suggested_actions": ["View task details", "Check assignees", "Get summary"],
                "chart_recommendation": "pie"
            }
        }

class ConversationHistory(BaseModel):
    """Model for conversation history"""
    id: str = Field(..., description="Unique conversation ID")
    query: str = Field(..., description="User query")
    response: str = Field(..., description="AI response")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the conversation occurred")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "conv_123",
                "query": "Show me task summary", 
                "response": "Here's your project overview: Total Tasks: 5, To Do: 2, In Progress: 2, Done: 1",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }

class TaskAnalysis(BaseModel):
    """Model for AI task analysis results"""
    total_tasks: int = Field(..., description="Total number of tasks")
    status_breakdown: dict = Field(..., description="Tasks grouped by status")
    assignee_breakdown: dict = Field(..., description="Tasks grouped by assignee")
    completion_percentage: float = Field(..., description="Percentage of completed tasks")
    insights: List[str] = Field(default_factory=list, description="AI-generated insights about the project")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_tasks": 5,
                "status_breakdown": {"To Do": 2, "In Progress": 2, "Done": 1},
                "assignee_breakdown": {"user1@example.com": 3, "user2@example.com": 2},
                "completion_percentage": 20.0,
                "insights": ["Most tasks are still pending", "Workload is evenly distributed"]
            }
        }