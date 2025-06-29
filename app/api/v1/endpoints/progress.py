# app/api/v1/progress.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, cast, Date
from typing import List, Optional, Tuple
from datetime import date, timedelta
from uuid import UUID
from collections import defaultdict

from app.db.session import get_db
from app.models.exercise_log import ExerciseLog
from app.models.exercise import Exercise
from app.models.user import User
from app.models.workout import Workout
from app.schemas.progress import (
    ChartDataPoint,
    DateRangePreset,
    WeeklyProgressMetrics,
    ExerciseProgress,
)
from app.schemas.weight_unit import WeightUnit
from app.core.security import get_current_user
from app.utils.weight_converter import convert_weight

router = APIRouter()


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


def calculate_weekly_progress(
    data_points: List[ChartDataPoint], target_unit: WeightUnit
) -> WeeklyProgressMetrics:
    """Calculate weekly progress metrics from data points."""
    if len(data_points) < 2:
        return WeeklyProgressMetrics(number_of_weeks=1 if data_points else 0, weight_unit=target_unit)

    sorted_points = sorted(data_points, key=lambda x: x.date)
    
    start_weight = sorted_points[0].weight
    end_weight = sorted_points[-1].weight
    
    days_diff = (sorted_points[-1].date - sorted_points[0].date).days
    num_weeks = (days_diff // 7) + 1

    if num_weeks <= 1:
        avg_change = 0
    else:
        avg_change = (end_weight - start_weight) / (num_weeks -1) if num_weeks > 1 else 0

    return WeeklyProgressMetrics(
        start_weight=start_weight,
        end_weight=end_weight,
        average_change_per_week=avg_change,
        number_of_weeks=num_weeks,
        weight_unit=target_unit,
    )


@router.get(
    "/exercise/{exercise_id}",
    response_model=ExerciseProgress,
    tags=["progress"],
)
def get_exercise_progress(
    exercise_id: UUID,
    target_unit: WeightUnit,
    start_date: date | None = None,
    end_date: date | None = None,
    include_trend: bool = True,
    include_personal_best: bool = True,
    include_weekly_progress: bool = True,
    date_range_preset: DateRangePreset | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExerciseProgress:
    """Get progress data for a specific exercise."""
    # Verify exercise exists and user has access
    result = db.execute(
        select(Exercise)
        .join(Workout)
        .filter(
            Exercise.id == exercise_id,
            Workout.user_id == current_user.id,
        )
    )
    exercise = result.scalars().first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # Determine date range
    if date_range_preset:
        if date_range_preset == DateRangePreset.CUSTOM:
            if not (start_date and end_date):
                raise HTTPException(
                    status_code=400,
                    detail="start_date and end_date are required when using CUSTOM preset",
                )
        else:
            start_date, end_date = get_date_range_from_preset(date_range_preset)
    else:
        # Default date range if none provided
        if not start_date and not end_date:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
        elif not start_date:
            # If only end_date is provided, default start_date to 30 days prior
            start_date = end_date - timedelta(days=30)
        elif not end_date:
            # If only start_date is provided, default end_date to today
            end_date = date.today()

    # Query for logs
    log_query = (
        select(ExerciseLog)
        .where(
            ExerciseLog.exercise_id == exercise.id,
            ExerciseLog.user_id == current_user.id,
            cast(ExerciseLog.date, Date).between(start_date, end_date)
        )
        .order_by(ExerciseLog.date.asc())
    )
    logs = db.execute(log_query).scalars().all()
    if not logs:
        raise HTTPException(status_code=404, detail="No logs found for this exercise in the given date range.")

    # Process logs to create data points and find personal best
    data_points: list[ChartDataPoint] = []
    personal_best: Optional[float] = None
    personal_best_date: Optional[date] = None

    for log in logs:
        weight_in_target = convert_weight(
            log.weight, from_unit=log.weight_unit, to_unit=target_unit
        )
        data_points.append(
            ChartDataPoint(
                date=log.date.date(),
                weight=weight_in_target,
                weight_unit=log.weight_unit,
                reps=log.reps,
                sets=log.sets
            )
        )
        if personal_best is None or weight_in_target > personal_best:
            personal_best = weight_in_target
            personal_best_date = log.date.date()

    response = ExerciseProgress(
        exercise_id=exercise_id,
        exercise_name=exercise.name,
        data_points=data_points,
        personal_best=personal_best,
        personal_best_date=personal_best_date,
        target_unit=target_unit,
    )

    if include_trend:
        # Simple linear regression trend calculation
        n = len(data_points)
        x_vals = [(dp.date - data_points[0].date).days for dp in data_points]
        y_vals = [dp.weight for dp in data_points]
        sum_x = sum(x_vals)
        sum_y = sum(y_vals)
        sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
        sum_xx = sum(x * x for x in x_vals)
        slope = (
            (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x**2)
            if (n * sum_xx - sum_x**2) != 0
            else 0
        )
        response.trend = slope

    if include_weekly_progress:
        response.weekly_progress = calculate_weekly_progress(data_points, target_unit)

    return response


@router.get(
    "/workout/{workout_id}",
    response_model=List[ExerciseProgress],
    tags=["progress"],
)
def get_workout_progress(
    workout_id: UUID,
    target_unit: WeightUnit,
    start_date: date | None = None,
    end_date: date | None = None,
    include_trend: bool = True,
    include_personal_best: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ExerciseProgress]:
    """Get progress data for all exercises in a workout."""
    # Verify workout exists and user has access
    result = db.execute(
        select(Workout).filter(
            Workout.id == workout_id,
            Workout.user_id == current_user.id,
        )
    )
    workout = result.scalars().first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    # Fetch all exercises in the workout
    exercises_result = db.execute(
        select(Exercise).filter(Exercise.workout_id == workout_id)
    )
    exercises = exercises_result.scalars().all()
    if not exercises:
        raise HTTPException(status_code=404, detail="No exercises found in workout")

    # Gather progress for each exercise
    progress_data: List[ExerciseProgress] = []
    for exercise in exercises:
        try:
            progress = get_exercise_progress(
                exercise_id=exercise.id,
                target_unit=target_unit,
                start_date=start_date,
                end_date=end_date,
                include_trend=include_trend,
                include_personal_best=include_personal_best,
                date_range_preset=None,
                current_user=current_user,
                db=db,
            )
            progress_data.append(progress)
        except HTTPException as exc:
            if exc.status_code != 404:
                raise

    if not progress_data:
        raise HTTPException(
            status_code=404,
            detail="No progress data found for any exercises",
        )

    return progress_data
