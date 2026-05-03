from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict



class AttachmentBase(BaseModel):
    task_id: int
    file_name: str = Field(..., min_length=1, max_length=255)
    file_url: str = Field(..., min_length=1, max_length=1000)
    mime_type: str = Field(..., min_length=1, max_length=255)
    size_bytes: int = Field(..., ge=0)


class AttachmentCreate(AttachmentBase):
    uploader_id: Optional[int] = None


class AttachmentUpdate(BaseModel):
    file_name: Optional[str] = Field(None, min_length=1, max_length=255)


class AttachmentResponse(AttachmentBase):
    id: int
    uploader_id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class AttachmentListResponse(BaseModel):
    attachments: List[AttachmentResponse]
    total: int
    skip: int
    limit: int
