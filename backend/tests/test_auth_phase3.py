from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.core.security import create_access_token, get_password_hash
from app.services.user_service import user_service


def test_phase3_registration_and_login_flow(client: TestClient):
    # 1. Test registration via /auth/register and /api/v1/auth/register
    reg_payload = {
        "email": "freshman2026@campus.edu",
        "password": "SecurePassword2026!",
        "full_name": "Taylor Freshman",
        "phone": "+1 555-4321",
        "department": "Mathematics",
        "student_id": "MATH-2026-99",
    }
    resp = client.post("/auth/register", json=reg_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == reg_payload["email"]
    assert data["student_id"] == "MATH-2026-99"
    assert data["role"] == "USER"
    assert "password" not in data
    assert "password_hash" not in data

    # 2. Test login via /auth/login
    login_payload = {
        "email": "freshman2026@campus.edu",
        "password": "SecurePassword2026!",
    }
    login_resp = client.post("/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
    assert login_data["user"]["email"] == reg_payload["email"]


def test_phase3_duplicate_email_rejected(client: TestClient, test_user: User):
    resp = client.post(
        "/auth/register",
        json={
            "email": test_user.email,
            "password": "Password123!",
            "full_name": "Duplicate Test",
        },
    )
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]


def test_phase3_invalid_login_credentials(client: TestClient, test_user: User):
    # Wrong password
    resp1 = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "WrongPassword!"},
    )
    assert resp1.status_code == 401
    assert "Incorrect email or password" in resp1.json()["detail"]

    # Nonexistent email
    resp2 = client.post(
        "/auth/login",
        json={"email": "nonexistent@campus.edu", "password": "AnyPassword!"},
    )
    assert resp2.status_code == 401


def test_phase3_missing_jwt_token(client: TestClient):
    resp = client.get("/users/me")
    assert resp.status_code == 401


def test_phase3_invalid_and_tampered_jwt(client: TestClient):
    # Malformed token
    resp1 = client.get(
        "/users/me",
        headers={"Authorization": "Bearer malformed.token.value"},
    )
    assert resp1.status_code == 401

    # Tampered signature
    resp2 = client.get(
        "/users/me",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.tamperedSignature"},
    )
    assert resp2.status_code == 401


def test_phase3_expired_jwt(client: TestClient, test_user: User):
    # Generate token already expired by 1 hour
    expired_token = create_access_token(
        subject=test_user.id,
        role=test_user.role.value,
        expires_delta=timedelta(hours=-1),
    )
    resp = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401
    assert "Could not validate credentials" in resp.json()["detail"]


def test_phase3_get_users_me(client: TestClient, user_headers: dict, test_user: User):
    # Test both /users/me and /api/v1/users/me
    resp1 = client.get("/users/me", headers=user_headers)
    assert resp1.status_code == 200
    assert resp1.json()["id"] == test_user.id
    assert resp1.json()["email"] == test_user.email

    resp2 = client.get("/api/v1/users/me", headers=user_headers)
    assert resp2.status_code == 200
    assert resp2.json()["id"] == test_user.id


def test_phase3_put_users_me_profile_update(client: TestClient, user_headers: dict):
    update_payload = {
        "full_name": "Alex P. Student",
        "phone": "+1 555-8899",
        "department": "Data Science",
        "student_id": "DS-2026-44",
    }
    resp = client.put("/users/me", json=update_payload, headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Alex P. Student"
    assert data["phone"] == "+1 555-8899"
    assert data["department"] == "Data Science"
    assert data["student_id"] == "DS-2026-44"


def test_phase3_inactive_user_cannot_login(client: TestClient, db_session: Session):
    # Create deactivated user
    inactive_user = User(
        email="suspended@campus.edu",
        password_hash=get_password_hash("SuspendedPass123!"),
        full_name="Suspended User",
        role=UserRole.USER,
        is_active=False,
    )
    db_session.add(inactive_user)
    db_session.commit()

    resp = client.post(
        "/auth/login",
        json={"email": "suspended@campus.edu", "password": "SuspendedPass123!"},
    )
    assert resp.status_code == 401
    assert "Inactive user account" in resp.json()["detail"]


def test_phase3_inactive_user_token_rejected(client: TestClient, db_session: Session):
    # User had a valid token but was deactivated subsequently
    temp_user = User(
        email="tobedeactivated@campus.edu",
        password_hash=get_password_hash("Password123!"),
        full_name="To Be Deactivated",
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(temp_user)
    db_session.commit()
    db_session.refresh(temp_user)

    token = create_access_token(subject=temp_user.id, role=temp_user.role.value)
    headers = {"Authorization": f"Bearer {token}"}

    # First request works
    resp1 = client.get("/users/me", headers=headers)
    assert resp1.status_code == 200

    # Deactivate user
    user_service.deactivate(db_session, temp_user)

    # Second request is rejected with 401
    resp2 = client.get("/users/me", headers=headers)
    assert resp2.status_code == 401
    assert "Inactive user account" in resp2.json()["detail"]


def test_phase3_user_blocked_from_admin_endpoint(client: TestClient, user_headers: dict):
    resp = client.get("/users/", headers=user_headers)
    assert resp.status_code == 403
    assert "Administrator access required" in resp.json()["detail"]


def test_phase3_admin_allowed_on_admin_endpoint(client: TestClient, admin_headers: dict):
    resp = client.get("/users/", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_phase3_password_never_exposed_in_responses(
    client: TestClient, user_headers: dict, admin_headers: dict
):
    forbidden_keys = {"password", "password_hash", "hashed_password"}

    # 1. Profile /users/me response
    me_resp = client.get("/users/me", headers=user_headers)
    assert me_resp.status_code == 200
    assert not forbidden_keys.intersection(me_resp.json().keys())

    # 2. Login response
    login_resp = client.post(
        "/auth/login",
        json={"email": "student@campus.edu", "password": "Password123!"},
    )
    assert login_resp.status_code == 200
    assert not forbidden_keys.intersection(login_resp.json().keys())
    assert not forbidden_keys.intersection(login_resp.json()["user"].keys())

    # 3. Admin user list response
    users_resp = client.get("/users/", headers=admin_headers)
    assert users_resp.status_code == 200
    for u in users_resp.json():
        assert not forbidden_keys.intersection(u.keys())
