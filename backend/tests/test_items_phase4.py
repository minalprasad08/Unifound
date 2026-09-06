import io
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.item import Item, ItemType, ItemStatus
from app.core.security import create_access_token, get_password_hash
from app.services.audit_service import audit_service


@pytest.fixture
def other_user(db_session: Session) -> User:
    user = User(
        email="otheruser@campus.edu",
        password_hash=get_password_hash("OtherPass123!"),
        full_name="Morgan Other",
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_headers(other_user: User) -> dict:
    token = create_access_token(subject=other_user.id, role=other_user.role.value)
    return {"Authorization": f"Bearer {token}"}


def test_create_lost_item_success(client: TestClient, user_headers: dict, test_user: User):
    payload = {
        "title": "Blue Hydro Flask Water Bottle",
        "description": "32oz stainless steel with stickers from National Parks.",
        "category": "Personal Accessories",
        "location": "Student Union Building 1st Floor Lounge",
        "incident_date": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
        "image_url": "https://example.com/flask.jpg",
    }
    resp = client.post("/items/lost", json=payload, headers=user_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == payload["title"]
    assert data["item_type"] == "LOST"
    assert data["status"] == "OPEN"
    assert data["reported_by"] == test_user.id
    assert "id" in data


def test_create_found_item_success(client: TestClient, user_headers: dict, test_user: User):
    payload = {
        "title": "Car Keys with Honda Fob",
        "description": "Black key fob with silver house key found on bench.",
        "category": "Keys",
        "location": "North Parking Lot near Pole 4",
        "incident_date": datetime.now(timezone.utc).isoformat(),
    }
    resp = client.post("/items/found", json=payload, headers=user_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == payload["title"]
    assert data["item_type"] == "FOUND"
    assert data["status"] == "OPEN"
    assert data["reported_by"] == test_user.id


def test_get_item_details(client: TestClient, user_headers: dict, test_user: User):
    # Create item
    payload = {
        "title": "AirPods Pro Case",
        "description": "White charging case with small scratch on the front.",
        "category": "Electronics",
        "location": "Computer Lab 304",
        "incident_date": datetime.now(timezone.utc).isoformat(),
    }
    create_resp = client.post("/items/lost", json=payload, headers=user_headers)
    item_id = create_resp.json()["id"]

    # Fetch details
    resp = client.get(f"/items/{item_id}", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == item_id
    assert data["title"] == payload["title"]
    assert data["reporter"]["id"] == test_user.id
    assert data["reporter"]["email"] == test_user.email


def test_get_nonexistent_item_returns_404(client: TestClient, user_headers: dict):
    resp = client.get("/items/99999", headers=user_headers)
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_list_my_reports(client: TestClient, user_headers: dict, test_user: User):
    resp = client.get("/items/my", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    for item in data:
        assert item["reported_by"] == test_user.id


def test_update_own_item_success(client: TestClient, user_headers: dict):
    # Create item
    create_resp = client.post(
        "/items/lost",
        json={
            "title": "Black Umbrella",
            "description": "Left in classroom.",
            "category": "Accessories",
            "location": "Science Hall 101",
            "incident_date": datetime.now(timezone.utc).isoformat(),
        },
        headers=user_headers,
    )
    item_id = create_resp.json()["id"]

    # Update item
    update_payload = {
        "title": "Black Wooden-Handle Umbrella",
        "description": "Left by front row desk in classroom.",
        "location": "Science Hall 102",
    }
    resp = client.put(f"/items/{item_id}", json=update_payload, headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Black Wooden-Handle Umbrella"
    assert data["location"] == "Science Hall 102"


def test_non_owner_cannot_update_item_returns_403(
    client: TestClient, user_headers: dict, other_headers: dict
):
    # User 1 creates item
    create_resp = client.post(
        "/items/lost",
        json={
            "title": "Dell Latitude Laptop",
            "description": "Grey laptop in black neoprene sleeve.",
            "category": "Electronics",
            "location": "Library 3rd Floor",
            "incident_date": datetime.now(timezone.utc).isoformat(),
        },
        headers=user_headers,
    )
    item_id = create_resp.json()["id"]

    # User 2 attempts update
    resp = client.put(
        f"/items/{item_id}",
        json={"title": "Hacked Title Attempt"},
        headers=other_headers,
    )
    assert resp.status_code == 403
    assert "do not have permission" in resp.json()["detail"].lower()


def test_close_own_item_success(client: TestClient, user_headers: dict):
    create_resp = client.post(
        "/items/found",
        json={
            "title": "Red Wool Beanie",
            "description": "Found on cafeteria chair.",
            "category": "Clothing",
            "location": "Dining Hall",
            "incident_date": datetime.now(timezone.utc).isoformat(),
        },
        headers=user_headers,
    )
    item_id = create_resp.json()["id"]

    # Close item
    resp = client.delete(f"/items/{item_id}", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "CLOSED"


def test_non_owner_cannot_close_item_returns_403(
    client: TestClient, user_headers: dict, other_headers: dict
):
    create_resp = client.post(
        "/items/found",
        json={
            "title": "Silver Bracelet",
            "description": "Found in chemistry bathroom.",
            "category": "Jewelry",
            "location": "Chem Building 2nd Floor",
            "incident_date": datetime.now(timezone.utc).isoformat(),
        },
        headers=user_headers,
    )
    item_id = create_resp.json()["id"]

    # Other user attempts delete/close
    resp = client.delete(f"/items/{item_id}", headers=other_headers)
    assert resp.status_code == 403
    assert "do not have permission" in resp.json()["detail"].lower()


def test_admin_can_update_and_close_any_item(
    client: TestClient, user_headers: dict, admin_headers: dict
):
    create_resp = client.post(
        "/items/lost",
        json={
            "title": "Calculus Textbook 9th Ed",
            "description": "Hardcover Stewart Calculus book.",
            "category": "Books",
            "location": "Math Study Lounge",
            "incident_date": datetime.now(timezone.utc).isoformat(),
        },
        headers=user_headers,
    )
    item_id = create_resp.json()["id"]

    # Admin updates report
    update_resp = client.put(
        f"/items/{item_id}",
        json={"location": "Math Study Lounge - Security Shelf A"},
        headers=admin_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["location"] == "Math Study Lounge - Security Shelf A"

    # Admin closes report
    close_resp = client.delete(f"/items/{item_id}", headers=admin_headers)
    assert close_resp.status_code == 200
    assert close_resp.json()["status"] == "CLOSED"


def test_unauthenticated_requests_return_401(client: TestClient):
    assert client.post("/items/lost", json={}).status_code == 401
    assert client.post("/items/found", json={}).status_code == 401
    assert client.get("/items/my").status_code == 401
    assert client.get("/items/1").status_code == 401
    assert client.put("/items/1", json={}).status_code == 401
    assert client.delete("/items/1").status_code == 401
    assert client.post("/items/upload-image").status_code == 401


def test_invalid_payload_returns_422(client: TestClient, user_headers: dict):
    # Title too short (< 2 chars), description too short (< 5 chars)
    payload = {
        "title": "A",
        "description": "Bad",
        "category": "Electronics",
        "location": "Somewhere",
        "incident_date": datetime.now(timezone.utc).isoformat(),
    }
    resp = client.post("/items/lost", json=payload, headers=user_headers)
    assert resp.status_code == 422


def test_future_incident_date_returns_422(client: TestClient, user_headers: dict):
    future_date = datetime.now(timezone.utc) + timedelta(days=10)
    payload = {
        "title": "Future Item Report",
        "description": "This item has an incident date in the far future.",
        "category": "Electronics",
        "location": "Campus Center",
        "incident_date": future_date.isoformat(),
    }
    resp = client.post("/items/lost", json=payload, headers=user_headers)
    assert resp.status_code == 422
    assert "future" in resp.text.lower()


def test_ownership_cannot_be_modified(client: TestClient, user_headers: dict, test_user: User):
    create_resp = client.post(
        "/items/lost",
        json={
            "title": "Green Backpack",
            "description": "JanSport backpack with notebooks.",
            "category": "Bags",
            "location": "Bus Stop A",
            "incident_date": datetime.now(timezone.utc).isoformat(),
        },
        headers=user_headers,
    )
    item_id = create_resp.json()["id"]

    # Attempt to change reported_by
    resp = client.put(
        f"/items/{item_id}",
        json={"title": "Green Backpack Updated", "reported_by": 9999},
        headers=user_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["reported_by"] == test_user.id  # Unchanged!


def test_invalid_status_transition_rejected(client: TestClient, user_headers: dict):
    create_resp = client.post(
        "/items/lost",
        json={
            "title": "Casio Wristwatch",
            "description": "Digital sports watch with black rubber strap.",
            "category": "Accessories",
            "location": "Swimming Pool Locker Room",
            "incident_date": datetime.now(timezone.utc).isoformat(),
        },
        headers=user_headers,
    )
    item_id = create_resp.json()["id"]

    # Attempt invalid jump: OPEN -> RESOLVED (must be CLAIMED first)
    resp = client.put(
        f"/items/{item_id}",
        json={"status": "RESOLVED"},
        headers=user_headers,
    )
    assert resp.status_code == 422
    assert "invalid item status transition" in resp.json()["detail"].lower()


def test_image_upload_success_and_validation(client: TestClient, user_headers: dict):
    # 1. Valid JPEG with magic bytes (\xff\xd8\xff)
    valid_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    files = {"file": ("test_image.jpg", io.BytesIO(valid_jpeg), "image/jpeg")}
    resp = client.post("/items/upload-image", files=files, headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "image_url" in data
    assert data["image_url"].startswith("/uploads/")
    assert data["image_url"].endswith(".jpg")

    # 2. Disallowed extension (.exe)
    invalid_exe = b"MZ" + b"\x00" * 50
    files_bad = {"file": ("malicious.exe", io.BytesIO(invalid_exe), "application/octet-stream")}
    resp_bad = client.post("/items/upload-image", files=files_bad, headers=user_headers)
    assert resp_bad.status_code == 422

    # 3. Spoofed extension: named .png but header is garbage
    fake_png = b"NOT_A_REAL_PNG_HEADER" + b"\x00" * 50
    files_fake = {"file": ("spoofed.png", io.BytesIO(fake_png), "image/png")}
    resp_fake = client.post("/items/upload-image", files=files_fake, headers=user_headers)
    assert resp_fake.status_code == 422


def test_audit_log_created_on_item_actions(
    client: TestClient, user_headers: dict, db_session: Session
):
    # Create item
    create_resp = client.post(
        "/items/lost",
        json={
            "title": "Audit Test Wallet",
            "description": "Brown leather bi-fold wallet.",
            "category": "Personal Accessories",
            "location": "Quad Bench",
            "incident_date": datetime.now(timezone.utc).isoformat(),
        },
        headers=user_headers,
    )
    item_id = create_resp.json()["id"]

    # Close item
    client.delete(f"/items/{item_id}", headers=user_headers)

    # Check audit logs
    logs = audit_service.list_logs(db=db_session, entity_type="ITEM", entity_id=item_id)
    actions = [log.action for log in logs]
    assert "ITEM_CREATED" in actions
    assert "ITEM_CLOSED" in actions
