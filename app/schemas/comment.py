# app/schemas/comment.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Comment schemas
# ---------------------------------------------------------------------------

class CommentBase(BaseModel):
    task_id: int
    content: str = Field(..., min_length=1, max_length=2000)
    is_system_event: bool = False
    author_id: Optional[int] = None


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=2000)


class CommentResponse(CommentBase):
    id: int
    edited_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CommentListResponse(BaseModel):
    comments: List[CommentResponse]
    total: int
    skip: int
    limit: int
