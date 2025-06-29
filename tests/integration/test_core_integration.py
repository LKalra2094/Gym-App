import pytest
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import timedelta, date
import uuid
import random
import string

from fastapi import HTTPException
from fastapi.testclient import TestClient
from jose import JWTError, jwt
from freezegun import freeze_time
from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)

from app.models.user import User
from app.models.workout import Workout
from app.models.exercise import Exercise
from app.models.exercise_log import ExerciseLog
from app.models.enums import UserRole, WeightUnit, Gender

# Test data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_WORKOUT_NAME = "Test Workout"
TEST_EXERCISE_NAME = "Test Exercise"

def random_string(length: int = 10) -> str:
    """Generate a random string of fixed length."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user with a unique email."""
    email = f"test_{random_string()}@example.com"
    user = User(
        email=email,
        password=get_password_hash(TEST_USER_PASSWORD),
        first_name="Test",
        last_name="User",
        birthday=date(2000, 1, 1),
        gender=Gender.PREFER_NOT_TO_SAY,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_admin(db_session: Session) -> User:
    """Create a test admin user with a unique email."""
    email = f"admin_{random_string()}@example.com"
    admin = User(
        email=email,
        password=get_password_hash("adminpass123"),
        first_name="Admin",
        last_name="User",
        birthday=date(1990, 1, 1),
        gender=Gender.MALE,
        role=UserRole.ADMIN,
        is_verified=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture
def test_workout(db_session: Session, test_user: User) -> Workout:
    """Create a test workout."""
    workout = Workout(
        name=TEST_WORKOUT_NAME,
        user_id=test_user.id
    )
    db_session.add(workout)
    db_session.commit()
    db_session.refresh(workout)
    return workout

@pytest.fixture
def test_exercise(db_session: Session, test_workout: Workout, test_user: User) -> Exercise:
    """Create a test exercise."""
    exercise = Exercise(
        name=TEST_EXERCISE_NAME,
        workout_id=test_workout.id,
        user_id=test_user.id
    )
    db_session.add(exercise)
    db_session.commit()
    db_session.refresh(exercise)
    return exercise

@pytest.fixture
def test_exercise_log(db_session: Session, test_exercise: Exercise, test_user: User) -> ExerciseLog:
    """Create a test exercise log."""
    log = ExerciseLog(
        exercise_id=test_exercise.id,
        user_id=test_user.id,
        weight=100.0,
        reps=10,
        sets=3,
        weight_unit=WeightUnit.KG
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)
    return log

def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

@freeze_time("2023-01-01 12:00:00")
def test_jwt_token_creation_and_verification():
    """Test JWT token creation and verification."""
    user_id = uuid.uuid4()
    # Test valid token
    token = create_access_token(subject=str(user_id))
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert str(payload["sub"]) == str(user_id)
    
    # Test expired token
    expired_token = create_access_token(
        subject=str(user_id),
        expires_delta=timedelta(seconds=-1) # Expired in the past
    )
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(expired_token)
    assert exc_info.value.status_code == 401

def test_user_model(test_user: User):
    """Test the User model creation and attributes."""
    assert test_user.id is not None
    assert "@example.com" in test_user.email
    assert test_user.is_verified is True
    assert test_user.role == UserRole.USER

def test_admin_model(test_admin: User):
    """Test Admin model functionality."""
    assert test_admin.role == UserRole.ADMIN

def test_workout_model(test_workout: Workout, db_session: Session):
    """Test Workout model functionality."""
    assert test_workout.name == TEST_WORKOUT_NAME
    # To check the relationship, we need to re-fetch or use a configured session
    res = db_session.execute(select(Workout).where(Workout.id == test_workout.id))
    workout = res.scalars().one()
    assert workout.exercises == []

def test_exercise_model(test_exercise: Exercise, db_session: Session):
    """Test Exercise model functionality."""
    assert test_exercise.name == TEST_EXERCISE_NAME
    res = db_session.execute(select(Exercise).where(Exercise.id == test_exercise.id))
    exercise = res.scalars().one()
    assert exercise.logs == []

def test_exercise_log_model(test_exercise_log: ExerciseLog):
    """Test ExerciseLog model functionality."""
    assert test_exercise_log.weight == 100.0
    assert test_exercise_log.reps == 10
    assert test_exercise_log.sets == 3

def test_middleware_headers(client: TestClient):
    """Test middleware security headers."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    # Check security headers
    assert "X-Content-Type-Options" in response.headers
    assert "X-Frame-Options" in response.headers
    assert "X-XSS-Protection" in response.headers
    assert "Strict-Transport-Security" in response.headers
    assert "Content-Security-Policy" in response.headers
    
    # Check request ID
    assert "X-Request-ID" in response.headers
    
    # Check timing header
    assert "X-Process-Time" in response.headers
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0 