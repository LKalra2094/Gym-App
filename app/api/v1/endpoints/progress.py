from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from ..database import get_db
from .. import models
from ..schemas.progress import (
    ChartDataPoint, DateRangePreset, WeeklyProgressMetrics, ExerciseProgress, ProgressQueryParams
)
from ..schemas.weight_unit import WeightUnit
from ..utils.auth import get_current_active_user
from ..utils.weight_converter import convert_weight
from uuid import UUID

router = APIRouter(
    prefix="/progress",
    tags=["progress"]
)

def get_date_range_from_preset(preset: DateRangePreset) -> Tuple[date, date]:
    """Get start and end dates based on the preset."""
    end_date = date.today()
    
    if preset == DateRangePreset.LAST_MONTH:
        start_date = end_date - timedelta(days=30)
    elif preset == DateRangePreset.LAST_3_MONTHS:
        start_date = end_date - timedelta(days=90)
    elif preset == DateRangePreset.LAST_6_MONTHS:
        start_date = end_date - timedelta(days=180)
    elif preset == DateRangePreset.LAST_12_MONTHS:
        start_date = end_date - timedelta(days=365)
    else:
        raise ValueError(f"Invalid preset: {preset}")
    
    return start_date, end_date

def calculate_weekly_progress(data_points: List[ChartDataPoint]) -> Optional[WeeklyProgressMetrics]:
    """Calculate weekly progress metrics from data points."""
    if len(data_points) < 2:
        return None
    
    # Sort data points by date
    sorted_points = sorted(data_points, key=lambda x: x.date)
    start_weight = sorted_points[0].weight
    end_weight = sorted_points[-1].weight
    
    # Calculate number of weeks between first and last data point
    days_diff = (sorted_points[-1].date - sorted_points[0].date).days
    number_of_weeks = max(1, days_diff / 7)  # Ensure at least 1 week
    
    # Calculate total and average weight increase
    total_weight_increase = end_weight - start_weight
    average_weight_increase = total_weight_increase / number_of_weeks
    
    return WeeklyProgressMetrics(
        average_weight_increase=round(average_weight_increase, 2),
        total_weight_increase=round(total_weight_increase, 2),
        number_of_weeks=round(number_of_weeks, 1),
        start_weight=start_weight,
        end_weight=end_weight,
        weight_unit=data_points[0].weight_unit
    )

def calculate_trend(data_points: List[ChartDataPoint]) -> Optional[float]:
    """Calculate the trend (slope) of weight progression."""
    if len(data_points) < 2:
        return None
    
    # Convert dates to days since first point
    first_date = data_points[0].date
    x_values = [(point.date - first_date).days for point in data_points]
    y_values = [point.weight for point in data_points]
    
    # Calculate slope using linear regression
    n = len(x_values)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_xx = sum(x * x for x in x_values)
    
    if sum_xx == 0:
        return None
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
    return slope

@router.get("/exercise/{exercise_id}", response_model=ExerciseProgress)
async def get_exercise_progress(
    exercise_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    target_unit: Optional[str] = None,
    include_trend: bool = True,
    include_personal_best: bool = True,
    include_weekly_progress: bool = True,
    date_range_preset: Optional[DateRangePreset] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get progress data for a specific exercise."""
    # Verify exercise exists and user has access
    exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    # Handle date range preset
    if date_range_preset:
        if date_range_preset == DateRangePreset.CUSTOM:
            if not start_date or not end_date:
                raise HTTPException(
                    status_code=400,
                    detail="start_date and end_date are required when using CUSTOM preset"
                )
        else:
            start_date, end_date = get_date_range_from_preset(date_range_preset)
    
    # Build query for exercise logs
    query = db.query(models.ExerciseLog).filter(
        models.ExerciseLog.exercise_id == exercise_id,
        models.ExerciseLog.user_id == current_user.id
    )
    
    # Apply date filters
    if start_date:
        query = query.filter(models.ExerciseLog.created_at >= start_date)
    if end_date:
        query = query.filter(models.ExerciseLog.created_at <= end_date)
    
    # Get logs ordered by date
    logs = query.order_by(models.ExerciseLog.created_at).all()
    
    if not logs:
        raise HTTPException(status_code=404, detail="No progress data found")
    
    # Convert target_unit to WeightUnit if provided
    target_unit_enum = None
    if target_unit is not None:
        try:
            target_unit_enum = WeightUnit(target_unit.upper())
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid weight unit: {target_unit}")
    
    # Convert logs to chart data points
    data_points = []
    personal_best = None
    personal_best_date = None
    
    for log in logs:
        weight = log.weight
        if target_unit_enum and log.weight_unit != target_unit_enum:
            weight = convert_weight(weight, log.weight_unit, target_unit_enum)
        
        data_point = ChartDataPoint(
            date=log.created_at.date(),
            weight=weight,
            weight_unit=target_unit_enum or log.weight_unit,
            reps=log.reps,
            sets=log.sets
        )
        data_points.append(data_point)
        
        # Track personal best
        if include_personal_best and (personal_best is None or weight > personal_best):
            personal_best = weight
            personal_best_date = log.created_at.date()
    
    # Calculate trend if requested
    trend = calculate_trend(data_points) if include_trend else None
    
    # Calculate weekly progress if requested
    weekly_progress = calculate_weekly_progress(data_points) if include_weekly_progress else None
    
    return ExerciseProgress(
        exercise_id=exercise.id,
        exercise_name=exercise.name,
        data_points=data_points,
        trend=trend,
        personal_best=personal_best,
        personal_best_date=personal_best_date,
        weekly_progress=weekly_progress
    )

@router.get("/workout/{workout_id}", response_model=List[ExerciseProgress])
async def get_workout_progress(
    workout_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    target_unit: Optional[str] = None,
    include_trend: bool = True,
    include_personal_best: bool = True,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get progress data for all exercises in a workout."""
    # Verify workout exists and user has access
    workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    # Get all exercises in the workout
    exercises = db.query(models.Exercise).filter(models.Exercise.workout_id == workout_id).all()
    
    if not exercises:
        raise HTTPException(status_code=404, detail="No exercises found in workout")
    
    # Convert target_unit to WeightUnit if provided
    if target_unit is not None:
        try:
            target_unit_enum = WeightUnit(target_unit)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid weight unit: {target_unit}")
    else:
        target_unit_enum = None
    
    # Get progress for each exercise
    progress_data = []
    for exercise in exercises:
        try:
            progress = await get_exercise_progress(
                exercise_id=exercise.id,
                start_date=start_date,
                end_date=end_date,
                target_unit=target_unit,
                include_trend=include_trend,
                include_personal_best=include_personal_best,
                current_user=current_user,
                db=db
            )
            progress_data.append(progress)
        except HTTPException as e:
            if e.status_code != 404:  # Skip exercises with no data
                raise e
    
    if not progress_data:
        raise HTTPException(status_code=404, detail="No progress data found for any exercises")
    
    return progress_data 