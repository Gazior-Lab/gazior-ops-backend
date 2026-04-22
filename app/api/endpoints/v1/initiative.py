# app/api/endpoints/v1/initiative.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.services.initiative_service import InitiativeService
from app.schemas.initiative import (
    InitiativeCreate,
    InitiativeUpdate,
    InitiativeResponse,
    InitiativeListResponse,
)
from app.core.enums.common import InitiativeHealthStatus


router = APIRouter(prefix="/initiatives", tags=["initiatives"])


# ---------------------------------------------------------------------------
# Initiative endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=InitiativeListResponse)
async def list_initiatives(
    workspace_id: int = Query(..., description="Filter initiatives by workspace"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    health_status: Optional[InitiativeHealthStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all initiatives in a workspace."""
    initiative_service = InitiativeService(db)
    return await initiative_service.get_initiatives(
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
        search=search,
        health_status=health_status.value if health_status else None,
    )


@router.get("/{initiative_id}", response_model=InitiativeResponse)
async def get_initiative(
    initiative_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific initiative by ID."""
    initiative_service = InitiativeService(db)
    initiative = await initiative_service.get_initiative(initiative_id)
    if not initiative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Initiative not found",
        )
    return initiative


@router.post("", response_model=InitiativeResponse, status_code=status.HTTP_201_CREATED)
async def create_initiative(
    initiative_data: InitiativeCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new initiative (requires workspace OWNER or ADMIN role)."""
    initiative_service = InitiativeService(db)
    return await initiative_service.create_initiative(
        initiative_data=initiative_data,
        current_user_id=current_user.id,
    )


@router.patch("/{initiative_id}", response_model=InitiativeResponse)
async def update_initiative(
    initiative_id: int,
    initiative_data: InitiativeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update an initiative (requires workspace OWNER or ADMIN role)."""
    initiative_service = InitiativeService(db)
    return await initiative_service.update_initiative(
        initiative_id=initiative_id,
        initiative_data=initiative_data,
        current_user_id=current_user.id,
    )


@router.delete("/{initiative_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_initiative(
    initiative_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Soft-delete an initiative (requires workspace OWNER or ADMIN role)."""
    initiative_service = InitiativeService(db)
    success = await initiative_service.delete_initiative(
        initiative_id=initiative_id,
        current_user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Initiative not found",
        )
