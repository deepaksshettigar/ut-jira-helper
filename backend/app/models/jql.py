from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class JQLQuery(BaseModel):
    """Model for JQL query requests"""
    natural_language: str = Field(..., min_length=1, max_length=1000, description="Natural language query to convert to JQL")
    context: Optional[str] = Field(None, description="Additional context for query conversion")
    max_results: Optional[int] = Field(50, ge=1, le=1000, description="Maximum number of results to return")
    start_at: Optional[int] = Field(0, ge=0, description="Starting index for pagination")
    
    class Config:
        json_schema_extra = {
            "example": {
                "natural_language": "Show me all high priority bugs assigned to John that were created this week",
                "context": "Project management context",
                "max_results": 50,
                "start_at": 0
            }
        }

class JQLResponse(BaseModel):
    """Model for JQL query responses"""
    jql_query: str = Field(..., description="Generated JQL query")
    natural_language: str = Field(..., description="Original natural language query")
    issues: List[Dict[str, Any]] = Field(..., description="List of matching Jira issues")
    total_count: int = Field(..., description="Total number of matching issues")
    start_at: int = Field(..., description="Starting index of returned results")
    max_results: int = Field(..., description="Maximum results requested")
    explanation: str = Field(..., description="Explanation of the JQL query")
    suggestions: Optional[List[str]] = Field(default_factory=list, description="Suggested follow-up queries")
    
    class Config:
        json_schema_extra = {
            "example": {
                "jql_query": "project = ABC AND priority = High AND assignee = 'john.doe' AND created >= -1w",
                "natural_language": "Show me all high priority bugs assigned to John that were created this week",
                "issues": [
                    {
                        "id": "ABC-123",
                        "title": "Critical login bug",
                        "status": "In Progress",
                        "assignee": "john.doe",
                        "priority": "High",
                        "created": "2024-06-01T10:00:00Z"
                    }
                ],
                "total_count": 5,
                "start_at": 0,
                "max_results": 50,
                "explanation": "This query finds high priority issues assigned to John that were created in the last week",
                "suggestions": ["Show only bugs", "Include medium priority", "Show completed tasks"]
            }
        }

class DirectJQLQuery(BaseModel):
    """Model for direct JQL query execution"""
    jql: str = Field(..., min_length=1, max_length=2000, description="Direct JQL query to execute")
    max_results: Optional[int] = Field(50, ge=1, le=1000, description="Maximum number of results to return")
    start_at: Optional[int] = Field(0, ge=0, description="Starting index for pagination")
    
    class Config:
        json_schema_extra = {
            "example": {
                "jql": "project = ABC AND status = 'In Progress' ORDER BY created DESC",
                "max_results": 50,
                "start_at": 0
            }
        }

class JQLValidationResponse(BaseModel):
    """Model for JQL validation responses"""
    is_valid: bool = Field(..., description="Whether the JQL query is valid")
    jql: str = Field(..., description="The JQL query that was validated")
    error_message: Optional[str] = Field(None, description="Error message if JQL is invalid")
    suggestions: Optional[List[str]] = Field(default_factory=list, description="Suggestions for fixing invalid JQL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "jql": "project = ABC AND status = 'In Progress'",
                "error_message": None,
                "suggestions": []
            }
        }
