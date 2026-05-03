from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.services.task_history_service import TaskHistoryService
from app.schemas.task_history import TaskHistoryListResponse


router = APIRouter(prefix="/task-histories", tags=["task-histories"])



@router.get("", response_model=TaskHistoryListResponse)
async def list_task_histories(
    task_id: int = Query(..., description="Filter history by task"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all history records for a task."""
    history_service = TaskHistoryService(db)
    return await history_service.get_task_histories(
        task_id=task_id,
        current_user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
