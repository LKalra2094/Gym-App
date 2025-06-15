from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models
from ..schemas.workout import Workout, WorkoutCreate
from ..database import get_db

router = APIRouter(
    prefix="/workouts",
    tags=["workouts"]
)

@router.post("/", response_model=Workout)
def create_workout(workout: WorkoutCreate, user_id: int, db: Session = Depends(get_db)):
    db_workout = models.Workout(**workout.dict(), user_id=user_id)
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

@router.get("/", response_model=List[Workout])
def read_workouts(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    workouts = db.query(models.Workout).filter(
        models.Workout.user_id == user_id
    ).offset(skip).limit(limit).all()
    return workouts

@router.get("/{workout_id}", response_model=Workout)
def read_workout(workout_id: int, db: Session = Depends(get_db)):
    db_workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return db_workout

@router.put("/{workout_id}", response_model=Workout)
def update_workout(workout_id: int, workout: WorkoutCreate, db: Session = Depends(get_db)):
    db_workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    for key, value in workout.dict().items():
        setattr(db_workout, key, value)
    
    db.commit()
    db.refresh(db_workout)
    return db_workout

@router.delete("/{workout_id}")
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    db_workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    db.delete(db_workout)
    db.commit()
    return {"message": "Workout deleted successfully"} 