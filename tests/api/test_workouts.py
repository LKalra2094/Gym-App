from fastapi.testclient import TestClient
import pytest
import random
import string
from app.core.config import settings

# Sync helper to get authenticated headers
def get_authenticated_headers(client: TestClient) -> dict:
    """Register, login, and return authentication headers for a new user."""
    email = f"workout_user_{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}@example.com"
    password = "a_very_secure_password"
    
    # Register user
    reg_res = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": email, 
            "password": password, 
            "first_name": "Test",
            "last_name": "Workout User",
            "birthday": "1994-01-01",
            "gender": "male"
        },
    )
    assert reg_res.status_code == 201, reg_res.text
    # Login and get token
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200, login_response.text
    token_data = login_response.json()
    access_token = token_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

def test_create_workout(client: TestClient):
    """Test creating a new workout."""
    auth_headers = get_authenticated_headers(client)
    workout_name = f"Morning Routine {''.join(random.choices(string.ascii_lowercase, k=5))}"
    
    response = client.post(
        f"{settings.API_V1_STR}/workouts/",
        json={"name": workout_name, "description": "A great start to the day."},
        headers=auth_headers,
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == workout_name
    assert "id" in data
    assert "user_id" in data

def test_get_user_workouts(client: TestClient):
    """Test retrieving all workouts for a user."""
    auth_headers = get_authenticated_headers(client)
    # Create a couple of workouts for this user
    client.post(f"{settings.API_V1_STR}/workouts/", json={"name": "Cardio Day"}, headers=auth_headers)
    client.post(f"{settings.API_V1_STR}/workouts/", json={"name": "Weight Day"}, headers=auth_headers)

    response = client.get(f"{settings.API_V1_STR}/workouts/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert "Cardio Day" in [w["name"] for w in data]
    assert "Weight Day" in [w["name"] for w in data]

def test_update_workout(client: TestClient):
    """Test updating a user's workout."""
    auth_headers = get_authenticated_headers(client)
    # Create a workout to update
    workout_name = f"Original Name {''.join(random.choices(string.ascii_lowercase, k=5))}"
    create_response = client.post(
        f"{settings.API_V1_STR}/workouts/",
        json={"name": workout_name},
        headers=auth_headers,
    )
    workout_id = create_response.json()["id"]

    updated_name = "Updated Workout Name"
    response = client.put(
        f"{settings.API_V1_STR}/workouts/{workout_id}",
        json={"name": updated_name},
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == updated_name
    assert data["id"] == workout_id

def test_delete_workout(client: TestClient):
    """Test deleting a user's workout."""
    auth_headers = get_authenticated_headers(client)
    # Create a workout to delete
    workout_name = f"To Be Deleted {''.join(random.choices(string.ascii_lowercase, k=5))}"
    create_response = client.post(
        f"{settings.API_V1_STR}/workouts/",
        json={"name": workout_name},
        headers=auth_headers,
    )
    workout_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"{settings.API_V1_STR}/workouts/{workout_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"{settings.API_V1_STR}/workouts/{workout_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_user_cannot_access_other_users_workout(client: TestClient):
    """Test that a user cannot get, update, or delete another user's workout."""
    # User A creates a workout
    user_a_headers = get_authenticated_headers(client)
    workout_name = f"User A's Secret {''.join(random.choices(string.ascii_lowercase, k=5))}"
    create_response = client.post(
        f"{settings.API_V1_STR}/workouts/",
        json={"name": workout_name},
        headers=user_a_headers,
    )
    user_a_workout_id = create_response.json()["id"]

    # User B logs in
    user_b_headers = get_authenticated_headers(client)

    # User B tries to access User A's workout
    get_response = client.get(f"{settings.API_V1_STR}/workouts/{user_a_workout_id}", headers=user_b_headers)
    assert get_response.status_code == 404

    put_response = client.put(
        f"{settings.API_V1_STR}/workouts/{user_a_workout_id}",
        json={"name": "Hacked"},
        headers=user_b_headers,
    )
    assert put_response.status_code == 403

    delete_response = client.delete(f"{settings.API_V1_STR}/workouts/{user_a_workout_id}", headers=user_b_headers)
    assert delete_response.status_code == 403 