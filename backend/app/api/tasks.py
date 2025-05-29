from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from app.models.task import TaskResponse, TaskCreate

# Create router
router = APIRouter(tags=["tasks"])

# Mock data for demonstration
mock_tasks = [
    {
        "id": "JIRA-1",
        "title": "Implement login page",
        "description": "Create a responsive login page with email and password fields",
        "status": "In Progress",
        "assignee": "user1@example.com"
    },
    {
        "id": "JIRA-2",
        "title": "Fix navigation bug",
        "description": "Menu doesn't appear correctly on mobile devices",
        "status": "To Do",
        "assignee": "user2@example.com"
    },
    {
        "id": "JIRA-3",
        "title": "Update documentation",
        "description": "Add API documentation for the new endpoints",
        "status": "Done",
        "assignee": "user1@example.com"
    }
]

@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(status: Optional[str] = None, assignee: Optional[str] = None):
    """
    Get all tasks, with optional filtering by status or assignee.
    """
    filtered_tasks = mock_tasks
    
    if status:
        filtered_tasks = [task for task in filtered_tasks if task["status"].lower() == status.lower()]
    
    if assignee:
        filtered_tasks = [task for task in filtered_tasks if task["assignee"] == assignee]
    
    return filtered_tasks

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """
    Get a specific task by ID.
    """
    for task in mock_tasks:
        if task["id"] == task_id:
            return task
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {task_id} not found"
    )

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """
    Create a new task (mock implementation).
    """
    # In a real implementation, this would create a task in Jira
    new_task = {
        "id": f"JIRA-{len(mock_tasks) + 1}",
        "title": task.title,
        "description": task.description,
        "status": "To Do",
        "assignee": task.assignee
    }
    
    # This is just a mock demo and won't persist after server restart
    mock_tasks.append(new_task)
    
    return new_task