import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.models.item import Item, ItemType, ItemStatus
from app.models.claim import Claim, ClaimStatus
from app.models.notification import Notification, NotificationType
from app.schemas.notification import NotificationCreate
from app.schemas.item import ItemReportCreate
from app.schemas.claim import ClaimCreate
from app.services.item_service import item_service
from app.services.claim_service import claim_service
from app.services.notification_service import notification_service
from app.services.analytics_service import analytics_service


# 1. Match Notification Creation on High Confidence Match
def test_match_notification_creation_on_high_confidence(
    client: TestClient, db_session: Session, test_user: User, test_admin: User
):
    """When a new item produces a match >= 70% confidence, a MATCH_ALERT notification is generated."""
    now = datetime.now(timezone.utc)

    # User reports lost silver Dell XPS laptop
    lost_item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Silver Dell XPS 15 Laptop",
            description="Silver Dell XPS 15 laptop with Intel Core i7 inside black sleeve.",
            category="Electronics",
            location="Library 2nd Floor",
            incident_date=now,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    # Admin reports found matching laptop
    found_item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Silver Dell XPS 15 Laptop",
            description="Found silver Dell XPS 15 laptop with Intel Core i7 inside black sleeve.",
            category="Electronics",
            location="Library 2nd Floor",
            incident_date=now,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_admin.id,
    )

    # Check that a MATCH_ALERT notification was created for test_user
    stmt = select(Notification).where(
        Notification.user_id == test_user.id,
        Notification.type == NotificationType.MATCH_ALERT,
    )
    notifs = list(db_session.execute(stmt).scalars().all())
    assert len(notifs) >= 1
    match_notif = notifs[0]
    assert "Match" in match_notif.title
    assert "Dell XPS" in match_notif.message
    assert match_notif.is_read is False


# 2. Claim Submitted Notification
def test_claim_submitted_notification(
    db_session: Session, test_user: User, test_admin: User
):
    """Claim submission generates notification for both claimant and item reporter."""
    now = datetime.now(timezone.utc)
    found_item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Black Leather Bi-fold Wallet",
            description="Found in lecture hall B with student ID card.",
            category="Accessories",
            location="Lecture Hall B",
            incident_date=now,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_admin.id,
    )

    claim = claim_service.create(
        db=db_session,
        claim_in=ClaimCreate(
            item_id=found_item.id,
            description="This is my leather wallet containing my campus card.",
        ),
        claimant_id=test_user.id,
    )

    # Verify claimant notification
    claimant_notifs = notification_service.list_for_user(db=db_session, user_id=test_user.id)
    assert any("Claim Submitted" in n.title for n in claimant_notifs)

    # Verify reporter notification
    reporter_notifs = notification_service.list_for_user(db=db_session, user_id=test_admin.id)
    assert any("New Claim Filed" in n.title for n in reporter_notifs)


# 3. Claim Approved Notification
def test_claim_approved_notification(
    db_session: Session, test_user: User, test_admin: User
):
    """Approving a claim generates an approval notification for claimant."""
    now = datetime.now(timezone.utc)
    item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Sony WH-CH720N Blue Headphones",
            description="Blue wireless over-ear headphones.",
            category="Electronics",
            location="Cafeteria",
            incident_date=now,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_admin.id,
    )
    claim = claim_service.create(
        db=db_session,
        claim_in=ClaimCreate(
            item_id=item.id,
            description="Lost my blue Sony wireless headphones in the cafeteria.",
        ),
        claimant_id=test_user.id,
    )

    # Admin reviews and approves
    claim_service.review(
        db=db_session,
        claim=claim,
        new_status=ClaimStatus.APPROVED,
        admin_notes="Ownership verified with receipt.",
        reviewer_id=test_admin.id,
    )

    user_notifs = notification_service.list_for_user(db=db_session, user_id=test_user.id)
    assert any("Claim Approved" in n.title for n in user_notifs)


# 4. Claim Rejected Notification
def test_claim_rejected_notification(
    db_session: Session, test_user: User, test_admin: User
):
    """Rejecting a claim generates rejection notification with admin note."""
    now = datetime.now(timezone.utc)
    item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Casio Scientific Calculator",
            description="Black scientific fx-991EX calculator.",
            category="Electronics",
            location="Math Lab",
            incident_date=now,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_admin.id,
    )
    claim = claim_service.create(
        db=db_session,
        claim_in=ClaimCreate(
            item_id=item.id,
            description="I left my Casio calculator on the desk.",
        ),
        claimant_id=test_user.id,
    )

    claim_service.review(
        db=db_session,
        claim=claim,
        new_status=ClaimStatus.REJECTED,
        admin_notes="Serial number does not match.",
        reviewer_id=test_admin.id,
    )

    user_notifs = notification_service.list_for_user(db=db_session, user_id=test_user.id)
    assert any("Claim Rejected" in n.title for n in user_notifs)


# 5. User Notification Isolation
def test_user_notification_isolation(
    client: TestClient, db_session: Session, test_user: User, test_admin: User, user_token: str, admin_token: str
):
    """Users can only see their own notifications, never another user's."""
    # Create notification specifically for admin
    notification_service.create(
        db=db_session,
        notification_in=NotificationCreate(
            user_id=test_admin.id,
            title="Admin Security Broadcast",
            message="Internal administration broadcast message.",
            type=NotificationType.SYSTEM,
        ),
    )

    # Test regular user request
    headers_user = {"Authorization": f"Bearer {user_token}"}
    resp = client.get("/api/v1/notifications/", headers=headers_user)
    assert resp.status_code == 200
    user_notif_ids = [n["id"] for n in resp.json()]

    # Verify admin's notification is NOT in user's list
    for n in resp.json():
        assert n["user_id"] == test_user.id
        assert n["title"] != "Admin Security Broadcast"


# 6. Mark Individual Notification as Read
def test_mark_notification_as_read(
    client: TestClient, db_session: Session, test_user: User, test_admin: User, user_token: str, admin_token: str
):
    """User can mark their own notification as read; cannot mark another user's."""
    notif = notification_service.create(
        db=db_session,
        notification_in=NotificationCreate(
            user_id=test_user.id,
            title="Read Test Notice",
            message="Please read this notice.",
            type=NotificationType.INFO,
        ),
    )
    assert notif.is_read is False

    # Mark as read with user token
    headers_user = {"Authorization": f"Bearer {user_token}"}
    resp = client.put(f"/api/v1/notifications/{notif.id}/read", headers=headers_user)
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True

    # Attempt to mark someone else's notification returns 404
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    resp_other = client.put(f"/api/v1/notifications/{notif.id}/read", headers=headers_admin)
    assert resp_other.status_code == 404


# 7. Mark All Notifications as Read
def test_mark_all_notifications_as_read(
    client: TestClient, db_session: Session, test_user: User, user_token: str
):
    """User can mark all unread notifications as read at once."""
    for i in range(3):
        notification_service.create(
            db=db_session,
            notification_in=NotificationCreate(
                user_id=test_user.id,
                title=f"Bulk Notice {i}",
                message=f"Message body {i}",
                type=NotificationType.INFO,
            ),
        )

    headers = {"Authorization": f"Bearer {user_token}"}
    resp = client.put("/api/v1/notifications/read-all", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["count"] >= 3

    # Verify unread list is now empty
    resp_unread = client.get("/api/v1/notifications/?unread_only=true", headers=headers)
    assert resp_unread.status_code == 200
    assert len(resp_unread.json()) == 0


# 8. Unread Notifications Filter
def test_unread_notifications_filter(
    client: TestClient, db_session: Session, test_user: User, user_token: str
):
    """Filtering notifications by unread_only=true returns only unread items."""
    # Ensure all existing are read
    notification_service.mark_all_as_read(db=db_session, user_id=test_user.id)

    # Create 1 new unread notification
    new_notif = notification_service.create(
        db=db_session,
        notification_in=NotificationCreate(
            user_id=test_user.id,
            title="Fresh Unread Notification",
            message="Unread content",
            type=NotificationType.INFO,
        ),
    )

    headers = {"Authorization": f"Bearer {user_token}"}
    resp = client.get("/api/v1/notifications/?unread_only=true", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == new_notif.id
    assert data[0]["is_read"] is False


# 9. Admin Analytics Authentication
def test_admin_analytics_authentication(client: TestClient):
    """GET /api/v1/admin/analytics requires authentication."""
    resp = client.get("/api/v1/admin/analytics")
    assert resp.status_code == 401


# 10. Admin Analytics RBAC Enforcement
def test_admin_analytics_rbac_enforcement(
    client: TestClient, user_token: str, admin_token: str
):
    """Regular user receives 403 Forbidden; Admin user receives 200 OK."""
    headers_user = {"Authorization": f"Bearer {user_token}"}
    resp_user = client.get("/api/v1/admin/analytics", headers=headers_user)
    assert resp_user.status_code == 403

    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    resp_admin = client.get("/api/v1/admin/analytics", headers=headers_admin)
    assert resp_admin.status_code == 200
    data = resp_admin.json()
    assert "total_users" in data
    assert "lost_vs_found_distribution" in data


# 11. Analytics Period Filtering
def test_analytics_period_filtering(client: TestClient, admin_token: str):
    """Admin analytics supports 7d, 30d, 90d periods and rejects invalid horizons."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    for p in ["7d", "30d", "90d"]:
        resp = client.get(f"/api/v1/admin/analytics?period={p}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["period"] == p

    # Invalid period returns 422
    resp_bad = client.get("/api/v1/admin/analytics?period=invalid_horizon", headers=headers)
    assert resp_bad.status_code == 422


# 12. Analytics Aggregation Accuracy
def test_analytics_aggregation_accuracy(
    client: TestClient, db_session: Session, test_admin: User, admin_token: str
):
    """Analytics accurately aggregates categories, locations, and time trends from DB."""
    now = datetime.now(timezone.utc)
    item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Analytics Test Backpack",
            description="Durable North Face black backpack.",
            category="Bags",
            location="Student Center",
            incident_date=now,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_admin.id,
    )

    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/api/v1/admin/analytics?period=7d", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_lost_reports"] >= 1
    assert data["lost_vs_found_distribution"]["lost"] >= 1
    assert any(c["category"] == "Bags" for c in data["reports_by_category"])
    assert any(l["location"] == "Student Center" for l in data["reports_by_location"])
    assert len(data["reports_over_time"]) >= 1


# 13. No Sensitive Credentials Leakage
def test_no_sensitive_credentials_in_analytics(
    client: TestClient, admin_token: str
):
    """Analytics responses never contain passwords, password hashes, or token secrets."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/api/v1/admin/analytics", headers=headers)
    assert resp.status_code == 200
    raw_text = resp.text.lower()
    assert "password_hash" not in raw_text
    assert "jwt_secret" not in raw_text
    assert "secret_key" not in raw_text


# 14. Invalid Custom Date Range Returns 422
def test_invalid_date_range_returns_422(
    client: TestClient, admin_token: str
):
    """When from_date is after to_date, returns 422 Unprocessable Entity."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    from_date = (datetime.now(timezone.utc)).isoformat()
    to_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()

    resp = client.get(
        "/api/v1/admin/analytics",
        params={"period": "custom", "from_date": from_date, "to_date": to_date},
        headers=headers,
    )
    assert resp.status_code == 422
    assert "from_date cannot be after to_date" in resp.json()["detail"]
