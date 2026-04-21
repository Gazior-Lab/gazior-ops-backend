from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.core.enums.common import TeamMemberRole


# ---------------------------------------------------------------------------
# Team schemas
# ---------------------------------------------------------------------------

class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    workspace_id: int
    lead_id: Optional[int] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    lead_id: Optional[int] = None


class TeamResponse(TeamBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TeamListResponse(BaseModel):
    teams: List[TeamResponse]
    total: int
    skip: int
    limit: int


# ---------------------------------------------------------------------------
# TeamMember schemas
# ---------------------------------------------------------------------------

class TeamMemberBase(BaseModel):
    user_id: int
    role: TeamMemberRole = TeamMemberRole.MEMBER


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMemberUpdate(BaseModel):
    role: Optional[TeamMemberRole] = None


class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    role: TeamMemberRole
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TeamMemberListResponse(BaseModel):
    members: List[TeamMemberResponse]
    total: int
    skip: int
    limit: int
