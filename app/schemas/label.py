from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict



class LabelBase(BaseModel):
    project_id: int
    name: str = Field(..., min_length=1, max_length=255)
    color: str = Field(..., min_length=4, max_length=7)  # e.g., #FF5733


class LabelCreate(LabelBase):
    pass


class LabelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    color: Optional[str] = Field(None, min_length=4, max_length=7)


class LabelResponse(LabelBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class LabelListResponse(BaseModel):
    labels: List[LabelResponse]
    total: int
    skip: int
    limit: int
