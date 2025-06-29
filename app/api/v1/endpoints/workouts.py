# app/api/v1/workouts.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.workout import Workout as WorkoutModel
from app.models.user import User as UserModel
from app.schemas.workout import Workout, WorkoutCreate, WorkoutUpdate
from app.core.security import get_current_user

router = APIRouter(tags=["workouts"])


@router.post("/", response_model=Workout, status_code=status.HTTP_201_CREATED)
def create_workout_for_user(
    workout: WorkoutCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    db_workout = WorkoutModel(**workout.model_dump(), user_id=current_user.id)
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


@router.get("/", response_model=List[Workout])
def read_workouts_for_user(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    workouts = db.execute(
        select(WorkoutModel).filter(WorkoutModel.user_id == current_user.id)
    ).scalars().all()
    return workouts


@router.get("/{workout_id}", response_model=Workout)
def read_workout(
    workout_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    workout = db.execute(
        select(WorkoutModel).filter(
            WorkoutModel.id == workout_id, WorkoutModel.user_id == current_user.id
        )
    ).scalars().first()
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.put("/{workout_id}", response_model=Workout)
def update_workout(
    workout_id: UUID,
    workout_in: WorkoutUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    db_workout = db.get(WorkoutModel, workout_id)
    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    if db_workout.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = workout_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_workout, field, value)
    
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    workout_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    db_workout = db.get(WorkoutModel, workout_id)
    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    if db_workout.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db.delete(db_workout)
    db.commit()
    return None
