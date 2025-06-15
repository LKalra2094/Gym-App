from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models
from ..schemas.exercise_log import ExerciseLog, ExerciseLogCreate

router = APIRouter(
    prefix="/workouts/{workout_slug}/exercises/{exercise_slug}/logs",
    tags=["exercise_logs"]
)

@router.post("/", response_model=ExerciseLog)
def create_exercise_log(
    workout_slug: str,
    exercise_slug: str,
    log: ExerciseLogCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    # Verify exercise exists and belongs to the workout
    exercise = db.query(models.Exercise).join(models.Workout).filter(
        models.Workout.slug == workout_slug,
        models.Exercise.slug == exercise_slug
    ).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    db_log = models.ExerciseLog(**log.dict(), user_id=user_id, exercise_id=exercise.id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/", response_model=List[ExerciseLog])
def read_exercise_logs(
    workout_slug: str,
    exercise_slug: str,
    db: Session = Depends(get_db)
):
    # Verify exercise exists and belongs to the workout
    exercise = db.query(models.Exercise).join(models.Workout).filter(
        models.Workout.slug == workout_slug,
        models.Exercise.slug == exercise_slug
    ).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    logs = db.query(models.ExerciseLog).filter(
        models.ExerciseLog.exercise_id == exercise.id
    ).order_by(models.ExerciseLog.date.desc()).all()
    return logs

@router.delete("/{log_id}")
def delete_exercise_log(
    workout_slug: str,
    exercise_slug: str,
    log_id: int,
    db: Session = Depends(get_db)
):
    # Verify exercise exists and belongs to the workout
    exercise = db.query(models.Exercise).join(models.Workout).filter(
        models.Workout.slug == workout_slug,
        models.Exercise.slug == exercise_slug
    ).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    db_log = db.query(models.ExerciseLog).filter(
        models.ExerciseLog.id == log_id,
        models.ExerciseLog.exercise_id == exercise.id
    ).first()
    if db_log is None:
        raise HTTPException(status_code=404, detail="Exercise log not found")
    
    db.delete(db_log)
    db.commit()
    return {"message": "Exercise log deleted successfully"} 