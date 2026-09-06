from datetime import datetime, timezone, timedelta
import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.item import Item, ItemType, ItemStatus
from app.models.user import User
from app.schemas.item import ItemReportCreate
from app.services.item_service import item_service
from app.services.matching_service import matching_service, MatchingWeights


def test_matching_lost_to_found_and_confidence(
    client: TestClient, db_session: Session, test_user: User, user_headers: dict
):
    """LOST item correctly matches candidate FOUND items and calculates confidence."""
    now = datetime.now(timezone.utc)

    # 1. Create a LOST item
    lost_item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Black Leather Bifold Wallet",
            description="Lost my black leather wallet containing campus student ID and debit cards.",
            category="Wallets",
            location="University Library 2nd Floor",
            incident_date=now - timedelta(hours=2),
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    # 2. Create matching FOUND item
    found_match = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Black Bifold Leather Wallet",
            description="Found a black leather wallet on 2nd floor library study desk with student cards.",
            category="Wallets",
            location="Library 2nd Floor Desk",
            incident_date=now - timedelta(hours=1),
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )

    # 3. Create distant / low match FOUND item
    found_unrelated = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Red Sports Water Bottle",
            description="Red metal hydro flask found in gym locker room.",
            category="Sporting Goods",
            location="Campus Gymnasium",
            incident_date=now - timedelta(days=25),
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )

    # Query matches for the lost item
    resp = client.get(f"/matches/item/{lost_item.id}", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["source_item_id"] == lost_item.id
    assert data["source_item_type"] == "LOST"
    assert data["total"] >= 1

    matches = data["matches"]
    assert len(matches) >= 1

    # First match should be the highly correlated wallet
    top_match = matches[0]
    assert top_match["item"]["id"] == found_match.id
    assert top_match["confidence"] > 70.0
    assert 0.0 <= top_match["confidence"] <= 100.0
    assert 0.0 <= top_match["title_score"] <= 1.0
    assert 0.0 <= top_match["description_score"] <= 1.0
    assert top_match["category_score"] == 1.0
    assert 0.0 <= top_match["location_score"] <= 1.0
    assert 0.0 <= top_match["date_score"] <= 1.0
    assert len(top_match["explanation"]) > 0


def test_matching_found_to_lost_bidirectional(
    client: TestClient, db_session: Session, test_user: User, user_headers: dict
):
    """FOUND item matches candidate LOST items."""
    now = datetime.now(timezone.utc)

    lost = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Sony WH-1000XM4 Headphones",
            description="Black wireless noise cancelling headphones in grey travel case.",
            category="Electronics",
            location="Engineering Center Room 102",
            incident_date=now - timedelta(days=1),
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    found = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Sony Wireless Headphones Black",
            description="Found Sony noise cancelling headset in grey protective pouch.",
            category="Electronics",
            location="Engineering Building Lab 102",
            incident_date=now,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )

    resp = client.get(f"/matches/item/{found.id}", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["source_item_id"] == found.id
    assert data["source_item_type"] == "FOUND"

    match_ids = [m["item"]["id"] for m in data["matches"]]
    assert lost.id in match_ids


def test_excludes_same_item_type_and_self(
    client: TestClient, db_session: Session, test_user: User, user_headers: dict
):
    """Matches never include items of the same type (LOST-LOST or FOUND-FOUND) or itself."""
    now = datetime.now(timezone.utc)

    lost1 = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Calculus Textbook 9th Edition",
            description="Stewart Calculus Early Transcendentals hardcover book.",
            category="Books",
            location="Student Union",
            incident_date=now,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    # Another LOST item with almost identical content
    lost2 = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Calculus Textbook Stewart",
            description="Stewart Calculus book 9th edition lost in Student Union.",
            category="Books",
            location="Student Union Lounge",
            incident_date=now,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    resp = client.get(f"/matches/item/{lost1.id}", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()

    match_ids = [m["item"]["id"] for m in data["matches"]]
    assert lost1.id not in match_ids, "Should not match itself"
    assert lost2.id not in match_ids, "Should not match another LOST item"


def test_excludes_closed_and_resolved_items(
    client: TestClient, db_session: Session, test_user: User, user_headers: dict
):
    """Items marked CLOSED or RESOLVED must not be returned as candidate matches."""
    now = datetime.now(timezone.utc)

    lost = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Car Keys with Honda Fob",
            description="Set of keys with silver Honda remote and blue lanyard.",
            category="Keys",
            location="North Parking Garage",
            incident_date=now,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    # Found item that is CLOSED
    found_closed = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Honda Car Key Fob",
            description="Honda car key found in North Parking Lot.",
            category="Keys",
            location="North Parking Lot",
            incident_date=now,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )
    found_closed.status = ItemStatus.CLOSED
    db_session.commit()

    # Found item that is RESOLVED
    found_resolved = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Honda Keys on Blue Lanyard",
            description="Keys with Honda logo and lanyard.",
            category="Keys",
            location="North Parking Garage Level 2",
            incident_date=now,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )
    found_resolved.status = ItemStatus.RESOLVED
    db_session.commit()

    resp = client.get(f"/matches/item/{lost.id}", headers=user_headers)
    assert resp.status_code == 200
    match_ids = [m["item"]["id"] for m in resp.json()["matches"]]

    assert found_closed.id not in match_ids
    assert found_resolved.id not in match_ids


def test_matching_ranking_and_deterministic_order(
    client: TestClient, db_session: Session, test_user: User, user_headers: dict
):
    """Results are strictly ranked descending by confidence and deterministic."""
    now = datetime.now(timezone.utc)

    lost = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="MacBook Air M2 Silver",
            description="Silver 13-inch MacBook Air with sticker on lid.",
            category="Electronics",
            location="Science Center Room 204",
            incident_date=now,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    # Exact match
    found_high = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Apple MacBook Air M2 Silver",
            description="Found silver Apple MacBook Air 13-inch laptop in Science Center.",
            category="Electronics",
            location="Science Center 204",
            incident_date=now,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )

    # Moderate match
    found_med = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Silver Laptop Computer",
            description="Generic silver laptop charger and device found on campus.",
            category="Electronics",
            location="Campus Dining Hall",
            incident_date=now - timedelta(days=10),
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )

    resp1 = client.get(f"/matches/item/{lost.id}", headers=user_headers)
    assert resp1.status_code == 200
    matches1 = resp1.json()["matches"]

    # Verify descending order
    confidences = [m["confidence"] for m in matches1]
    assert confidences == sorted(confidences, reverse=True)

    # Verify highest match is the MacBook
    assert matches1[0]["item"]["id"] == found_high.id

    # Verify deterministic behavior (repeat query returns exact same results)
    resp2 = client.get(f"/matches/item/{lost.id}", headers=user_headers)
    matches2 = resp2.json()["matches"]
    assert [m["confidence"] for m in matches1] == [m["confidence"] for m in matches2]
    assert [m["item"]["id"] for m in matches1] == [m["item"]["id"] for m in matches2]


def test_min_confidence_filter_and_pagination(
    client: TestClient, db_session: Session, test_user: User, user_headers: dict
):
    """Filters matches by min_confidence and supports pagination."""
    now = datetime.now(timezone.utc)

    lost = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Ray-Ban Aviator Sunglasses Gold",
            description="Gold metal framed Ray-Ban aviator sunglasses in brown leather case.",
            category="Accessories",
            location="Campus Quad Lawn",
            incident_date=now,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    # High match
    item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Ray-Ban Sunglasses Aviators",
            description="Found gold frame Ray-Ban sunglasses in brown case on quad.",
            category="Accessories",
            location="Quad Lawn Bench",
            incident_date=now,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )

    # Unrelated item with very low confidence
    item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Green Umbrella",
            description="Small umbrella found in restroom.",
            category="Other",
            location="Basement Restroom",
            incident_date=now - timedelta(days=40),
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )

    # Query with min_confidence=60.0
    resp_filtered = client.get(f"/matches/item/{lost.id}?min_confidence=60.0", headers=user_headers)
    assert resp_filtered.status_code == 200
    filtered_matches = resp_filtered.json()["matches"]
    for m in filtered_matches:
        assert m["confidence"] >= 60.0

    # Query with pagination
    resp_paged = client.get(f"/matches/item/{lost.id}?page=1&page_size=1", headers=user_headers)
    assert resp_paged.status_code == 200
    assert len(resp_paged.json()["matches"]) <= 1
    assert resp_paged.json()["page_size"] == 1


def test_date_proximity_and_feature_components():
    """Unit test matching_service feature calculators."""
    dt_now = datetime.now(timezone.utc)

    # 1. Date proximity decay
    score_same_day = matching_service.compute_date_proximity(dt_now, dt_now)
    score_3_days = matching_service.compute_date_proximity(dt_now, dt_now - timedelta(days=3))
    score_30_days = matching_service.compute_date_proximity(dt_now, dt_now - timedelta(days=30))

    assert score_same_day == 1.0
    assert score_same_day > score_3_days > score_30_days > 0.0

    # 2. Category matching
    assert matching_service.compute_category_similarity("Electronics", "electronics") == 1.0
    assert matching_service.compute_category_similarity("Electronics", "Books") == 0.0

    # 3. Location matching
    loc_identical = matching_service.compute_location_similarity("Main Library 2nd Floor", "Main Library 2nd Floor")
    loc_similar = matching_service.compute_location_similarity("Main Library Floor 2", "Library 2nd Floor")
    loc_diff = matching_service.compute_location_similarity("Main Library", "Sports Complex Gym")
    assert loc_identical == 1.0
    assert loc_similar > loc_diff

    # 4. Title similarity
    title_high = matching_service.compute_title_similarity("Dell Inspiron Laptop", "Dell Inspiron 15 Laptop")
    title_low = matching_service.compute_title_similarity("Dell Inspiron Laptop", "Red Silk Scarf")
    assert title_high > title_low


def test_unauthorized_and_invalid_item_id(client: TestClient, user_headers: dict):
    """Handles 401 unauthenticated and 404 for nonexistent items."""
    # 401 when no JWT
    resp_unauth = client.get("/matches/item/999999")
    assert resp_unauth.status_code == 401

    # 404 when item does not exist
    resp_notfound = client.get("/matches/item/999999", headers=user_headers)
    assert resp_notfound.status_code == 404


def test_item_creation_succeeds_even_if_matching_fails(
    db_session: Session, test_user: User, monkeypatch
):
    """Graceful degradation: item creation succeeds even if matching service raises an error."""
    def broken_find_matches(*args, **kwargs):
        raise RuntimeError("Simulated ML engine crash")

    monkeypatch.setattr(matching_service, "find_matches", broken_find_matches)

    # Item creation must still succeed and return created item
    item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Stainless Steel Watch",
            description="Fossil silver chronograph watch.",
            category="Jewelry",
            location="Dining Center",
            incident_date=datetime.now(timezone.utc),
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )
    assert item.id is not None
    assert item.title == "Stainless Steel Watch"
