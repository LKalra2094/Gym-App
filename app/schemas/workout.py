from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID

class WorkoutBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

    @validator('name')
    def name_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or contain only whitespace')
        return v.strip()

class WorkoutCreate(WorkoutBase):
    pass

class Workout(WorkoutBase):
    id: UUID
    slug: str
    user_id: UUID
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True 