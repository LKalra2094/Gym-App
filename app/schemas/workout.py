import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.exercise import Exercise

class WorkoutBase(BaseModel):
    """
    Shared properties for Workout schemas.
    """
    name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('name')
    def validate_name(cls, v):
        # Allow None for updates; enforce non-empty when provided
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v

class WorkoutCreate(WorkoutBase):
    """
    Properties to receive on creation of a Workout.
    """
    pass

class WorkoutUpdate(BaseModel):
    """
    Properties to receive on update of a Workout; all fields optional.
    """
    name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v

class WorkoutInDBBase(WorkoutBase):
    """
    Shared properties stored in DB.
    """
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

class Workout(WorkoutInDBBase):
    """
    Properties returned to the client.
    """
    exercises: List[Exercise] = []

    model_config = ConfigDict(from_attributes=True)

class WorkoutInDB(WorkoutInDBBase):
    """
    Properties stored in the database.
    """
    pass
