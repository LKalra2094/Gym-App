from fastapi.testclient import TestClient
import pytest
from app.core.config import settings
import random
import string
from typing import Dict, Tuple

# --- Sync Helper Functions ---

def random_string(length: int = 10) -> str:
    """Generate a random string of fixed length."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_authenticated_user(client: TestClient) -> tuple[dict, str]:
    """Register and login a new user, returning headers and user email."""
    email = f"log_user_{random_string()}@example.com"
    password = "a_very_secure_password"
    reg_res = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": email, 
            "password": password, 
            "first_name": "Test",
            "last_name": "Log User",
            "birthday": "1992-01-01",
            "gender": "other"
        },
    )
    assert reg_res.status_code == 201, reg_res.text

    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login", data={"username": email, "password": password}
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers, email

def setup_user_with_exercise(client: TestClient) -> tuple[dict, str]:
    """Create a user, workout, and exercise, returning headers and the exercise ID."""
    headers, _ = get_authenticated_user(client)
    
    # Create a workout
    workout_name = f"Workout {random_string(5)}"
    workout_res = client.post(
        f"{settings.API_V1_STR}/workouts/", json={"name": workout_name}, headers=headers
    )
    assert workout_res.status_code == 201, workout_res.text
    workout_id = workout_res.json()["id"]

    # Create an exercise within that workout
    exercise_name = f"Exercise {random_string(5)}"
    exercise_res = client.post(
        f"{settings.API_V1_STR}/exercises/",
        json={"name": exercise_name, "workout_id": workout_id},
        headers=headers,
    )
    assert exercise_res.status_code == 201, exercise_res.text
    exercise_id = exercise_res.json()["id"]
    
    return headers, exercise_id

# --- Test Cases ---
def test_create_exercise_log(client: TestClient):
    """Test creating a new exercise log for a user's exercise."""
    headers, exercise_id = setup_user_with_exercise(client)
    
    log_data = {"exercise_id": exercise_id, "weight": 50.5, "reps": 10, "sets": 3, "weight_unit": "kg"}
    response = client.post(
        f"{settings.API_V1_STR}/exercise-logs/", json=log_data, headers=headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["weight"] == 50.5
    assert data["reps"] == 10
    assert data["sets"] == 3
    assert data["exercise_id"] == exercise_id
    assert data["weight_unit"] == "kg"
    assert "id" in data

def test_get_logs_for_exercise(client: TestClient):
    """Test retrieving all logs for a specific exercise."""
    headers, exercise_id = setup_user_with_exercise(client)
    # Create a couple of logs
    client.post(f"{settings.API_V1_STR}/exercise-logs/", json={"exercise_id": exercise_id, "weight": 100, "reps": 5, "sets": 5, "weight_unit": "kg"}, headers=headers)
    client.post(f"{settings.API_V1_STR}/exercise-logs/", json={"exercise_id": exercise_id, "weight": 110, "reps": 4, "sets": 4, "weight_unit": "lbs"}, headers=headers)

    response = client.get(f"{settings.API_V1_STR}/exercise-logs/exercise/{exercise_id}", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["weight"] == 100
    assert data[1]["weight"] == 110
    assert data[0]["weight_unit"] == "kg"
    assert data[1]["weight_unit"] == "lbs"

def test_update_exercise_log(client: TestClient):
    """Test updating an existing exercise log."""
    headers, exercise_id = setup_user_with_exercise(client)
    log_data = {"exercise_id": exercise_id, "weight": 25.5, "reps": 10, "sets": 3, "weight_unit": "kg"}
    log_res = client.post(f"{settings.API_V1_STR}/exercise-logs/", json=log_data, headers=headers)
    log_id = log_res.json()["id"]
    
    update_data = {"weight": 30.0, "reps": 12}
    response = client.put(f"{settings.API_V1_STR}/exercise-logs/{log_id}", json=update_data, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["weight"] == 30.0
    assert data["reps"] == 12
    assert data["sets"] == 3 # Should remain unchanged
    assert data["weight_unit"] == "kg"

def test_delete_exercise_log(client: TestClient):
    """Test deleting an exercise log."""
    headers, exercise_id = setup_user_with_exercise(client)
    log_data = {"exercise_id": exercise_id, "weight": 100, "reps": 10, "sets": 3, "weight_unit": "kg"}
    log_res = client.post(f"{settings.API_V1_STR}/exercise-logs/", json=log_data, headers=headers)
    log_id = log_res.json()["id"]

    del_response = client.delete(f"{settings.API_V1_STR}/exercise-logs/{log_id}", headers=headers)
    assert del_response.status_code == 204

    get_response = client.get(f"{settings.API_V1_STR}/exercise-logs/{log_id}", headers=headers)
    assert get_response.status_code == 404

def test_user_cannot_log_for_another_users_exercise(client: TestClient):
    """Test that User B cannot create a log for User A's exercise."""
    # User A creates an exercise
    _, user_a_exercise_id = setup_user_with_exercise(client)

    # User B logs in
    user_b_headers, _ = get_authenticated_user(client)

    # User B tries to create a log for User A's exercise
    log_data = {"exercise_id": user_a_exercise_id, "weight": 999, "reps": 1, "sets": 1, "weight_unit": "kg"}
    response = client.post(f"{settings.API_V1_STR}/exercise-logs/", json=log_data, headers=user_b_headers)

    assert response.status_code == 404
    assert "Exercise not found" in response.text

def test_user_cannot_access_another_users_log(client: TestClient):
    """Test User B cannot get, update, or delete User A's log."""
    # User A creates an exercise and a log
    user_a_headers, exercise_id = setup_user_with_exercise(client)
    log_res = client.post(f"{settings.API_V1_STR}/exercise-logs/", json={"exercise_id": exercise_id, "weight": 10, "reps": 10, "sets": 10, "weight_unit": "kg"}, headers=user_a_headers)
    user_a_log_id = log_res.json()["id"]

    # User B logs in
    user_b_headers, _ = get_authenticated_user(client)

    # User B tries to access User A's log
    get_response = client.get(f"{settings.API_V1_STR}/exercise-logs/{user_a_log_id}", headers=user_b_headers)
    assert get_response.status_code == 403

    put_response = client.put(f"{settings.API_V1_STR}/exercise-logs/{user_a_log_id}", json={"weight": 1}, headers=user_b_headers)
    assert put_response.status_code == 403

    delete_response = client.delete(f"{settings.API_V1_STR}/exercise-logs/{user_a_log_id}", headers=user_b_headers)
    assert delete_response.status_code == 403

def test_create_exercise_log_with_optional_fields(client: TestClient):
    """Test creating a new exercise log with only required fields, omitting optional ones."""
    headers, exercise_id = setup_user_with_exercise(client)

    log_data = {"exercise_id": exercise_id, "weight_unit": "kg"}
    response = client.post(
        f"{settings.API_V1_STR}/exercise-logs/", json=log_data, headers=headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["exercise_id"] == exercise_id
    assert data["weight"] is None
    assert data["reps"] is None
    assert data["sets"] is None
    assert data["weight_unit"] == "kg"
    assert "id" in data 