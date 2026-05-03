from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.services.task_label_service import TaskLabelService
from app.schemas.task_label import (
    TaskLabelCreate,
    TaskLabelResponse,
    TaskLabelListResponse,
)


router = APIRouter(prefix="/task-labels", tags=["task-labels"])



@router.get("", response_model=TaskLabelListResponse)
async def list_task_labels(
    task_id: int = Query(..., description="Filter labels by task"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all labels for a task."""
    task_label_service = TaskLabelService(db)
    return await task_label_service.get_task_labels(
        task_id=task_id,
        current_user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=TaskLabelResponse, status_code=status.HTTP_201_CREATED)
async def add_label_to_task(
    task_label_data: TaskLabelCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Add a label to a task."""
    task_label_service = TaskLabelService(db)
    return await task_label_service.add_label_to_task(
        task_label_data=task_label_data,
        current_user_id=current_user.id,
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def remove_label_from_task(
    task_id: int = Query(..., description="ID of the task"),
    label_id: int = Query(..., description="ID of the label to remove"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Remove a label from a task."""
    task_label_service = TaskLabelService(db)
    success = await task_label_service.remove_label_from_task(
        task_id=task_id,
        label_id=label_id,
        current_user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task label association not found",
        )
