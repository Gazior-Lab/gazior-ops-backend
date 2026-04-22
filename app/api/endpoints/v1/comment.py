# app/api/endpoints/v1/comment.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.services.comment_service import CommentService
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentListResponse,
)


router = APIRouter(prefix="/comments", tags=["comments"])


# ---------------------------------------------------------------------------
# Comment endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=CommentListResponse)
async def list_comments(
    task_id: int = Query(..., description="Filter comments by task"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all comments for a task."""
    comment_service = CommentService(db)
    return await comment_service.get_comments(
        task_id=task_id,
        current_user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific comment by ID."""
    comment_service = CommentService(db)
    comment = await comment_service.get_comment(
        comment_id=comment_id,
        current_user_id=current_user.id
    )
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    return comment


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new comment on a task."""
    comment_service = CommentService(db)
    
    # Automatically set the author_id to the current user if not a system event
    if not comment_data.is_system_event:
        comment_data.author_id = current_user.id
        
    return await comment_service.create_comment(
        comment_data=comment_data,
        current_user_id=current_user.id,
    )


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a comment (author only)."""
    comment_service = CommentService(db)
    return await comment_service.update_comment(
        comment_id=comment_id,
        comment_data=comment_data,
        current_user_id=current_user.id,
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Soft-delete a comment (author or workspace admin)."""
    comment_service = CommentService(db)
    success = await comment_service.delete_comment(
        comment_id=comment_id,
        current_user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
