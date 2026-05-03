from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.services.project_service import ProjectService
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.core.enums.common import ProjectStatus


router = APIRouter(prefix="/projects", tags=["projects"])



@router.get("", response_model=ProjectListResponse)
async def list_projects(
    workspace_id: int = Query(..., description="Filter projects by workspace"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    status: Optional[ProjectStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all projects in a workspace."""
    project_service = ProjectService(db)
    return await project_service.get_projects(
        workspace_id=workspace_id,
        current_user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        status=status.value if status else None,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific project by ID."""
    project_service = ProjectService(db)
    project = await project_service.get_project(
        project_id=project_id,
        current_user_id=current_user.id
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new project (requires workspace OWNER or ADMIN role)."""
    project_service = ProjectService(db)
    return await project_service.create_project(
        project_data=project_data,
        current_user_id=current_user.id,
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a project (requires workspace OWNER or ADMIN role)."""
    project_service = ProjectService(db)
    return await project_service.update_project(
        project_id=project_id,
        project_data=project_data,
        current_user_id=current_user.id,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Soft-delete a project (requires workspace OWNER or ADMIN role)."""
    project_service = ProjectService(db)
    success = await project_service.delete_project(
        project_id=project_id,
        current_user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
