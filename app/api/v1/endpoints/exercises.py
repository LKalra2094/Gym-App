from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models
from ..schemas.exercise import Exercise, ExerciseCreate, ExerciseBase

router = APIRouter(
    prefix="/workouts/{workout_slug}/exercises",
    tags=["exercises"]
)

@router.post("/", response_model=Exercise)
def create_exercise(
    workout_slug: str,
    exercise: ExerciseCreate,
    db: Session = Depends(get_db)
):
    # Verify workout exists
    workout = db.query(models.Workout).filter(models.Workout.slug == workout_slug).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    db_exercise = models.Exercise(**exercise.dict(), workout_id=workout.id)
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

@router.get("/", response_model=List[Exercise])
def read_exercises(workout_slug: str, db: Session = Depends(get_db)):
    # Verify workout exists
    workout = db.query(models.Workout).filter(models.Workout.slug == workout_slug).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    exercises = db.query(models.Exercise).filter(
        models.Exercise.workout_id == workout.id
    ).all()
    return exercises

@router.get("/{exercise_slug}", response_model=Exercise)
def read_exercise(workout_slug: str, exercise_slug: str, db: Session = Depends(get_db)):
    exercise = db.query(models.Exercise).join(models.Workout).filter(
        models.Workout.slug == workout_slug,
        models.Exercise.slug == exercise_slug
    ).first()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise

@router.put("/{exercise_slug}", response_model=Exercise)
def update_exercise(
    workout_slug: str,
    exercise_slug: str,
    exercise: ExerciseBase,
    db: Session = Depends(get_db)
):
    db_exercise = db.query(models.Exercise).join(models.Workout).filter(
        models.Workout.slug == workout_slug,
        models.Exercise.slug == exercise_slug
    ).first()
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    for key, value in exercise.dict().items():
        setattr(db_exercise, key, value)
    
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

@router.delete("/{exercise_slug}")
def delete_exercise(workout_slug: str, exercise_slug: str, db: Session = Depends(get_db)):
    db_exercise = db.query(models.Exercise).join(models.Workout).filter(
        models.Workout.slug == workout_slug,
        models.Exercise.slug == exercise_slug
    ).first()
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    db.delete(db_exercise)
    db.commit()
    return {"message": "Exercise deleted successfully"} 