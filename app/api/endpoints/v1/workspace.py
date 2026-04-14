from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.services.workspace_service import WorkspaceService
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceListResponse,
    WorkspaceWithMembers,
    WorkspaceMemberResponse,
    WorkspaceMemberListResponse,
)
from app.core.enums.common import WorkspaceMemberRole


router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=WorkspaceListResponse)
async def list_workspaces(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get paginated list of workspaces with optional search.
    """
    workspace_service = WorkspaceService(db)
    result = await workspace_service.get_workspaces(
        skip=skip,
        limit=limit,
        search=search,
    )
    return result


@router.get("/my", response_model=WorkspaceListResponse)
async def get_my_workspaces(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get all workspaces where the current user is a member.
    """
    workspace_service = WorkspaceService(db)
    result = await workspace_service.get_user_workspaces(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return result


@router.get("/{workspace_id}", response_model=WorkspaceWithMembers)
async def get_workspace(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific workspace by ID with its members"""
    workspace_service = WorkspaceService(db)
    workspace = await workspace_service.get_workspace(workspace_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Get workspace members
    members_result = await workspace_service.get_workspace_members(
        workspace_id=workspace_id,
        skip=0,
        limit=1000,
    )

    # Combine workspace with members
    return WorkspaceWithMembers(
        **workspace.__dict__,
        members=members_result["members"],
    )


@router.get("/slug/{slug}", response_model=WorkspaceResponse)
async def get_workspace_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific workspace by slug"""
    workspace_service = WorkspaceService(db)
    workspace = await workspace_service.get_workspace_by_slug(slug)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    return workspace


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new workspace.
    The creator will be automatically assigned as the OWNER role.
    """
    workspace_service = WorkspaceService(db)

    try:
        workspace = await workspace_service.create_workspace(
            workspace_data=workspace_data,
            current_user_id=current_user.id,
        )
        return workspace
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: int,
    workspace_data: WorkspaceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a workspace (requires OWNER or ADMIN role)"""
    workspace_service = WorkspaceService(db)

    workspace = await workspace_service.update_workspace(
        workspace_id=workspace_id,
        workspace_data=workspace_data,
        current_user_id=current_user.id,
    )

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Soft delete a workspace.
    Only the workspace OWNER can perform this action.
    """
    workspace_service = WorkspaceService(db)

    success = await workspace_service.delete_workspace(
        workspace_id=workspace_id,
        current_user_id=current_user.id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )


@router.get(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberListResponse,
)
async def list_workspace_members(
    workspace_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all members of a workspace"""
    workspace_service = WorkspaceService(db)
    result = await workspace_service.get_workspace_members(
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
    )
    return result


@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_workspace_member(
    workspace_id: int,
    user_id: int = Query(..., description="User ID to add"),
    role: WorkspaceMemberRole = Query(
        WorkspaceMemberRole.MEMBER,
        description="Role to assign to the new member",
    ),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Add a member to a workspace.
    Requires OWNER or ADMIN role.
    """
    workspace_service = WorkspaceService(db)

    try:
        member = await workspace_service.add_member(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
            current_user_id=current_user.id,
        )
        return member
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{workspace_id}/members/{user_id}",
    response_model=WorkspaceMemberResponse,
)
async def update_workspace_member(
    workspace_id: int,
    user_id: int,
    new_role: WorkspaceMemberRole = Query(..., description="New role for the member"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update a member's role.
    Only the workspace OWNER can perform this action.
    """
    workspace_service = WorkspaceService(db)

    member = await workspace_service.update_member_role(
        workspace_id=workspace_id,
        user_id=user_id,
        new_role=new_role,
        current_user_id=current_user.id,
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    return member


@router.delete(
    "/{workspace_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_workspace_member(
    workspace_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Remove a member from the workspace.
    Users can remove themselves, or OWNER/ADMIN can remove others.
    """
    workspace_service = WorkspaceService(db)

    success = await workspace_service.remove_member(
        workspace_id=workspace_id,
        user_id=user_id,
        current_user_id=current_user.id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )


@router.get("/{workspace_id}/stats")
async def get_workspace_stats(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get workspace statistics"""
    workspace_service = WorkspaceService(db)
    stats = await workspace_service.get_workspace_stats(workspace_id)
    return stats
