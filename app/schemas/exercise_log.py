from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime, date as date_type
from ..schemas.weight_unit import WeightUnit

class ExerciseLogBase(BaseModel):
    """
    Shared properties for ExerciseLog models.
    """
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    weight: Optional[float] = Field(None, gt=0)
    reps: Optional[int] = Field(None, gt=0)
    sets: Optional[int] = Field(None, gt=0)
    weight_unit: WeightUnit
    date: date_type = Field(default_factory=date_type.today)

class ExerciseLogCreate(ExerciseLogBase):
    exercise_id: UUID

class ExerciseLogUpdate(BaseModel):
    """
    Properties for updating an ExerciseLog; all fields optional.
    """
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    weight: Optional[float] = Field(None, gt=0)
    reps: Optional[int] = Field(None, gt=0)
    sets: Optional[int] = Field(None, gt=0)
    date: Optional[date_type] = None
    weight_unit: Optional[WeightUnit] = None

class ExerciseLogRead(ExerciseLogBase):
    """
    Properties returned when reading an ExerciseLog from the database.
    """
    id: UUID
    exercise_id: UUID
    user_id: UUID
    date: datetime
    created_at: datetime
    updated_at: datetime

    # BaseModel.Config is deprecated in Pydantic v2; use model_config
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
