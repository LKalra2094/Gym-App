from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
import uuid

class ExerciseBase(BaseModel):
    name: str
    workout_id: uuid.UUID | None = None

    @field_validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(ExerciseBase):
    name: str | None = None
    workout_id: uuid.UUID | None = None

class ExerciseInDBBase(ExerciseBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

class Exercise(ExerciseInDBBase):
    pass

class ExerciseInDB(ExerciseInDBBase):
    pass
