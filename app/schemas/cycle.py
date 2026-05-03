from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.core.enums.common import CycleStatus



class CycleBase(BaseModel):
    project_id: int
    name: str = Field(..., min_length=1, max_length=255)
    start_date: datetime
    end_date: datetime
    status: CycleStatus = CycleStatus.PLANNED


class CycleCreate(CycleBase):
    pass


class CycleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[CycleStatus] = None


class CycleResponse(CycleBase):
    id: int
    status_changed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CycleListResponse(BaseModel):
    cycles: List[CycleResponse]
    total: int
    skip: int
    limit: int
