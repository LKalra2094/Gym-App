from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID

class ExerciseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

    @validator('name')
    def name_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or contain only whitespace')
        return v.strip()

class ExerciseCreate(ExerciseBase):
    pass

class Exercise(ExerciseBase):
    id: UUID
    slug: str
    workout_id: UUID
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True 