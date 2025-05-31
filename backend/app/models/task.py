from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    """Base model for Jira tasks"""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    assignee: Optional[str] = Field(None, description="Email of the assignee")

class TaskCreate(TaskBase):
    """Model for creating a new task"""
    pass

class TaskResponse(TaskBase):
    """Model for task responses"""
    id: str = Field(..., description="Jira task ID")
    status: str = Field(..., description="Current status of the task")
    created_date: Optional[datetime] = Field(None, description="Task creation date")
    resolved_date: Optional[datetime] = Field(None, description="Task resolution date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "JIRA-123",
                "title": "Implement login page",
                "description": "Create a responsive login page with email and password fields",
                "status": "In Progress",
                "assignee": "user@example.com",
                "created_date": "2024-01-15T10:30:00Z",
                "resolved_date": None
            }
        }