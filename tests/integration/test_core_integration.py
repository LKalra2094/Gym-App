import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password, get_password_hash, verify_token
from app.core.config import settings
from app.models.user import User
from app.models.workout import Workout
from app.models.exercise import Exercise
from app.models.exercise_log import ExerciseLog
from app.models.enums import UserRole, WeightUnit
from app.core.middleware import RequestIDMiddleware, SecurityHeadersMiddleware, TimingMiddleware

# Test data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_WORKOUT_NAME = "Test Workout"
TEST_EXERCISE_NAME = "Test Exercise"

@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user."""
    user = User(
        email=TEST_USER_EMAIL,
        password=get_password_hash(TEST_USER_PASSWORD),
        role=UserRole.USER,
        is_verified=True,
        preferred_weight_unit=WeightUnit.KG
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_admin(db: Session) -> User:
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        password=get_password_hash("adminpass123"),
        role=UserRole.ADMIN,
        is_verified=True,
        preferred_weight_unit=WeightUnit.KG
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture
def test_workout(db: Session, test_user: User) -> Workout:
    """Create a test workout."""
    workout = Workout(
        name=TEST_WORKOUT_NAME,
        user_id=test_user.id
    )
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout

@pytest.fixture
def test_exercise(db: Session, test_workout: Workout) -> Exercise:
    """Create a test exercise."""
    exercise = Exercise(
        name=TEST_EXERCISE_NAME,
        workout_id=test_workout.id
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise

@pytest.fixture
def test_exercise_log(db: Session, test_exercise: Exercise, test_user: User) -> ExerciseLog:
    """Create a test exercise log."""
    log = ExerciseLog(
        exercise_id=test_exercise.id,
        user_id=test_user.id,
        weight=100.0,
        weight_unit=WeightUnit.KG,
        reps=10,
        sets=3
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_jwt_token_creation_and_verification():
    """Test JWT token creation and verification."""
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    assert token is not None
    
    # Test valid token
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "test@example.com"
    
    # Test expired token
    expired_token = create_access_token(
        data,
        expires_delta=timedelta(microseconds=1)
    )
    payload = verify_token(expired_token)
    assert payload is None

def test_user_model(test_user: User):
    """Test User model functionality."""
    assert test_user.email == TEST_USER_EMAIL
    assert test_user.role == UserRole.USER
    assert test_user.is_verified is True
    assert test_user.preferred_weight_unit == WeightUnit.KG
    assert not test_user.is_admin()
    assert test_user.can_access_user_data(test_user.id)
    assert not test_user.can_access_user_data(uuid4())

def test_admin_model(test_admin: User):
    """Test Admin model functionality."""
    assert test_admin.role == UserRole.ADMIN
    assert test_admin.is_admin()
    assert test_admin.can_access_user_data(uuid4())  # Admins can access any user's data

def test_workout_model(test_workout: Workout):
    """Test Workout model functionality."""
    assert test_workout.name == TEST_WORKOUT_NAME
    assert test_workout.slug == "test-workout"
    assert test_workout.exercises == []

def test_exercise_model(test_exercise: Exercise):
    """Test Exercise model functionality."""
    assert test_exercise.name == TEST_EXERCISE_NAME
    assert test_exercise.slug == "test-exercise"
    assert test_exercise.logs == []

def test_exercise_log_model(test_exercise_log: ExerciseLog):
    """Test ExerciseLog model functionality."""
    assert test_exercise_log.weight == 100.0
    assert test_exercise_log.weight_unit == WeightUnit.KG
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

def test_slug_generation():
    """Test slug generation for workouts and exercises."""
    # Test workout slug
    workout = Workout(name="Test Workout 123!")
    workout.update_slug()
    assert workout.slug == "test-workout-123"
    
    # Test exercise slug
    exercise = Exercise(name="Bench Press (Barbell)")
    exercise.update_slug()
    assert exercise.slug == "bench-press-barbell" 