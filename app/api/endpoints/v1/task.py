# app/api/endpoints/v1/task.py
from typing import Dict, Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, check_workspace_membership
from app.services.task_service import TaskService
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)
from app.core.enums.common import TaskStatus, TaskPriority


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    workspace_id: Optional[int] = None,
    project_id: Optional[int] = None,
    cycle_id: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    assignee_id: Optional[int] = None,
    priority: Optional[TaskPriority] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get paginated list of tasks with filtering options.
    """
    task_service = TaskService(db)
    result = await task_service.get_tasks(
        skip=skip,
        limit=limit,
        workspace_id=workspace_id,
        project_id=project_id,
        cycle_id=cycle_id,
        status=status,
        assignee_id=assignee_id,
        priority=priority,
        search=search,
    )
    return result


@router.get("/identifier/{identifier}", response_model=TaskResponse)
async def get_task_by_identifier(
    identifier: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific task by identifier (e.g., GAZ-123)"""
    task_service = TaskService(db)
    task = await task_service.get_task_by_identifier(identifier)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify user has access to the workspace this task belongs to
    await check_workspace_membership(
        workspace_id=task.workspace_id,
        db=db,
        current_user=current_user,
    )

    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific task by ID"""
    task_service = TaskService(db)
    task = await task_service.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify user has access to the workspace this task belongs to
    await check_workspace_membership(
        workspace_id=task.workspace_id,
        db=db,
        current_user=current_user,
    )

    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new task (requires workspace membership)"""
    task_service = TaskService(db)

    # Verify user has access to the workspace
    workspace_access = await check_workspace_membership(
        workspace_id=task_data.workspace_id,
        db=db,
        current_user=current_user,
    )

    try:
        task = await task_service.create_task(
            task_data=task_data,
            current_user_id=current_user.id
        )
        return task
    except HTTPException:
        raise
    except Exception as e:
        # Don't expose internal error details to clients
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create task"
        )


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a task"""
    task_service = TaskService(db)

    task = await task_service.update_task(
        task_id=task_id,
        task_data=task_data,
        current_user_id=current_user.id
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Soft delete a task"""
    task_service = TaskService(db)

    success = await task_service.delete_task(
        task_id=task_id,
        current_user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.post("/{task_id}/archive", response_model=TaskResponse)
async def archive_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Archive a task"""
    task_service = TaskService(db)

    task = await task_service.archive_task(
        task_id=task_id,
        current_user_id=current_user.id
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.post("/{task_id}/unarchive", response_model=TaskResponse)
async def unarchive_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Unarchive a task"""
    task_service = TaskService(db)

    task = await task_service.unarchive_task(
        task_id=task_id,
        current_user_id=current_user.id
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.post("/bulk/status", response_model=Dict[str, int])
async def bulk_update_status(
    task_ids: List[int],
    new_status: TaskStatus = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Bulk update status for multiple tasks"""
    if not task_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No task IDs provided"
        )

    task_service = TaskService(db)

    updated_count = await task_service.bulk_update_status(
        task_ids=task_ids,
        status=new_status,
        current_user_id=current_user.id
    )

    return {"updated_count": updated_count}
