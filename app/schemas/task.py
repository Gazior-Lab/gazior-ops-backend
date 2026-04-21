from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.core.enums.common import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: TaskStatus = TaskStatus.BACKLOG
    priority: TaskPriority = TaskPriority.NONE
    position: Optional[int] = None
    assignee_id: Optional[int] = None
    story_points: Optional[float] = Field(None, ge=0)
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    workspace_id: int
    project_id: int
    cycle_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    reporter_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    position: Optional[int] = None
    assignee_id: Optional[int] = None
    story_points: Optional[float] = Field(None, ge=0)
    due_date: Optional[date] = None
    is_archived: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    workspace_id: int
    project_id: int
    cycle_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    number: int
    identifier: str
    reporter_id: int
    ai_summary: Optional[str] = None
    is_archived: bool
    archived_at: Optional[datetime] = None
    archived_by_id: Optional[int] = None
    status_changed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    skip: int
    limit: int