from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.services.label_service import LabelService
from app.schemas.label import (
    LabelCreate,
    LabelUpdate,
    LabelResponse,
    LabelListResponse,
)


router = APIRouter(prefix="/labels", tags=["labels"])



@router.get("", response_model=LabelListResponse)
async def list_labels(
    project_id: int = Query(..., description="Filter labels by project"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all labels in a project."""
    label_service = LabelService(db)
    return await label_service.get_labels(
        project_id=project_id,
        current_user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get("/{label_id}", response_model=LabelResponse)
async def get_label(
    label_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific label by ID."""
    label_service = LabelService(db)
    label = await label_service.get_label(
        label_id=label_id,
        current_user_id=current_user.id
    )
    if not label:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found",
        )
    return label


@router.post("", response_model=LabelResponse, status_code=status.HTTP_201_CREATED)
async def create_label(
    label_data: LabelCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new label (requires workspace OWNER or ADMIN role)."""
    label_service = LabelService(db)
    return await label_service.create_label(
        label_data=label_data,
        current_user_id=current_user.id,
    )


@router.patch("/{label_id}", response_model=LabelResponse)
async def update_label(
    label_id: int,
    label_data: LabelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a label (requires workspace OWNER or ADMIN role)."""
    label_service = LabelService(db)
    return await label_service.update_label(
        label_id=label_id,
        label_data=label_data,
        current_user_id=current_user.id,
    )


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_label(
    label_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a label (requires workspace OWNER or ADMIN role)."""
    label_service = LabelService(db)
    success = await label_service.delete_label(
        label_id=label_id,
        current_user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found",
        )
