# app/api/endpoints/v1/attachment.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.services.attachment_service import AttachmentService
from app.schemas.attachment import (
    AttachmentCreate,
    AttachmentUpdate,
    AttachmentResponse,
    AttachmentListResponse,
)


router = APIRouter(prefix="/attachments", tags=["attachments"])


# ---------------------------------------------------------------------------
# Attachment endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=AttachmentListResponse)
async def list_attachments(
    task_id: int = Query(..., description="Filter attachments by task"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all attachments for a task."""
    attachment_service = AttachmentService(db)
    return await attachment_service.get_attachments(
        task_id=task_id,
        current_user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get("/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment(
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific attachment by ID."""
    attachment_service = AttachmentService(db)
    attachment = await attachment_service.get_attachment(
        attachment_id=attachment_id,
        current_user_id=current_user.id
    )
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
    return attachment


@router.post("", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def create_attachment(
    attachment_data: AttachmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new attachment on a task."""
    attachment_service = AttachmentService(db)
    return await attachment_service.create_attachment(
        attachment_data=attachment_data,
        current_user_id=current_user.id,
    )


@router.patch("/{attachment_id}", response_model=AttachmentResponse)
async def update_attachment(
    attachment_id: int,
    attachment_data: AttachmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update an attachment (uploader only)."""
    attachment_service = AttachmentService(db)
    return await attachment_service.update_attachment(
        attachment_id=attachment_id,
        attachment_data=attachment_data,
        current_user_id=current_user.id,
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Soft-delete an attachment (uploader or workspace admin)."""
    attachment_service = AttachmentService(db)
    success = await attachment_service.delete_attachment(
        attachment_id=attachment_id,
        current_user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
