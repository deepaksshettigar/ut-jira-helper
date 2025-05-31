from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from app.models.task import TaskResponse, TaskCreate
from app.services.jira_service import jira_service

# Create router
router = APIRouter(tags=["tasks"])

@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(status: Optional[str] = None, assignee: Optional[str] = None):
    """
    Get all tasks from Jira, with optional filtering by status or assignee.
    """
    try:
        tasks = jira_service.get_tasks(status=status, assignee=assignee)
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching tasks: {str(e)}"
        )

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """
    Get a specific task by ID from Jira.
    """
    try:
        task = jira_service.get_task_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching task {task_id}: {str(e)}"
        )

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """
    Create a new task in Jira.
    """
    try:
        new_task = jira_service.create_task(
            title=task.title,
            description=task.description or "",
            assignee=task.assignee or ""
        )
        return new_task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}"
        )