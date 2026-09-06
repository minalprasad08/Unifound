import io
import os
import pytest
from datetime import datetime, timezone, timedelta
from PIL import Image as PILImage
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.item import Item, ItemType, ItemStatus
from app.models.user import User, UserRole
from app.schemas.item import ItemReportCreate
from app.services.item_service import item_service
from app.services.image_analysis_service import image_analysis_service, LocalImageAnalyzer, ImageAnalyzer
from app.services.matching_service import matching_service


@pytest.fixture
def sample_image_path(tmp_path):
    """Generate a valid test image with distinctive blue and black colors."""
    img = PILImage.new("RGB", (200, 200), color=(35, 90, 205))
    # Draw some black pixels
    for x in range(50):
        for y in range(50):
            img.putpixel((x, y), (25, 25, 25))

    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
    os.makedirs(uploads_dir, exist_ok=True)
    file_path = os.path.join(uploads_dir, "test_phase9_sample.jpg")
    img.save(file_path, "JPEG")
    return "/uploads/test_phase9_sample.jpg"


def test_successful_image_analysis_and_structure(
    client: TestClient, db_session: Session, test_user: User, user_headers: dict, sample_image_path: str
):
    """Owner can trigger image analysis and receive structured visual attributes."""
    # 1. Create item with image
    item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Dell USB-C Laptop Charger",
            description="Black Dell 65W charger with blue power indicator ring.",
            category="Electronics",
            location="Library 2nd Floor",
            incident_date=datetime.now(timezone.utc),
            image_url=sample_image_path,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    # 2. Call POST /items/{id}/analyze-image
    resp = client.post(f"/items/{item.id}/analyze-image", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["item_id"] == item.id
    assert data["image_url"] == sample_image_path

    analysis = data["image_analysis"]
    assert analysis["item_type"] == "laptop charger"
    assert "blue" in analysis["colors"]
    assert analysis["brand"] == "Dell"
    assert "Dell" in analysis["visible_text"]
    assert isinstance(analysis["characteristics"], list)
    assert 0.60 <= analysis["confidence"] <= 1.0
    assert analysis["analyzer"] == "local-vision-v1"
    assert "analyzed_at" in analysis

    # Verify persistence in database
    db_session.refresh(item)
    assert item.image_analysis is not None
    assert item.image_analysis["item_type"] == "laptop charger"
    assert item.image_analysis["brand"] == "Dell"


def test_missing_image_returns_400(
    client: TestClient, db_session: Session, test_user: User, user_headers: dict
):
    """Triggering analysis on an item without an image returns 400."""
    item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="House Keys",
            description="Keys with brass keychain.",
            category="Keys",
            location="Student Center",
            incident_date=datetime.now(timezone.utc),
            image_url=None,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    resp = client.post(f"/items/{item.id}/analyze-image", headers=user_headers)
    assert resp.status_code == 400
    assert "does not contain an associated image" in resp.json()["detail"]


def test_nonexistent_item_returns_404(client: TestClient, user_headers: dict):
    """Triggering analysis on nonexistent item returns 404."""
    resp = client.post("/items/999999/analyze-image", headers=user_headers)
    assert resp.status_code == 404


def test_unauthenticated_request_returns_401(client: TestClient):
    """Unauthenticated request returns 401."""
    resp = client.post("/items/1/analyze-image")
    assert resp.status_code == 401


def test_non_owner_blocked_from_analysis_returns_403(
    client: TestClient, db_session: Session, test_admin: User, user_headers: dict, sample_image_path: str
):
    """Non-owner regular user cannot analyze another user's item."""
    # Item owned by admin
    item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Hydro Flask Bottle",
            description="Navy blue insulated flask.",
            category="Accessories",
            location="Gym",
            incident_date=datetime.now(timezone.utc),
            image_url=sample_image_path,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_admin.id,
    )

    # Regular user tries to analyze admin's item
    resp = client.post(f"/items/{item.id}/analyze-image", headers=user_headers)
    assert resp.status_code == 403
    assert "not authorized" in resp.json()["detail"]


def test_admin_can_analyze_any_item(
    client: TestClient, db_session: Session, test_user: User, admin_headers: dict, sample_image_path: str
):
    """Admin user can trigger image analysis on any user's item."""
    item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Scientific Calculator TI-84",
            description="Black Texas Instruments calculator.",
            category="Electronics",
            location="Math Hall 105",
            incident_date=datetime.now(timezone.utc),
            image_url=sample_image_path,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    resp = client.post(f"/items/{item.id}/analyze-image", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["image_analysis"]["item_type"] == "calculator"


def test_missing_image_file_on_disk_handled_gracefully(
    client: TestClient, db_session: Session, test_user: User, user_headers: dict
):
    """If image file is deleted from disk, API returns 422 and item remains intact."""
    item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Lost Flash Drive",
            description="USB flash drive.",
            category="Electronics",
            location="Lab 101",
            incident_date=datetime.now(timezone.utc),
            image_url="/uploads/nonexistent_file_xyz_123.jpg",
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    resp = client.post(f"/items/{item.id}/analyze-image", headers=user_headers)
    assert resp.status_code == 422
    assert "missing" in resp.json()["detail"].lower() or "failed" in resp.json()["detail"].lower()

    # Item still exists and is untouched
    db_session.refresh(item)
    assert item.id is not None
    assert item.status == ItemStatus.OPEN


def test_matching_with_visual_similarity_boost(
    client: TestClient, db_session: Session, test_user: User, user_headers: dict
):
    """When both items possess image analysis, visual similarity score is calculated (10% weight)."""
    now = datetime.now(timezone.utc)

    # 1. Create LOST item with image analysis
    lost = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Dell 65W Laptop Charger",
            description="Black charger cord with USB-C connector.",
            category="Electronics",
            location="Science Hall",
            incident_date=now,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )
    lost.image_analysis = {
        "item_type": "laptop charger",
        "colors": ["black", "blue"],
        "brand": "Dell",
        "visible_text": ["Dell"],
        "characteristics": ["USB-C connector"],
        "confidence": 0.90,
        "analyzer": "local-vision-v1",
        "analyzed_at": now.isoformat(),
    }
    db_session.commit()

    # 2. Create FOUND item with matching image analysis
    found = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Dell USB-C Charger",
            description="Found black Dell laptop power adapter.",
            category="Electronics",
            location="Science Hall Room 201",
            incident_date=now,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )
    found.image_analysis = {
        "item_type": "laptop charger",
        "colors": ["black", "blue"],
        "brand": "Dell",
        "visible_text": ["Dell"],
        "characteristics": ["USB-C connector"],
        "confidence": 0.92,
        "analyzer": "local-vision-v1",
        "analyzed_at": now.isoformat(),
    }
    db_session.commit()

    # Query matches
    resp = client.get(f"/matches/item/{lost.id}", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["matches"]) >= 1

    top = data["matches"][0]
    assert top["visual_score"] is not None
    assert top["visual_score"] >= 0.80
    assert len(top["visual_evidence"]) > 0
    assert "Same item type" in top["visual_evidence"] or "Matching brand" in top["visual_evidence"]


def test_matching_without_visual_attributes_falls_back_to_phase8(
    client: TestClient, db_session: Session, test_user: User, user_headers: dict
):
    """When either item lacks image analysis, visual_score is None and Phase 8 score is unchanged."""
    now = datetime.now(timezone.utc)

    lost = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Wireless Mouse Logitech",
            description="Black bluetooth optical mouse.",
            category="Electronics",
            location="Library Desk 4",
            incident_date=now,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )
    # No image analysis on lost item

    found = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Logitech Wireless Mouse",
            description="Black compact optical mouse.",
            category="Electronics",
            location="Library 2nd Floor",
            incident_date=now,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )
    # Image analysis on found item only
    found.image_analysis = {
        "item_type": "mouse",
        "colors": ["black"],
        "brand": "Logitech",
        "visible_text": ["Logitech"],
        "characteristics": [],
        "confidence": 0.88,
        "analyzer": "local-vision-v1",
        "analyzed_at": now.isoformat(),
    }
    db_session.commit()

    resp = client.get(f"/matches/item/{lost.id}", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["matches"]) >= 1

    top = data["matches"][0]
    assert top["visual_score"] is None
    assert top["visual_evidence"] == []
    assert top["confidence"] > 70.0


def test_custom_analyzer_provider_abstraction():
    """Verify ImageAnalyzer provider abstraction works with custom mock implementation."""
    class CustomMockAnalyzer(ImageAnalyzer):
        def analyze(self, image_path: str, context=None):
            return {
                "item_type": "water bottle",
                "colors": ["green", "silver"],
                "brand": "Stanley",
                "visible_text": ["Stanley"],
                "characteristics": ["vacuum insulated"],
                "confidence": 0.95,
                "analyzer": "custom-mock-v1",
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
            }

    service = image_analysis_service.__class__(analyzer=CustomMockAnalyzer())
    result = service.analyzer.analyze("fake_path.jpg")
    assert result["item_type"] == "water bottle"
    assert result["brand"] == "Stanley"
    assert result["analyzer"] == "custom-mock-v1"
