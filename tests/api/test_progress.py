from fastapi.testclient import TestClient
import pytest
from app.core.config import settings
import random
import string
from datetime import date, timedelta

# --- Sync Helper Functions ---

def random_string(length: int = 10) -> str:
    """Generate a random string of fixed length."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_user_and_get_headers(client: TestClient) -> dict:
    """Register and login a new user, returning auth headers."""
    email = f"progress_user_{random_string()}@example.com"
    password = "a_very_secure_password"
    reg_res = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": email, 
            "password": password, 
            "first_name": "Test",
            "last_name": "Progress User",
            "birthday": "1993-01-01",
            "gender": "prefer_not_to_say"
        },
    )
    assert reg_res.status_code == 201, reg_res.text
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login", data={"username": email, "password": password}
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def setup_user_with_progress_data(client: TestClient) -> dict:
    """Create a user, workout, exercise, and multiple logs, returning a dict of relevant IDs and headers."""
    headers = create_user_and_get_headers(client)
    
    # Create Workout
    workout_name = f"Progress Workout {random_string(5)}"
    workout_res = client.post(f"{settings.API_V1_STR}/workouts/", json={"name": workout_name}, headers=headers)
    assert workout_res.status_code == 201, workout_res.text
    workout_id = workout_res.json()["id"]

    # Create Exercise
    exercise_name = f"Progress Exercise {random_string(5)}"
    exercise_res = client.post(f"{settings.API_V1_STR}/exercises/", json={"name": exercise_name, "workout_id": workout_id}, headers=headers)
    assert exercise_res.status_code == 201, exercise_res.text
    exercise_id = exercise_res.json()["id"]

    # Create Exercise Logs with varying dates
    today = date.today()
    for i in range(10):
        # Spread logs over the last 10 days
        log_date = today - timedelta(days=i)
        log_data = {
            "exercise_id": exercise_id,
            "weight": 50 + (i * 2),  # Incrementing weight
            "reps": 10,
            "sets": 3,
            "date": log_date.isoformat(),
            "weight_unit": "kg"
        }
        log_res = client.post(f"{settings.API_V1_STR}/exercise-logs/", json=log_data, headers=headers)
        assert log_res.status_code == 201, log_res.text

    return {
        "headers": headers,
        "workout_id": workout_id,
        "exercise_id": exercise_id,
        "exercise_name": exercise_name,
    }

# --- Test Cases ---
def test_get_exercise_progress(client: TestClient):
    """Test getting progress for a single exercise."""
    test_data = setup_user_with_progress_data(client)
    headers = test_data["headers"]
    exercise_id = test_data["exercise_id"]
    
    response = client.get(f"{settings.API_V1_STR}/progress/exercise/{exercise_id}", headers=headers, params={"target_unit": "kg"})
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["exercise_id"] == exercise_id
    assert data["exercise_name"] == test_data["exercise_name"]
    assert len(data["data_points"]) == 10
    assert data["personal_best"] == 68.0
    assert isinstance(data["trend"], float)

def test_get_workout_progress(client: TestClient):
    """Test getting progress for all exercises in a workout."""
    test_data = setup_user_with_progress_data(client)
    headers = test_data["headers"]
    workout_id = test_data["workout_id"]
    
    response = client.get(f"{settings.API_V1_STR}/progress/workout/{workout_id}", headers=headers, params={"target_unit": "kg"})
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert "exercise_id" in data[0]
    assert len(data[0]["data_points"]) == 10

def test_user_cannot_see_other_user_progress(client: TestClient):
    """Test that a user cannot access another user's progress data."""
    # User A creates data
    user_a_data = setup_user_with_progress_data(client)
    user_a_exercise_id = user_a_data["exercise_id"]
    
    # User B logs in
    user_b_headers = create_user_and_get_headers(client)
    
    # User B tries to get User A's progress
    response = client.get(f"{settings.API_V1_STR}/progress/exercise/{user_a_exercise_id}", headers=user_b_headers, params={"target_unit": "kg"})
    assert response.status_code == 404 # Because the exercise is not found for this user

def test_progress_with_date_range(client: TestClient):
    """Test filtering progress data with a specific date range."""
    test_data = setup_user_with_progress_data(client)
    headers = test_data["headers"]
    exercise_id = test_data["exercise_id"]
    
    # Filter for the last 5 days, which should capture 5-6 logs
    start_date = (date.today() - timedelta(days=5)).isoformat()
    end_date = date.today().isoformat()
    
    params = {"start_date": start_date, "end_date": end_date, "target_unit": "kg"}
    response = client.get(f"{settings.API_V1_STR}/progress/exercise/{exercise_id}", headers=headers, params=params)
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data["data_points"]) == 6 # Day 0, 1, 2, 3, 4, 5

def test_no_progress_data_found(client: TestClient):
    """Test the response when an exercise has no logs."""
    headers = create_user_and_get_headers(client)
    
    # Create a workout first
    workout_res = client.post(f"{settings.API_V1_STR}/workouts/", json={"name": "Test Workout"}, headers=headers)
    assert workout_res.status_code == 201
    workout_id = workout_res.json()["id"]

    # Create an exercise but don't add any logs to it
    exercise_response = client.post(f"{settings.API_V1_STR}/exercises/", headers=headers, json={"name": "Cable Curls", "workout_id": workout_id})
    assert exercise_response.status_code == 201
    exercise_id = exercise_response.json()["id"]

    response = client.get(f"{settings.API_V1_STR}/progress/exercise/{exercise_id}", headers=headers, params={"target_unit": "kg"})

    assert response.status_code == 404
    assert response.json() == {"detail": "No logs found for this exercise in the given date range."} 