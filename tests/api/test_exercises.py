import pytest
from fastapi.testclient import TestClient
from app.core.config import settings
import random
import string
from typing import Dict, Tuple

# Corrected helper to get authenticated headers
def get_authenticated_headers(client: TestClient) -> dict:
    """Register, login, and return authentication headers."""
    email = f"exercise_user_{''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}@example.com"
    password = "a_secure_password"
    
    # Register user
    reg_res = client.post(
        f"{settings.API_V1_STR}/auth/register", 
        json={
            "email": email, 
            "password": password, 
            "first_name": "Test",
            "last_name": "Exercise User",
            "birthday": "1991-01-01",
            "gender": "female"
        }
    )
    assert reg_res.status_code == 201, reg_res.text
    
    # Login and get token
    login_response = client.post(f"{settings.API_V1_STR}/auth/login", data={"username": email, "password": password})
    assert login_response.status_code == 200, login_response.text
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def auth_headers(client: TestClient) -> dict:
    """Fixture to provide authenticated headers for each test function."""
    return get_authenticated_headers(client)

def test_create_exercise(client: TestClient, auth_headers: dict):
    """
    Test creating an exercise, which must be associated with a workout.
    """
    # 1. Create a Workout first
    workout_name = f"Full Body Routine {''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}"
    workout_response = client.post(
        f"{settings.API_V1_STR}/workouts/",
        json={"name": workout_name, "description": "A workout for all major muscle groups."},
        headers=auth_headers,
    )
    assert workout_response.status_code == 201
    workout_data = workout_response.json()
    workout_id = workout_data["id"]

    # 2. Now, create an Exercise linked to that workout
    exercise_name = f"Barbell Squat {''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}"
    exercise_response = client.post(
        f"{settings.API_V1_STR}/exercises/",
        json={"name": exercise_name, "workout_id": workout_id},
        headers=auth_headers,
    )
    
    assert exercise_response.status_code == 201, exercise_response.text
    exercise_data = exercise_response.json()
    assert exercise_data["name"] == exercise_name
    assert "id" in exercise_data
    assert exercise_data["workout_id"] == workout_id

def test_get_exercise(client: TestClient, auth_headers: dict):
    """
    Test retrieving a single exercise by its ID.
    """
    # 1. Create a workout and an exercise to retrieve
    workout_name = f"Strength Day {''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}"
    workout_response = client.post(
        f"{settings.API_V1_STR}/workouts/",
        json={"name": workout_name, "description": "Focus on compound lifts."},
        headers=auth_headers,
    )
    assert workout_response.status_code == 201
    workout_id = workout_response.json()["id"]

    exercise_name = f"Deadlift {''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}"
    exercise_response = client.post(
        f"{settings.API_V1_STR}/exercises/",
        json={"name": exercise_name, "workout_id": workout_id},
        headers=auth_headers,
    )
    assert exercise_response.status_code == 201
    exercise_id = exercise_response.json()["id"]
    created_exercise_name = exercise_response.json()["name"]

    # 2. Retrieve the exercise
    get_response = client.get(f"{settings.API_V1_STR}/exercises/{exercise_id}", headers=auth_headers)
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["name"] == created_exercise_name
    assert get_data["id"] == exercise_id

def test_update_exercise(client: TestClient, auth_headers: dict):
    """Test updating an existing exercise."""
    # 1. Create a workout and an exercise
    workout_name = f"Updatable Workout {''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}"
    workout_response = client.post(
        f"{settings.API_V1_STR}/workouts/",
        json={"name": workout_name, "description": "This workout will be updated."},
        headers=auth_headers,
    )
    assert workout_response.status_code == 201
    workout_id = workout_response.json()["id"]

    exercise_name = f"Initial Name {''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}"
    exercise_response = client.post(
        f"{settings.API_V1_STR}/exercises/",
        json={"name": exercise_name, "workout_id": workout_id},
        headers=auth_headers,
    )
    assert exercise_response.status_code == 201
    exercise_id = exercise_response.json()["id"]

    # 2. Update the exercise
    updated_name = f"Updated Exercise Name {''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}"
    update_response = client.put(
        f"{settings.API_V1_STR}/exercises/{exercise_id}",
        json={"name": updated_name},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["name"] == updated_name
    assert updated_data["id"] == exercise_id

def test_delete_exercise(client: TestClient, auth_headers: dict):
    """Test deleting an existing exercise."""
    # 1. Create a workout and an exercise to delete
    workout_name = f"Deletable Workout {''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}"
    workout_response = client.post(
        f"{settings.API_V1_STR}/workouts/",
        json={"name": workout_name, "description": "This workout will be deleted."},
        headers=auth_headers,
    )
    assert workout_response.status_code == 201
    workout_id = workout_response.json()["id"]

    exercise_name = f"To Be Deleted {''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}"
    exercise_response = client.post(
        f"{settings.API_V1_STR}/exercises/",
        json={"name": exercise_name, "workout_id": workout_id},
        headers=auth_headers,
    )
    assert exercise_response.status_code == 201
    exercise_id = exercise_response.json()["id"]

    # 2. Delete the exercise
    delete_response = client.delete(f"{settings.API_V1_STR}/exercises/{exercise_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    # 3. Verify it's gone
    get_response = client.get(f"{settings.API_V1_STR}/exercises/{exercise_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_unauthenticated_user_cannot_create_exercise(client: TestClient):
    """Test that an unauthenticated user gets a 401 Unauthorized error."""
    response = client.post(
        f"{settings.API_V1_STR}/exercises/",
        json={"name": "Should Fail", "workout_id": "some-uuid"}, # workout_id doesn't matter here
    )
    assert response.status_code == 401

def test_user_cannot_get_other_users_exercise(client: TestClient):
    """Test that a user cannot access an exercise belonging to another user."""
    # 1. User A creates a workout and exercise
    user_a_headers = get_authenticated_headers(client)
    workout_name = f"User A's Private Workout {''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}"
    workout_response = client.post(
        f"{settings.API_V1_STR}/workouts/",
        json={"name": workout_name, "description": ""},
        headers=user_a_headers,
    )
    assert workout_response.status_code == 201
    workout_id = workout_response.json()["id"]

    exercise_name = f"User A's Private Exercise {''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}"
    exercise_response = client.post(
        f"{settings.API_V1_STR}/exercises/",
        json={"name": exercise_name, "workout_id": workout_id},
        headers=user_a_headers,
    )
    assert exercise_response.status_code == 201
    exercise_id_user_a = exercise_response.json()["id"]

    # 2. User B (a new user) tries to get User A's exercise
    user_b_headers = get_authenticated_headers(client)
    
    get_response = client.get(f"{settings.API_V1_STR}/exercises/{exercise_id_user_a}", headers=user_b_headers)
    
    # This should fail with 404 because the security check now hides the resource's existence.
    assert get_response.status_code == 404