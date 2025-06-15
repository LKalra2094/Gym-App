from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID

class ExerciseLogBase(BaseModel):
    weight: float = Field(..., gt=0)
    reps: int = Field(..., gt=0)
    sets: int = Field(..., gt=0)

    @validator('weight')
    def weight_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Weight must be greater than 0')
        return v

    @validator('reps')
    def reps_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Reps must be greater than 0')
        return v

    @validator('sets')
    def sets_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Sets must be greater than 0')
        return v

class ExerciseLogCreate(ExerciseLogBase):
    pass

class ExerciseLog(ExerciseLogBase):
    id: UUID
    exercise_id: UUID
    user_id: UUID
    date: str
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True 