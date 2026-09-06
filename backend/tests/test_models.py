from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.testclient import TestClient

from app.models import (
    User,
    UserRole,
    Item,
    ItemType,
    ItemStatus,
    Claim,
    ClaimStatus,
    Notification,
    NotificationType,
    AuditLog,
)
from app.schemas.item import ItemCreate, ItemUpdate
from app.schemas.claim import ClaimCreate
from app.schemas.notification import NotificationCreate
from app.services.user_service import user_service
from app.services.item_service import item_service
from app.services.claim_service import claim_service
from app.services.notification_service import notification_service
from app.services.audit_service import audit_service
from app.db.init_db import init_db


def test_user_model_creation_and_soft_delete(db_session: Session):
    user = User(
        email="teststudent@campus.edu",
        password_hash="hashed_secret_pw",
        full_name="Jordan Lee",
        phone="+1 555-1234",
        department="Bioengineering",
        student_id="BIO-2026-001",
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.student_id == "BIO-2026-001"
    assert user.password_hash == "hashed_secret_pw"
    # Test backward compatibility alias
    assert user.hashed_password == "hashed_secret_pw"
    assert user.is_active is True

    # Test soft delete / deactivation requirement
    deactivated = user_service.deactivate(db_session, user)
    assert deactivated.is_active is False

    # Historical user record is preserved
    queried = user_service.get_by_id(db_session, user.id)
    assert queried is not None
    assert queried.is_active is False
    assert queried.email == "teststudent@campus.edu"


def test_item_model_creation_and_relationships(db_session: Session, test_user: User):
    item_in = ItemCreate(
        item_type=ItemType.LOST,
        title="Silver MacBook Air M2",
        description="Left on table in 2nd floor library near the window.",
        category="Electronics",
        location="Main Campus Library",
        incident_date=datetime.now(timezone.utc),
        image_url="https://example.com/macbook.jpg",
    )
    item = item_service.create(db_session, item_in, reported_by=test_user.id)

    assert item.id is not None
    assert item.status == ItemStatus.OPEN
    assert item.reported_by == test_user.id

    # Test bidirectional relationship
    assert item.reporter.id == test_user.id
    assert item in test_user.items

    # Test status transitions
    item_service.transition_status(db_session, item, ItemStatus.CLAIM_PENDING)
    assert item.status == ItemStatus.CLAIM_PENDING

    # Invalid transition should raise ValueError
    with pytest.raises(ValueError):
        # Cannot jump straight from CLAIM_PENDING to RESOLVED without CLAIMED
        item_service.transition_status(db_session, item, ItemStatus.RESOLVED)


def test_claim_model_and_single_active_claim_rule(
    db_session: Session, test_user: User, test_admin: User
):
    # 1. Create an item
    item_in = ItemCreate(
        item_type=ItemType.FOUND,
        title="Graphing Calculator TI-84",
        description="Found in Math Lecture Hall 101",
        category="Electronics",
        location="Math Hall 101",
        incident_date=datetime.now(timezone.utc),
    )
    item = item_service.create(db_session, item_in, reported_by=test_admin.id)

    # 2. First claim submitted by test_user
    claim_in = ClaimCreate(
        item_id=item.id,
        description="This is my TI-84 calculator. It has a blue sticker on the back cover.",
        evidence="Serial: TI-84-PLUS-9901",
    )
    claim1 = claim_service.create(db_session, claim_in, claimant_id=test_user.id)

    assert claim1.id is not None
    assert claim1.status == ClaimStatus.PENDING
    assert claim1.claimant_id == test_user.id
    assert claim1.item_id == item.id
    assert item.status == ItemStatus.CLAIM_PENDING

    # 3. Second claim by SAME claimant on SAME item while pending MUST BE REJECTED
    claim_dup = ClaimCreate(
        item_id=item.id,
        description="Attempting to duplicate claim on same item.",
    )
    with pytest.raises(ValueError, match="already have an active pending claim"):
        claim_service.create(db_session, claim_dup, claimant_id=test_user.id)

    # 4. Admin reviews and approves the claim
    reviewed_claim = claim_service.review(
        db=db_session,
        claim=claim1,
        new_status=ClaimStatus.APPROVED,
        admin_notes="Student verified sticker matches physical item in security safe.",
        reviewer_id=test_admin.id,
    )

    assert reviewed_claim.status == ClaimStatus.APPROVED
    assert reviewed_claim.reviewer.id == test_admin.id
    assert item.status == ItemStatus.CLAIMED
    assert reviewed_claim in test_admin.reviewed_claims


def test_claim_rejection_reverts_item_to_open(
    db_session: Session, test_user: User, test_admin: User
):
    item_in = ItemCreate(
        item_type=ItemType.FOUND,
        title="Keys with Brass Keychain",
        description="Found by Gym entrance",
        category="Keys",
        location="Student Recreation Center",
        incident_date=datetime.now(timezone.utc),
    )
    item = item_service.create(db_session, item_in, reported_by=test_admin.id)

    claim_in = ClaimCreate(
        item_id=item.id,
        description="I lost keys last night.",
    )
    claim = claim_service.create(db_session, claim_in, claimant_id=test_user.id)
    assert item.status == ItemStatus.CLAIM_PENDING

    # Reject claim
    claim_service.review(
        db=db_session,
        claim=claim,
        new_status=ClaimStatus.REJECTED,
        admin_notes="Keys do not match description given.",
        reviewer_id=test_admin.id,
    )

    assert claim.status == ClaimStatus.REJECTED
    # With no other pending claims, item reverts to OPEN
    assert item.status == ItemStatus.OPEN


def test_notification_model_and_relationships(db_session: Session, test_user: User):
    notif_in = NotificationCreate(
        user_id=test_user.id,
        title="Claim Update",
        message="Your claim has been reviewed by campus security.",
        type=NotificationType.CLAIM_UPDATE,
    )
    notification = notification_service.create(db_session, notif_in)

    assert notification.id is not None
    assert notification.is_read is False
    assert notification.user_id == test_user.id
    assert notification in test_user.notifications

    # Test marking as read
    updated = notification_service.mark_as_read(db_session, notification.id, test_user.id)
    assert updated is not None
    assert updated.is_read is True


def test_audit_log_model(db_session: Session, test_admin: User):
    log_entry = audit_service.log(
        db=db_session,
        action="CLAIM_APPROVED",
        entity_type="CLAIM",
        entity_id=42,
        actor_id=test_admin.id,
        details="Verified via student ID and matching sticker.",
    )

    assert log_entry.id is not None
    assert log_entry.action == "CLAIM_APPROVED"
    assert log_entry.entity_type == "CLAIM"
    assert log_entry.actor_id == test_admin.id
    assert log_entry.actor.id == test_admin.id

    # Test system audit log with actor_id=None
    system_log = audit_service.log(
        db=db_session,
        action="SYSTEM_CRON",
        entity_type="SYSTEM",
        actor_id=None,
        details="Automated stale item cleanup check.",
    )
    assert system_log.id is not None
    assert system_log.actor_id is None


def test_public_registration_enforces_user_role(client: TestClient):
    # Attempt to request ADMIN role via public registration endpoint
    payload = {
        "email": "hacker@campus.edu",
        "password": "Password123!",
        "full_name": "Privilege Escalation Test",
        "role": "ADMIN",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    # Must be forced to USER
    assert data["role"] == "USER"
    assert data["role"] != "ADMIN"


def test_database_init_function(db_session: Session):
    # Test that init_db executes cleanly without exceptions
    init_db(db_session)
    admin = user_service.ensure_initial_admin(db_session)
    assert admin is not None
    assert admin.role == UserRole.ADMIN
