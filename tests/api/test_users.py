from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User as UserModel
from app.models.enums import UserRole
import random
import string
from typing import Dict, Any
from datetime import date

BASE_URL = f"{settings.API_V1_STR}/users"

# --- Helper Functions ---

def random_string(length: int = 10) -> str:
    """Generate a random string of fixed length."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_user_and_login(
    client: TestClient, db: Session
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Register and login a new user, returning headers and user data."""
    email = f"test_user_{random_string()}@example.com"
    password = "a_very_secure_password"
    
    # Use the public registration endpoint
    registration_data = {
        "email": email, 
        "password": password, 
        "first_name": "Test",
        "last_name": "User",
        "birthday": "1990-01-01",
        "gender": "male"
    }
    reg_res = client.post(f"{settings.API_V1_STR}/auth/register", json=registration_data)
    assert reg_res.status_code == 201, reg_res.text
    user_data = reg_res.json()

    # Login to get token
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/login", data={"username": email, "password": password}
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    return headers, user_data

def login_as_admin(client: TestClient) -> Dict[str, str]:
    """Logs in the default admin user and returns auth headers."""
    login_data = {
        "username": "lakshyakalra123@gmail.com",
        "password": "LK@12345678"
    }
    login_response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert login_response.status_code == 200, "Failed to log in admin user. Ensure the user exists and the database is seeded."
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# --- Test Cases ---

def test_read_users_me(client: TestClient, db_session: Session):
    """Test the /users/me endpoint to get the current user's info."""
    headers, user_data = create_user_and_login(client, db_session)
    
    response = client.get(f"{BASE_URL}/me", headers=headers)
    
    assert response.status_code == 200
    me_data = response.json()
    assert me_data["email"] == user_data["email"]
    assert me_data["id"] == user_data["id"]
    assert me_data["first_name"] == "Test"

def test_admin_can_read_all_users(client: TestClient, db_session: Session):
    """An admin should be able to list all users."""
    # Create a regular user first
    create_user_and_login(client, db_session)

    # Login as admin
    admin_headers = login_as_admin(client)
    
    # Access the user list endpoint
    response = client.get(f"{BASE_URL}/", headers=admin_headers)
    assert response.status_code == 200
    user_list = response.json()
    assert isinstance(user_list, list)
    assert len(user_list) >= 2 # The admin and the user we just created

def test_update_own_user_info(client: TestClient, db_session: Session):
    """Test that a user can update their own information."""
    headers, user_data = create_user_and_login(client, db_session)
    user_id = user_data["id"]
    
    update_data = {"first_name": "Updated", "last_name": "Name"}
    response = client.put(f"{BASE_URL}/{user_id}", json=update_data, headers=headers)
    
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["id"] == user_id
    assert updated_user["first_name"] == "Updated"
    assert updated_user["last_name"] == "Name"

def test_admin_can_delete_user(client: TestClient, db_session: Session):
    """An admin should be able to delete another user."""
    _, user_to_delete = create_user_and_login(client, db_session)
    user_id_to_delete = user_to_delete["id"]

    # Login as admin
    admin_headers = login_as_admin(client)

    # Admin deletes the user
    delete_response = client.delete(f"{BASE_URL}/{user_id_to_delete}", headers=admin_headers)
    assert delete_response.status_code == 204

    # Verify user is gone
    get_response = client.get(f"{BASE_URL}/{user_id_to_delete}", headers=admin_headers)
    assert get_response.status_code == 404 