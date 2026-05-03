from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user, check_workspace_membership
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
from app.schemas.invitation import (
    InvitationCreate,
    InvitationCreatedResponse,
    InvitationListResponse,
)
from app.services.invitation_service import InvitationService
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

    # Verify user has access to this workspace
    await check_workspace_membership(
        workspace_id=workspace.id,
        db=db,
        current_user=current_user,
    )

    return workspace


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

    # Verify user has access to this workspace
    await check_workspace_membership(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    # Get workspace members
    members_result = await workspace_service.get_workspace_members(
        workspace_id=workspace_id,
        skip=0,
        limit=1000,
    )

    # Combine workspace with members using proper serialization
    workspace_dict = {
        "id": workspace.id,
        "name": workspace.name,
        "slug": workspace.slug,
        "logo_url": workspace.logo_url,
        "timezone": workspace.timezone,
        "description": workspace.description,
        "created_at": workspace.created_at,
        "updated_at": workspace.updated_at,
        "created_by_id": workspace.created_by_id,
        "updated_by_id": workspace.updated_by_id,
        "members": members_result["members"],
    }

    return WorkspaceWithMembers(**workspace_dict)


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

    return await workspace_service.create_workspace(
        workspace_data=workspace_data,
        current_user_id=current_user.id,
    )


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: int,
    workspace_data: WorkspaceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a workspace (requires OWNER or ADMIN role)"""
    # Verify user has access to this workspace
    await check_workspace_membership(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

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
    # Verify user has access to this workspace
    await check_workspace_membership(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

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
    """Get all members of a workspace (requires workspace membership)"""
    # Verify user has access to this workspace
    await check_workspace_membership(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

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
    # Verify user has access to this workspace
    await check_workspace_membership(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    workspace_service = WorkspaceService(db)

    return await workspace_service.add_member(
        workspace_id=workspace_id,
        user_id=user_id,
        role=role,
        current_user_id=current_user.id,
    )


@router.patch(
    "/{workspace_id}/members/{user_id}",
    response_model=WorkspaceMemberResponse,
)
async def update_workspace_member(
    workspace_id: int,
    user_id: int,
    new_role: WorkspaceMemberRole = Query(...,
                                          description="New role for the member"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update a member's role.
    Only the workspace OWNER can perform this action.
    """
    # Verify user has access to this workspace
    await check_workspace_membership(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

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
    # Verify user has access to this workspace
    await check_workspace_membership(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

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


@router.get(
    "/{workspace_id}/invitations",
    response_model=InvitationListResponse,
)
async def list_workspace_invitations(
    workspace_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List pending and past invitations for a workspace (OWNER or ADMIN)."""
    await check_workspace_membership(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )
    invitation_service = InvitationService(db)
    return await invitation_service.list_invitations(
        workspace_id=workspace_id,
        current_user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/{workspace_id}/invitations",
    response_model=InvitationCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace_invitation(
    workspace_id: int,
    body: InvitationCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create an email invitation to join the workspace (OWNER or ADMIN)."""
    await check_workspace_membership(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )
    invitation_service = InvitationService(db)
    return await invitation_service.create_invitation(
        workspace_id=workspace_id,
        data=body,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{workspace_id}/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_workspace_invitation(
    workspace_id: int,
    invitation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Revoke an invitation (OWNER or ADMIN)."""
    await check_workspace_membership(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )
    invitation_service = InvitationService(db)
    await invitation_service.revoke_invitation(
        workspace_id=workspace_id,
        invitation_id=invitation_id,
        current_user_id=current_user.id,
    )


@router.get("/{workspace_id}/stats")
async def get_workspace_stats(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get workspace statistics"""
    # Verify user has access to this workspace
    await check_workspace_membership(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    workspace_service = WorkspaceService(db)
    stats = await workspace_service.get_workspace_stats(workspace_id)
    return stats
