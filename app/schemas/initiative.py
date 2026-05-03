from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.core.enums.common import InitiativeHealthStatus



class InitiativeBase(BaseModel):
    workspace_id: int
    name: str = Field(..., min_length=1, max_length=255)
    summary: Optional[str] = Field(None, max_length=1000)
    owner_id: Optional[int] = None
    health_status: InitiativeHealthStatus = InitiativeHealthStatus.ON_TRACK
    progress_percentage: int = Field(0, ge=0, le=100)


class InitiativeCreate(InitiativeBase):
    pass


class InitiativeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    summary: Optional[str] = Field(None, max_length=1000)
    owner_id: Optional[int] = None
    health_status: Optional[InitiativeHealthStatus] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)


class InitiativeResponse(InitiativeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class InitiativeListResponse(BaseModel):
    initiatives: List[InitiativeResponse]
    total: int
    skip: int
    limit: int
