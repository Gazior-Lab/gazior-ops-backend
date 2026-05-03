from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.services.cycle_service import CycleService
from app.schemas.cycle import (
    CycleCreate,
    CycleUpdate,
    CycleResponse,
    CycleListResponse,
)


router = APIRouter(prefix="/cycles", tags=["cycles"])



@router.get("", response_model=CycleListResponse)
async def list_cycles(
    project_id: int = Query(..., description="Filter cycles by project"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all cycles in a project."""
    cycle_service = CycleService(db)
    return await cycle_service.get_cycles(
        project_id=project_id,
        current_user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


@router.get("/{cycle_id}", response_model=CycleResponse)
async def get_cycle(
    cycle_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific cycle by ID."""
    cycle_service = CycleService(db)
    cycle = await cycle_service.get_cycle(
        cycle_id=cycle_id,
        current_user_id=current_user.id
    )
    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found",
        )
    return cycle


@router.post("", response_model=CycleResponse, status_code=status.HTTP_201_CREATED)
async def create_cycle(
    cycle_data: CycleCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new cycle (requires workspace OWNER or ADMIN role)."""
    cycle_service = CycleService(db)
    return await cycle_service.create_cycle(
        cycle_data=cycle_data,
        current_user_id=current_user.id,
    )


@router.patch("/{cycle_id}", response_model=CycleResponse)
async def update_cycle(
    cycle_id: int,
    cycle_data: CycleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a cycle (requires workspace OWNER or ADMIN role)."""
    cycle_service = CycleService(db)
    return await cycle_service.update_cycle(
        cycle_id=cycle_id,
        cycle_data=cycle_data,
        current_user_id=current_user.id,
    )


@router.delete("/{cycle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cycle(
    cycle_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Soft-delete a cycle (requires workspace OWNER or ADMIN role)."""
    cycle_service = CycleService(db)
    success = await cycle_service.delete_cycle(
        cycle_id=cycle_id,
        current_user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cycle not found",
        )
