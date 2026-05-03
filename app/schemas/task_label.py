from typing import List
from pydantic import BaseModel, ConfigDict



class TaskLabelBase(BaseModel):
    task_id: int
    label_id: int


class TaskLabelCreate(TaskLabelBase):
    pass


class TaskLabelResponse(TaskLabelBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TaskLabelListResponse(BaseModel):
    task_labels: List[TaskLabelResponse]
    total: int
    skip: int
    limit: int
