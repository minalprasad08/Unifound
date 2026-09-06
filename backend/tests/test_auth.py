from fastapi.testclient import TestClient
from app.models.user import User


def test_register_user_success(client: TestClient):
    payload = {
        "email": "newstudent@campus.edu",
        "password": "Password123!",
        "full_name": "New Student",
        "phone": "+1 555-0333",
        "department": "Physics",
        "role": "USER",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert data["role"] == "USER"
    assert data["is_active"] is True
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient, test_user: User):
    payload = {
        "email": test_user.email,
        "password": "AnotherPassword123!",
        "full_name": "Duplicate Student",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_register_invalid_payload(client: TestClient):
    # Missing required password and invalid email
    payload = {
        "email": "not-an-email",
        "full_name": "A",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client: TestClient, test_user: User):
    payload = {
        "email": test_user.email,
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email
    assert data["user"]["full_name"] == test_user.full_name


def test_login_wrong_password(client: TestClient, test_user: User):
    payload = {
        "email": test_user.email,
        "password": "WrongPassword999!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_nonexistent_email(client: TestClient):
    payload = {
        "email": "nobody@campus.edu",
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_current_user_me(client: TestClient, user_headers: dict, test_user: User):
    response = client.get("/api/v1/auth/me", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id


def test_get_current_user_unauthorized(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token(client: TestClient):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_12345"},
    )
    assert response.status_code == 401


def test_update_user_profile(client: TestClient, user_headers: dict, test_user: User):
    update_payload = {
        "full_name": "Alex Updated",
        "phone": "+1 555-7777",
        "department": "Mechanical Engineering",
    }
    response = client.put("/api/v1/users/profile", json=update_payload, headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Alex Updated"
    assert data["phone"] == "+1 555-7777"
    assert data["department"] == "Mechanical Engineering"


def test_rbac_admin_list_users(client: TestClient, admin_headers: dict, user_headers: dict):
    # Regular user should be forbidden (403)
    user_resp = client.get("/api/v1/users/", headers=user_headers)
    assert user_resp.status_code == 403
    assert "Administrator access required" in user_resp.json()["detail"]

    # Admin user should succeed (200)
    admin_resp = client.get("/api/v1/users/", headers=admin_headers)
    assert admin_resp.status_code == 200
    users = admin_resp.json()
    assert isinstance(users, list)
    assert len(users) >= 2
