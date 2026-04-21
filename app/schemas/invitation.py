from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums.common import InvitationStatus, WorkspaceMemberRole


class InvitationCreate(BaseModel):
    email: EmailStr
    role: WorkspaceMemberRole = WorkspaceMemberRole.MEMBER
    expires_in_days: int = Field(default=7, ge=1, le=90)


class InvitationResponse(BaseModel):
    id: int
    workspace_id: int
    inviter_id: int
    email: str
    role: WorkspaceMemberRole
    status: InvitationStatus
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvitationCreatedResponse(InvitationResponse):
    token: str


class InvitationListResponse(BaseModel):
    invitations: List[InvitationResponse]
    total: int
    skip: int
    limit: int
