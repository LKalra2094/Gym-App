# app/api/v1/exercises.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.exercise import Exercise as ExerciseModel
from app.models.workout import Workout as WorkoutModel
from app.models.user import User as UserModel
from app.schemas.exercise import Exercise, ExerciseCreate, ExerciseUpdate
from app.core.security import get_current_user

router = APIRouter(tags=["exercises"])


@router.post("/", response_model=Exercise, status_code=status.HTTP_201_CREATED)
def create_exercise_for_workout(
    exercise: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = db.execute(
        select(WorkoutModel).filter(
            WorkoutModel.id == exercise.workout_id,
            WorkoutModel.user_id == current_user.id,
        )
    )
    if not result.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

    db_exercise = ExerciseModel(**exercise.model_dump(), user_id=current_user.id)
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


@router.get("/by-workout/{workout_id}", response_model=List[Exercise])
def read_exercises_for_workout(
    workout_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = db.execute(
        select(ExerciseModel)
        .join(WorkoutModel)
        .filter(
            ExerciseModel.workout_id == workout_id,
            WorkoutModel.user_id == current_user.id,
        )
    )
    return result.scalars().all()


@router.get("/{exercise_id}", response_model=Exercise)
def read_exercise(
    exercise_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = db.execute(
        select(ExerciseModel)
        .join(WorkoutModel)
        .filter(
            ExerciseModel.id == exercise_id,
            WorkoutModel.user_id == current_user.id,
        )
    )
    exercise = result.scalars().first()
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return exercise


@router.put("/{exercise_id}", response_model=Exercise)
def update_exercise(
    exercise_id: UUID,
    exercise_in: ExerciseUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    db_exercise = db.get(ExerciseModel, exercise_id)
    if not db_exercise or db_exercise.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    update_data = exercise_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_exercise, field, value)

    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    exercise_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    db_exercise = db.get(ExerciseModel, exercise_id)
    if not db_exercise or db_exercise.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    db.delete(db_exercise)
    db.commit()
    return None
