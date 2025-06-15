from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date
from enum import Enum
from .weight_unit import WeightUnit
from uuid import UUID

class ChartDataPoint(BaseModel):
    date: date
    weight: float
    weight_unit: WeightUnit
    reps: int
    sets: int

    class Config:
        from_attributes = True

class DateRangePreset(str, Enum):
    LAST_MONTH = "last_month"
    LAST_3_MONTHS = "last_3_months"
    LAST_6_MONTHS = "last_6_months"
    LAST_12_MONTHS = "last_12_months"
    CUSTOM = "custom"

class WeeklyProgressMetrics(BaseModel):
    average_weight_increase: float
    total_weight_increase: float
    number_of_weeks: int
    start_weight: float
    end_weight: float
    weight_unit: WeightUnit

    class Config:
        from_attributes = True

class ExerciseProgress(BaseModel):
    exercise_id: UUID
    exercise_name: str
    data_points: List[ChartDataPoint]
    trend: Optional[float] = None
    personal_best: Optional[float] = None
    personal_best_date: Optional[date] = None
    weekly_progress: Optional[WeeklyProgressMetrics] = None

    class Config:
        from_attributes = True

class ProgressQueryParams(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    target_unit: Optional[str] = None
    include_trend: bool = True
    include_personal_best: bool = True
    date_range_preset: Optional[DateRangePreset] = None
    include_weekly_progress: bool = True

    @validator('start_date', 'end_date')
    def validate_dates_with_preset(cls, v, values):
        if values.get('date_range_preset') and values['date_range_preset'] != DateRangePreset.CUSTOM:
            if v:
                raise ValueError('start_date and end_date should not be provided when using a preset')
        return v

    @validator('target_unit')
    def validate_target_unit(cls, v):
        if v is not None:
            try:
                WeightUnit(v.upper())
            except ValueError:
                raise ValueError(f"Invalid weight unit: {v}")
        return v 