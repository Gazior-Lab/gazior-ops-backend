from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict



class TaskHistoryBase(BaseModel):
    task_id: int
    field_name: str = Field(..., min_length=1, max_length=255)
    old_value: Optional[str] = Field(None, max_length=1000)
    new_value: Optional[str] = Field(None, max_length=1000)


class TaskHistoryCreate(TaskHistoryBase):
    changed_by_id: int


class TaskHistoryResponse(TaskHistoryBase):
    id: int
    changed_by_id: int
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskHistoryListResponse(BaseModel):
    histories: List[TaskHistoryResponse]
    total: int
    skip: int
    limit: int
