from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.core.enums.common import WorkspaceMemberRole


class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=255)
    timezone: str = Field(default="UTC", max_length=50)
    description: Optional[str] = Field(None, max_length=500)


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=255)
    timezone: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=500)


class WorkspaceResponse(WorkspaceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class WorkspaceListResponse(BaseModel):
    workspaces: List[WorkspaceResponse]
    total: int
    skip: int
    limit: int


class WorkspaceMemberBase(BaseModel):
    user_id: int
    role: WorkspaceMemberRole = WorkspaceMemberRole.MEMBER


class WorkspaceMemberCreate(WorkspaceMemberBase):
    pass


class WorkspaceMemberUpdate(BaseModel):
    role: Optional[WorkspaceMemberRole] = None


class WorkspaceMemberResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    role: WorkspaceMemberRole
    joined_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceMemberListResponse(BaseModel):
    members: List[WorkspaceMemberResponse]
    total: int
    skip: int
    limit: int


class WorkspaceWithMembers(WorkspaceResponse):
    members: List[WorkspaceMemberResponse] = []
