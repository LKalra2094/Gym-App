from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi import status

from app.db.session import get_db
from app.models.exercise import Exercise as ExerciseModel
from app.models.exercise_log import ExerciseLog as ExerciseLogModel
from app.models.user import User as UserModel
from app.schemas.exercise_log import (
    ExerciseLogRead,
    ExerciseLogCreate,
    ExerciseLogUpdate,
)
from app.core.security import get_current_user


router = APIRouter()


@router.get("/", response_model=list[ExerciseLogRead])
def read_exercise_logs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Retrieve exercise logs for the current user.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    logs = db.query(ExerciseLogModel).filter(ExerciseLogModel.user_id == current_user.id).offset(skip).limit(limit).all()
    return logs


@router.post("/", response_model=ExerciseLogRead, status_code=status.HTTP_201_CREATED)
def create_exercise_log(
    *,
    db: Session = Depends(get_db),
    log_in: ExerciseLogCreate,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Create new exercise log.
    """
    # First, verify that the exercise exists and belongs to the current user.
    exercise = db.query(ExerciseModel).filter(ExerciseModel.id == log_in.exercise_id, ExerciseModel.user_id == current_user.id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    db_obj = ExerciseLogModel(**log_in.model_dump(), user_id=current_user.id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.get("/exercise/{exercise_id}", response_model=list[ExerciseLogRead])
def read_exercise_logs_for_exercise(
    *,
    db: Session = Depends(get_db),
    exercise_id: UUID,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Retrieve all exercise logs for a specific exercise.
    """
    # Verify the exercise exists and belongs to the user to prevent data leakage
    exercise = db.query(ExerciseModel).filter(ExerciseModel.id == exercise_id, ExerciseModel.user_id == current_user.id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found or not owned by user")

    logs = db.query(ExerciseLogModel).filter(ExerciseLogModel.exercise_id == exercise_id).all()
    return logs


@router.put("/{log_id}", response_model=ExerciseLogRead)
def update_exercise_log(
    *,
    db: Session = Depends(get_db),
    log_id: UUID,
    log_in: ExerciseLogUpdate,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Update an exercise log.
    """
    log = db.get(ExerciseLogModel, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Exercise log not found")
    if log.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = log_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/{log_id}", response_model=ExerciseLogRead)
def read_exercise_log(
    *,
    db: Session = Depends(get_db),
    log_id: UUID,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get exercise log by ID.
    """
    log = db.get(ExerciseLogModel, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Exercise log not found")
    if log.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise_log(
    *,
    db: Session = Depends(get_db),
    log_id: UUID,
    current_user: UserModel = Depends(get_current_user),
):
    """
    Delete an exercise log.
    """
    log = db.get(ExerciseLogModel, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Exercise log not found")
    if log.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(log)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)