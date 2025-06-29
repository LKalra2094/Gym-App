from pydantic import BaseModel, model_validator, ConfigDict
from typing import Optional, List
from datetime import date
from enum import Enum
from uuid import UUID

from .weight_unit import WeightUnit

class ChartDataPoint(BaseModel):
    """
    Single data point for exercise charting.
    """
    date: date
    weight: float
    weight_unit: WeightUnit
    reps: int
    sets: int

    model_config = ConfigDict(from_attributes=True)

class DateRangePreset(str, Enum):
    LAST_MONTH = "last_month"
    LAST_3_MONTHS = "last_3_months"
    LAST_6_MONTHS = "last_6_months"
    LAST_12_MONTHS = "last_12_months"
    CUSTOM = "custom"

class WeeklyProgressMetrics(BaseModel):
    """Metrics for weekly weight-lifting progress."""
    start_weight: Optional[float] = None
    end_weight: Optional[float] = None
    average_change_per_week: Optional[float] = None
    number_of_weeks: int = 0
    weight_unit: Optional[WeightUnit] = None

class ExerciseProgress(BaseModel):
    """Comprehensive progress metrics for a single exercise."""
    exercise_id: UUID
    exercise_name: str
    data_points: List[ChartDataPoint]
    personal_best: Optional[float] = None
    personal_best_date: Optional[date] = None
    trend: Optional[float] = None
    weekly_progress: Optional[WeeklyProgressMetrics] = None
    target_unit: WeightUnit

    model_config = ConfigDict(from_attributes=True)

class ProgressQueryParams(BaseModel):
    """
    Query parameters for retrieving exercise progress.
    """
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    target_unit: Optional[WeightUnit] = None
    include_trend: bool = True
    include_personal_best: bool = True
    date_range_preset: Optional[DateRangePreset] = None
    include_weekly_progress: bool = True

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def _check_preset_and_dates(cls, values):
        preset = values.get("date_range_preset")
        start = values.get("start_date")
        end = values.get("end_date")
        if preset and preset != DateRangePreset.CUSTOM and (start or end):
            raise ValueError(
                "Cannot specify start_date or end_date when using a preset"
            )
        return values
