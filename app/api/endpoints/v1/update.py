# app/api/endpoints/v1/update.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.services.update_service import UpdateService
from app.schemas.update import (
    UpdateCreate,
    UpdateUpdate,
    UpdateResponse,
    UpdateListResponse,
)


router = APIRouter(prefix="/updates", tags=["updates"])


# ---------------------------------------------------------------------------
# Update endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=UpdateListResponse)
async def list_updates(
    workspace_id: int = Query(..., description="Filter updates by workspace"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tag: Optional[str] = None,
    department: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all updates in a workspace."""
    update_service = UpdateService(db)
    return await update_service.get_updates(
        workspace_id=workspace_id,
        current_user_id=current_user.id,
        skip=skip,
        limit=limit,
        tag=tag,
        department=department,
    )


@router.get("/{update_id}", response_model=UpdateResponse)
async def get_update(
    update_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific update by ID."""
    update_service = UpdateService(db)
    update_obj = await update_service.get_update(
        update_id=update_id,
        current_user_id=current_user.id
    )
    if not update_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
    return update_obj


@router.post("", response_model=UpdateResponse, status_code=status.HTTP_201_CREATED)
async def create_update(
    update_data: UpdateCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new update."""
    update_service = UpdateService(db)
    return await update_service.create_update(
        update_data=update_data,
        current_user_id=current_user.id,
    )


@router.patch("/{update_id}", response_model=UpdateResponse)
async def update_update(
    update_id: int,
    update_data: UpdateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Modify an update (author only)."""
    update_service = UpdateService(db)
    return await update_service.update_update(
        update_id=update_id,
        update_data=update_data,
        current_user_id=current_user.id,
    )


@router.delete("/{update_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_update(
    update_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete an update (author or workspace admin)."""
    update_service = UpdateService(db)
    success = await update_service.delete_update(
        update_id=update_id,
        current_user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found",
        )
