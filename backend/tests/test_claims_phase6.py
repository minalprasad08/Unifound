import pytest
from datetime import datetime, timezone
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.item import Item, ItemType, ItemStatus
from app.models.user import User, UserRole
from app.models.claim import Claim, ClaimStatus
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.core.security import create_access_token, get_password_hash


@pytest.fixture
def other_user_headers(db_session: Session) -> dict:
    """Create a secondary regular user for testing multi-user claims."""
    user = User(
        email="student2@campus.edu",
        password_hash=get_password_hash("Password123!"),
        full_name="Student Two",
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=str(user.id), role=user.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def third_user_headers(db_session: Session) -> dict:
    """Create a tertiary regular user for testing multi-user claims."""
    user = User(
        email="student3@campus.edu",
        password_hash=get_password_hash("Password123!"),
        full_name="Student Three",
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(subject=str(user.id), role=user.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def target_item(db_session: Session, user_headers: dict) -> Item:
    """Create an item reported by user1."""
    # Find user1
    user1 = db_session.query(User).filter(User.email == "student@campus.edu").first()
    item = Item(
        item_type=ItemType.FOUND,
        title="Silver Apple MacBook Pro 14",
        description="Found in Campus Library Room 302 with charger.",
        category="Electronics & Gadgets",
        location="Campus Library",
        incident_date=datetime.now(timezone.utc),
        status=ItemStatus.OPEN,
        reported_by=user1.id,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


def test_submit_claim_success_and_item_state_transition(
    client: TestClient, db_session: Session, target_item: Item, other_user_headers: dict
):
    """A different user can submit a claim, transitioning the item to CLAIM_PENDING."""
    payload = {
        "item_id": target_item.id,
        "description": "This is my personal MacBook Pro that I forgot on the study desk.",
        "evidence": "Serial number ends in 8976, has a green anime sticker on bottom shell.",
    }
    resp = client.post("/claims", json=payload, headers=other_user_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["item_id"] == target_item.id
    assert data["status"] == "PENDING"
    assert data["evidence"] == payload["evidence"]
    assert data["item"]["title"] == target_item.title
    assert data["claimant"]["email"] == "student2@campus.edu"

    # Verify item status changed to CLAIM_PENDING in DB
    db_session.refresh(target_item)
    assert target_item.status == ItemStatus.CLAIM_PENDING

    # Verify notifications created (one for claimant, one for reporter)
    notifications = db_session.query(Notification).all()
    assert len(notifications) >= 2
    claimant_notif = [n for n in notifications if n.user_id == data["claimant_id"]]
    assert len(claimant_notif) >= 1
    assert "Claim Submitted" in claimant_notif[0].title

    reporter_notif = [n for n in notifications if n.user_id == target_item.reported_by]
    assert len(reporter_notif) >= 1
    assert "New Claim Filed" in reporter_notif[0].title

    # Verify audit log created
    audit = db_session.query(AuditLog).filter(AuditLog.action == "CLAIM_CREATED").first()
    assert audit is not None
    assert audit.entity_id == data["id"]


def test_cannot_claim_own_item_returns_400(
    client: TestClient, target_item: Item, user_headers: dict
):
    """User cannot claim an item they reported themselves."""
    payload = {
        "item_id": target_item.id,
        "description": "Trying to claim my own reported item.",
    }
    resp = client.post("/claims", json=payload, headers=user_headers)
    assert resp.status_code == 400
    assert "You cannot claim an item you reported yourself" in resp.json()["detail"]


def test_duplicate_pending_claim_rejected_returns_400(
    client: TestClient, target_item: Item, other_user_headers: dict
):
    """User cannot submit two active claims for the same item."""
    payload = {
        "item_id": target_item.id,
        "description": "First legitimate claim for my laptop.",
    }
    resp1 = client.post("/claims", json=payload, headers=other_user_headers)
    assert resp1.status_code == 201

    resp2 = client.post("/claims", json=payload, headers=other_user_headers)
    assert resp2.status_code == 400
    assert "already have an active pending claim" in resp2.json()["detail"]


def test_cannot_claim_closed_or_claimed_item(
    client: TestClient, db_session: Session, target_item: Item, other_user_headers: dict
):
    """Item with status CLAIMED or CLOSED cannot receive new claims."""
    target_item.status = ItemStatus.CLAIMED
    db_session.commit()

    payload = {
        "item_id": target_item.id,
        "description": "Attempting to claim an already claimed item.",
    }
    resp = client.post("/claims", json=payload, headers=other_user_headers)
    assert resp.status_code == 400
    assert "Cannot claim an item with status CLAIMED" in resp.json()["detail"]

    target_item.status = ItemStatus.CLOSED
    db_session.commit()
    resp2 = client.post("/claims", json=payload, headers=other_user_headers)
    assert resp2.status_code == 400
    assert "Cannot claim an item with status CLOSED" in resp2.json()["detail"]


def test_list_my_claims(
    client: TestClient, target_item: Item, other_user_headers: dict
):
    """User can list only their submitted claims."""
    payload = {
        "item_id": target_item.id,
        "description": "Checking my submitted claims retrieval.",
    }
    client.post("/claims", json=payload, headers=other_user_headers)

    resp = client.get("/claims/my", headers=other_user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["item"]["id"] == target_item.id


def test_get_claim_details_and_authorization(
    client: TestClient,
    target_item: Item,
    other_user_headers: dict,
    third_user_headers: dict,
    admin_headers: dict,
):
    """Claimant and admin can view claim details; other users are forbidden."""
    payload = {
        "item_id": target_item.id,
        "description": "Detailed claim testing access controls.",
    }
    claim = client.post("/claims", json=payload, headers=other_user_headers).json()
    claim_id = claim["id"]

    # Claimant can view
    resp_owner = client.get(f"/claims/{claim_id}", headers=other_user_headers)
    assert resp_owner.status_code == 200
    assert resp_owner.json()["id"] == claim_id

    # Admin can view
    resp_admin = client.get(f"/claims/{claim_id}", headers=admin_headers)
    assert resp_admin.status_code == 200

    # Third user gets 403 Forbidden
    resp_third = client.get(f"/claims/{claim_id}", headers=third_user_headers)
    assert resp_third.status_code == 403


def test_cancel_own_pending_claim_reverts_item_to_open(
    client: TestClient, db_session: Session, target_item: Item, other_user_headers: dict
):
    """Cancelling own pending claim changes status to CANCELLED and restores item to OPEN."""
    payload = {
        "item_id": target_item.id,
        "description": "I found it at home so I need to cancel this claim.",
    }
    claim = client.post("/claims", json=payload, headers=other_user_headers).json()
    claim_id = claim["id"]

    # Item is CLAIM_PENDING
    db_session.refresh(target_item)
    assert target_item.status == ItemStatus.CLAIM_PENDING

    # Cancel claim
    cancel_resp = client.put(f"/claims/{claim_id}/cancel", headers=other_user_headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"

    # Item reverted to OPEN
    db_session.refresh(target_item)
    assert target_item.status == ItemStatus.OPEN

    # Cannot cancel again
    repeat_cancel = client.put(f"/claims/{claim_id}/cancel", headers=other_user_headers)
    assert repeat_cancel.status_code == 400


def test_admin_approve_claim_updates_item_to_claimed(
    client: TestClient,
    db_session: Session,
    target_item: Item,
    other_user_headers: dict,
    admin_headers: dict,
):
    """Admin approves claim -> claim APPROVED, item CLAIMED."""
    payload = {
        "item_id": target_item.id,
        "description": "Legitimate claim for verified laptop.",
    }
    claim = client.post("/claims", json=payload, headers=other_user_headers).json()
    claim_id = claim["id"]

    approve_resp = client.put(
        f"/admin/claims/{claim_id}/approve",
        json={"admin_notes": "Student verified identity and serial number matches."},
        headers=admin_headers,
    )
    assert approve_resp.status_code == 200
    data = approve_resp.json()
    assert data["status"] == "APPROVED"
    assert data["admin_notes"] == "Student verified identity and serial number matches."
    assert data["reviewed_by"] is not None
    assert data["reviewed_at"] is not None

    db_session.refresh(target_item)
    assert target_item.status == ItemStatus.CLAIMED


def test_admin_approve_claim_rejects_other_pending_claims(
    client: TestClient,
    db_session: Session,
    target_item: Item,
    other_user_headers: dict,
    third_user_headers: dict,
    admin_headers: dict,
):
    """Approving one claim automatically marks other pending claims on that item as REJECTED."""
    c1 = client.post(
        "/claims",
        json={"item_id": target_item.id, "description": "User 2 claim description."},
        headers=other_user_headers,
    ).json()

    c2 = client.post(
        "/claims",
        json={"item_id": target_item.id, "description": "User 3 competing claim."},
        headers=third_user_headers,
    ).json()

    # Admin approves user 2's claim
    client.put(
        f"/admin/claims/{c1['id']}/approve",
        json={"admin_notes": "Verified receipt with store purchase."},
        headers=admin_headers,
    )

    # User 3's claim should now be automatically REJECTED
    c2_record = db_session.get(Claim, c2["id"])
    assert c2_record.status == ClaimStatus.REJECTED
    assert "Another ownership claim was verified" in c2_record.admin_notes


def test_admin_reject_claim_reverts_item_to_open_if_no_others(
    client: TestClient,
    db_session: Session,
    target_item: Item,
    other_user_headers: dict,
    admin_headers: dict,
):
    """Admin rejects solitary pending claim -> item reverts to OPEN."""
    claim = client.post(
        "/claims",
        json={"item_id": target_item.id, "description": "Suspicious claim without details."},
        headers=other_user_headers,
    ).json()

    reject_resp = client.put(
        f"/admin/claims/{claim['id']}/reject",
        json={"admin_notes": "Serial number did not match claimant's report."},
        headers=admin_headers,
    )
    assert reject_resp.status_code == 200
    assert reject_resp.json()["status"] == "REJECTED"

    db_session.refresh(target_item)
    assert target_item.status == ItemStatus.OPEN


def test_regular_user_blocked_from_admin_claim_endpoints_returns_403(
    client: TestClient, other_user_headers: dict
):
    """Normal user cannot access admin claim endpoints."""
    assert client.get("/admin/claims", headers=other_user_headers).status_code == 403
    assert client.get("/admin/claims/1", headers=other_user_headers).status_code == 403
    assert client.put("/admin/claims/1/approve", headers=other_user_headers).status_code == 403
    assert client.put("/admin/claims/1/reject", headers=other_user_headers).status_code == 403


def test_notifications_endpoints(
    client: TestClient, db_session: Session, user_headers: dict
):
    """User can fetch notifications, mark one as read, and mark all as read."""
    # Create notification for user1
    user1 = db_session.query(User).filter(User.email == "student@campus.edu").first()
    notif = Notification(
        user_id=user1.id,
        title="System Notice",
        message="Your campus account has been verified.",
        is_read=False,
    )
    db_session.add(notif)
    db_session.commit()
    db_session.refresh(notif)

    # GET /notifications/my
    resp = client.get("/notifications/my", headers=user_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1

    # PUT /notifications/{id}/read
    read_resp = client.put(f"/notifications/{notif.id}/read", headers=user_headers)
    assert read_resp.status_code == 200
    assert read_resp.json()["is_read"] is True

    # PUT /notifications/read-all
    all_read_resp = client.put("/notifications/read-all", headers=user_headers)
    assert all_read_resp.status_code == 200
    assert "count" in all_read_resp.json()


def test_unauthenticated_requests_return_401(client: TestClient):
    """Unauthenticated claim actions are rejected with 401."""
    assert client.post("/claims", json={"item_id": 1, "description": "Test"}).status_code == 401
    assert client.get("/claims/my").status_code == 401
    assert client.get("/admin/claims").status_code == 401
    assert client.get("/notifications/my").status_code == 401


def test_admin_claims_list_filtering_and_pagination(
    client: TestClient, target_item: Item, other_user_headers: dict, admin_headers: dict
):
    """Admin can list claims with pagination and filter by status."""
    client.post(
        "/claims",
        json={"item_id": target_item.id, "description": "Testing admin list and filter."},
        headers=other_user_headers,
    )

    resp = client.get("/admin/claims?status=PENDING&page=1&page_size=10", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["claims"]) >= 1
    assert data["claims"][0]["status"] == "PENDING"

