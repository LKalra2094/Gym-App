# app/api/v1/endpoints/auth.py

from datetime import datetime, timedelta, timezone
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User as UserModel
from app.schemas.auth import Token, PasswordReset, PasswordResetConfirm
from app.schemas.user import UserCreate, UserResponse
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.utils.email import send_password_reset_email
from app.core.config import settings

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_new_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    # Prevent duplicate email
    result = db.execute(
        select(UserModel).filter(UserModel.email == user_in.email)
    )
    if result.scalars().first():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user_in.password)
    db_user = UserModel(
        email=user_in.email,
        password=hashed_password,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        birthday=user_in.birthday,
        gender=user_in.gender,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.scalar(select(UserModel).where(UserModel.email == form_data.username))
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/test-token", response_model=dict)
def test_token(current_user: UserModel = Depends(get_current_user)):
    """
    Test access token
    """
    return {"user_id": str(current_user.id)}


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
)
def forgot_password(
    request: PasswordReset,
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(UserModel).filter(UserModel.email == request.email)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Generate token & expiry
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    db.commit()

    # Send email (await if your send function is async)
    send_password_reset_email(email=user.email, token=token)
    return {"message": "Password reset email sent"}


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
)
def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(UserModel).filter(UserModel.reset_token == request.token)
    )
    user = result.scalars().first()

    if (
        not user
        or user.reset_token_expires is None
        or user.reset_token_expires < datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    user.password = get_password_hash(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return {"message": "Password has been reset successfully"}
