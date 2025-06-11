from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.models.jql import JQLQuery, JQLResponse, DirectJQLQuery, JQLValidationResponse
from app.services.jql_service import jql_converter
from app.services.jira_service import jira_service
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["jql"])

@router.post("/convert", response_model=JQLResponse)
async def convert_natural_language_to_jql(query: JQLQuery):
    """
    Convert natural language query to JQL and execute it
    """
    try:
        # Convert natural language to JQL
        jql_query, explanation = jql_converter.convert_to_jql(
            query.natural_language, 
            query.context
        )
        
        # Execute the JQL query through Jira service
        if jira_service.is_configured():
            try:
                # Use the JQL query directly with Jira client
                issues = jira_service.jira_client.search_issues(
                    jql_query, 
                    maxResults=query.max_results,
                    startAt=query.start_at,
                    expand='changelog'
                )
                
                # Convert issues to task format
                formatted_issues = []
                for issue in issues:
                    formatted_issues.append(jira_service._convert_issue_to_task(issue))
                
                total_count = issues.total
                
            except Exception as e:
                logger.warning(f"JQL execution failed: {e}, using fallback")
                # Fallback to mock data
                formatted_issues = jira_service.get_tasks()[:query.max_results]
                total_count = len(formatted_issues)
        else:
            # Use mock data
            formatted_issues = jira_service.get_tasks()[:query.max_results]
            total_count = len(formatted_issues)
        
        # Generate suggestions for follow-up queries
        suggestions = jql_converter.get_query_suggestions(query.natural_language)
        
        return JQLResponse(
            jql_query=jql_query,
            natural_language=query.natural_language,
            issues=formatted_issues,
            total_count=total_count,
            start_at=query.start_at,
            max_results=query.max_results,
            explanation=explanation,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"Error converting natural language to JQL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process natural language query: {str(e)}"
        )

@router.post("/execute", response_model=JQLResponse)
async def execute_direct_jql(query: DirectJQLQuery):
    """
    Execute a direct JQL query
    """
    try:
        if jira_service.is_configured():
            try:
                # Execute the JQL query directly
                issues = jira_service.jira_client.search_issues(
                    query.jql,
                    maxResults=query.max_results,
                    startAt=query.start_at,
                    expand='changelog'
                )
                
                # Convert issues to task format
                formatted_issues = []
                for issue in issues:
                    formatted_issues.append(jira_service._convert_issue_to_task(issue))
                
                total_count = issues.total
                
            except Exception as e:
                logger.warning(f"Direct JQL execution failed: {e}, using fallback")
                # Fallback to mock data
                formatted_issues = jira_service.get_tasks()[:query.max_results]
                total_count = len(formatted_issues)
        else:
            # Use mock data
            formatted_issues = jira_service.get_tasks()[:query.max_results]
            total_count = len(formatted_issues)
        
        return JQLResponse(
            jql_query=query.jql,
            natural_language="Direct JQL execution",
            issues=formatted_issues,
            total_count=total_count,
            start_at=query.start_at,
            max_results=query.max_results,
            explanation=f"Executed JQL query: {query.jql}",
            suggestions=[]
        )
        
    except Exception as e:
        logger.error(f"Error executing JQL query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute JQL query: {str(e)}"
        )

@router.post("/validate", response_model=JQLValidationResponse)
async def validate_jql(jql: str = Query(..., description="JQL query to validate")):
    """
    Validate a JQL query without executing it
    """
    try:
        if jira_service.is_configured():
            try:
                # Try to parse the JQL query with a limit of 0 to just validate syntax
                jira_service.jira_client.search_issues(jql, maxResults=0)
                
                return JQLValidationResponse(
                    is_valid=True,
                    jql=jql,
                    error_message=None,
                    suggestions=[]
                )
                
            except Exception as e:
                error_msg = str(e)
                suggestions = []
                
                # Provide common suggestions based on error
                if "syntax" in error_msg.lower():
                    suggestions.append("Check JQL syntax - ensure proper quotes and operators")
                if "field" in error_msg.lower():
                    suggestions.append("Verify field names are correct for your Jira instance")
                if "function" in error_msg.lower():
                    suggestions.append("Check if JQL functions are supported in your Jira version")
                
                return JQLValidationResponse(
                    is_valid=False,
                    jql=jql,
                    error_message=error_msg,
                    suggestions=suggestions
                )
        else:
            # Basic validation without Jira connection
            basic_validation = jql_converter._validate_and_clean_jql(jql)
            
            return JQLValidationResponse(
                is_valid=bool(basic_validation),
                jql=jql,
                error_message=None if basic_validation else "JQL appears to be empty or invalid",
                suggestions=["Connect to Jira for full validation"] if basic_validation else []
            )
            
    except Exception as e:
        logger.error(f"Error validating JQL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate JQL query: {str(e)}"
        )

@router.get("/suggestions")
async def get_query_suggestions(
    query: str = Query(..., description="Current query to generate suggestions for")
) -> List[str]:
    """
    Get suggestions for improving or extending a query
    """
    try:
        suggestions = jql_converter.get_query_suggestions(query)
        return suggestions
        
    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        return []

@router.get("/fields")
async def get_available_fields():
    """
    Get available JQL fields from the connected Jira instance
    """
    try:
        if jira_service.is_configured():
            try:
                # Get available fields from Jira
                fields = jira_service.jira_client.fields()
                
                # Format fields for frontend use
                formatted_fields = []
                for field in fields:
                    formatted_fields.append({
                        "id": field["id"],
                        "name": field["name"],
                        "custom": field.get("custom", False),
                        "searchable": field.get("searchable", True)
                    })
                
                return formatted_fields
                
            except Exception as e:
                logger.warning(f"Failed to fetch fields from Jira: {e}")
                # Return common default fields
                return [
                    {"id": "project", "name": "Project", "custom": False, "searchable": True},
                    {"id": "status", "name": "Status", "custom": False, "searchable": True},
                    {"id": "assignee", "name": "Assignee", "custom": False, "searchable": True},
                    {"id": "priority", "name": "Priority", "custom": False, "searchable": True},
                    {"id": "issuetype", "name": "Issue Type", "custom": False, "searchable": True},
                    {"id": "created", "name": "Created", "custom": False, "searchable": True},
                    {"id": "updated", "name": "Updated", "custom": False, "searchable": True}
                ]
        else:
            # Return common default fields when not connected
            return [
                {"id": "project", "name": "Project", "custom": False, "searchable": True},
                {"id": "status", "name": "Status", "custom": False, "searchable": True},
                {"id": "assignee", "name": "Assignee", "custom": False, "searchable": True},
                {"id": "priority", "name": "Priority", "custom": False, "searchable": True},
                {"id": "issuetype", "name": "Issue Type", "custom": False, "searchable": True}
            ]
            
    except Exception as e:
        logger.error(f"Error fetching available fields: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch available fields: {str(e)}"
        )
