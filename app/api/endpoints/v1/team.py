# app/api/endpoints/v1/team.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.services.team_service import TeamService
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamListResponse,
    TeamMemberCreate,
    TeamMemberUpdate,
    TeamMemberResponse,
    TeamMemberListResponse,
)
from app.core.enums.common import TeamMemberRole


router = APIRouter(prefix="/teams", tags=["teams"])


# ---------------------------------------------------------------------------
# Team endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=TeamListResponse)
async def list_teams(
    workspace_id: int = Query(..., description="Filter teams by workspace"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all teams in a workspace."""
    team_service = TeamService(db)
    return await team_service.get_teams(
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
        search=search,
    )


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific team by ID."""
    team_service = TeamService(db)
    team = await team_service.get_team(team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    return team


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new team (requires workspace OWNER or ADMIN role)."""
    team_service = TeamService(db)
    return await team_service.create_team(
        team_data=team_data,
        current_user_id=current_user.id,
    )


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a team's name or lead (requires workspace OWNER or ADMIN role)."""
    team_service = TeamService(db)
    return await team_service.update_team(
        team_id=team_id,
        team_data=team_data,
        current_user_id=current_user.id,
    )


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Soft-delete a team (requires workspace OWNER or ADMIN role)."""
    team_service = TeamService(db)
    success = await team_service.delete_team(
        team_id=team_id,
        current_user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )


# ---------------------------------------------------------------------------
# Team member sub-resource endpoints
# ---------------------------------------------------------------------------

@router.get("/{team_id}/members", response_model=TeamMemberListResponse)
async def list_team_members(
    team_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all members of a team."""
    team_service = TeamService(db)
    return await team_service.get_team_members(
        team_id=team_id,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/{team_id}/members",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_team_member(
    team_id: int,
    member_data: TeamMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Add a user to a team (requires workspace OWNER or ADMIN role)."""
    team_service = TeamService(db)
    return await team_service.add_member(
        team_id=team_id,
        user_id=member_data.user_id,
        role=member_data.role,
        current_user_id=current_user.id,
    )


@router.patch("/{team_id}/members/{user_id}", response_model=TeamMemberResponse)
async def update_team_member_role(
    team_id: int,
    user_id: int,
    member_data: TeamMemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a team member's role (requires workspace OWNER or ADMIN role)."""
    if member_data.role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'role' is required",
        )
    team_service = TeamService(db)
    return await team_service.update_member_role(
        team_id=team_id,
        user_id=user_id,
        new_role=member_data.role,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_team_member(
    team_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Remove a member from a team (requires workspace OWNER or ADMIN role)."""
    team_service = TeamService(db)
    await team_service.remove_member(
        team_id=team_id,
        user_id=user_id,
        current_user_id=current_user.id,
    )
