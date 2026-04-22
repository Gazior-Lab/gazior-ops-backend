# app/schemas/project.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.core.enums.common import ProjectStatus, ProjectVisibility


# ---------------------------------------------------------------------------
# Project schemas
# ---------------------------------------------------------------------------

class ProjectBase(BaseModel):
    workspace_id: int
    name: str = Field(..., min_length=1, max_length=255)
    identifier: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    owner_id: Optional[int] = None
    status: ProjectStatus = ProjectStatus.PLANNED
    visibility: ProjectVisibility = ProjectVisibility.PRIVATE


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    owner_id: Optional[int] = None
    status: Optional[ProjectStatus] = None
    visibility: Optional[ProjectVisibility] = None


class ProjectResponse(ProjectBase):
    id: int
    status_changed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    skip: int
    limit: int
