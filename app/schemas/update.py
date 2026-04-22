# app/schemas/update.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Update schemas
# ---------------------------------------------------------------------------

class UpdateBase(BaseModel):
    workspace_id: int
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, max_length=5000)
    tag: str = Field(..., min_length=1, max_length=50)
    department: Optional[str] = Field(None, max_length=100)


class UpdateCreate(UpdateBase):
    pass


class UpdateUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    tag: Optional[str] = Field(None, min_length=1, max_length=50)
    department: Optional[str] = Field(None, max_length=100)


class UpdateResponse(UpdateBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpdateListResponse(BaseModel):
    updates: List[UpdateResponse]
    total: int
    skip: int
    limit: int
