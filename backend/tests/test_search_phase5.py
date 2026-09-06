from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.item import Item, ItemType, ItemStatus
from app.core.security import get_password_hash


@pytest.fixture
def seed_search_items(db_session: Session, test_user: User):
    """Seed test dataset for search queries."""
    now = datetime.now(timezone.utc)
    items = [
        Item(
            title="Red Calculus Textbook",
            description="Stewart Calculus 8th edition with notes inside.",
            category="Books",
            location="Main Library 2nd Floor",
            incident_date=now - timedelta(days=5),
            item_type=ItemType.LOST,
            status=ItemStatus.OPEN,
            reported_by=test_user.id,
        ),
        Item(
            title="Black Waterproof Jacket",
            description="North Face rain jacket with hood left in gym.",
            category="Clothing",
            location="Campus Recreation Gym Locker Room",
            incident_date=now - timedelta(days=4),
            item_type=ItemType.LOST,
            status=ItemStatus.OPEN,
            reported_by=test_user.id,
        ),
        Item(
            title="Silver MacBook Pro 14",
            description="Apple laptop with university computer science department sticker.",
            category="Electronics",
            location="Engineering Hall 301",
            incident_date=now - timedelta(days=3),
            item_type=ItemType.FOUND,
            status=ItemStatus.OPEN,
            reported_by=test_user.id,
        ),
        Item(
            title="Hydro Flask Water Bottle",
            description="Blue 32oz bottle found under table.",
            category="Accessories",
            location="Student Union Cafeteria",
            incident_date=now - timedelta(days=2),
            item_type=ItemType.FOUND,
            status=ItemStatus.CLOSED,
            reported_by=test_user.id,
        ),
        Item(
            title="Sony Wireless Headphones",
            description="WH-1000XM4 black noise canceling headphones.",
            category="Electronics",
            location="Main Library Quiet Study Area",
            incident_date=now - timedelta(days=1),
            item_type=ItemType.LOST,
            status=ItemStatus.OPEN,
            reported_by=test_user.id,
        ),
    ]
    for item in items:
        db_session.add(item)
    db_session.commit()
    return items


def test_search_keyword_title_and_description(
    client: TestClient, user_headers: dict, seed_search_items
):
    # 1. Match in title ("Calculus")
    resp1 = client.get("/items/search?q=Calculus", headers=user_headers)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["total"] == 1
    assert data1["items"][0]["title"] == "Red Calculus Textbook"

    # 2. Match in description ("waterproof")
    resp2 = client.get("/items/search?q=waterproof", headers=user_headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["total"] == 1
    assert data2["items"][0]["title"] == "Black Waterproof Jacket"


def test_search_filter_by_item_type(
    client: TestClient, user_headers: dict, seed_search_items
):
    # Filter LOST items
    resp_lost = client.get("/items/search?item_type=LOST", headers=user_headers)
    assert resp_lost.status_code == 200
    data_lost = resp_lost.json()
    assert data_lost["total"] >= 3
    for item in data_lost["items"]:
        assert item["item_type"] == "LOST"

    # Filter FOUND items
    resp_found = client.get("/items/search?item_type=FOUND", headers=user_headers)
    assert resp_found.status_code == 200
    data_found = resp_found.json()
    assert data_found["total"] >= 2
    for item in data_found["items"]:
        assert item["item_type"] == "FOUND"


def test_search_filter_by_category(
    client: TestClient, user_headers: dict, seed_search_items
):
    resp = client.get("/items/search?category=Electronics", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    for item in data["items"]:
        assert item["category"] == "Electronics"


def test_search_filter_by_location(
    client: TestClient, user_headers: dict, seed_search_items
):
    resp = client.get("/items/search?location=Library", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    for item in data["items"]:
        assert "Library" in item["location"]


def test_search_filter_by_status(
    client: TestClient, user_headers: dict, seed_search_items
):
    resp = client.get("/items/search?status=CLOSED", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "CLOSED"


def test_search_filter_by_date_range(
    client: TestClient, user_headers: dict, seed_search_items
):
    now = datetime.now(timezone.utc)
    from_date = (now - timedelta(days=4, hours=12)).isoformat()
    to_date = (now - timedelta(days=2, hours=12)).isoformat()

    resp = client.get(
        "/items/search",
        params={"from_date": from_date, "to_date": to_date},
        headers=user_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    # Should include day -4 (Jacket) and day -3 (MacBook)
    assert data["total"] == 2


def test_search_combined_filters(
    client: TestClient, user_headers: dict, seed_search_items
):
    resp = client.get(
        "/items/search?item_type=LOST&category=Electronics&location=Library",
        headers=user_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Sony Wireless Headphones"


def test_search_sorting(client: TestClient, user_headers: dict, seed_search_items):
    # Sort by incident_date asc
    resp_asc = client.get(
        "/items/search?sort_by=incident_date&sort_order=asc",
        headers=user_headers,
    )
    assert resp_asc.status_code == 200
    items_asc = resp_asc.json()["items"]
    # First item should be oldest incident date (Calculus Textbook)
    assert items_asc[0]["title"] == "Red Calculus Textbook"

    # Sort by incident_date desc
    resp_desc = client.get(
        "/items/search?sort_by=incident_date&sort_order=desc",
        headers=user_headers,
    )
    assert resp_desc.status_code == 200
    items_desc = resp_desc.json()["items"]
    # First item should be most recent incident date (Sony Headphones)
    assert items_desc[0]["title"] == "Sony Wireless Headphones"


def test_search_pagination(client: TestClient, user_headers: dict, seed_search_items):
    # Page 1 with page_size=2
    resp1 = client.get("/items/search?page=1&page_size=2", headers=user_headers)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["page"] == 1
    assert data1["page_size"] == 2
    assert len(data1["items"]) == 2
    assert data1["total"] >= 5
    assert data1["total_pages"] >= 3

    # Page 2 with page_size=2
    resp2 = client.get("/items/search?page=2&page_size=2", headers=user_headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["page"] == 2
    assert len(data2["items"]) == 2
    # Distinct items between page 1 and page 2
    page1_ids = {i["id"] for i in data1["items"]}
    page2_ids = {i["id"] for i in data2["items"]}
    assert not page1_ids.intersection(page2_ids)


def test_search_empty_results(client: TestClient, user_headers: dict):
    resp = client.get("/items/search?q=NonExistentSuperUnlikelyQuery999", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []
    assert data["total_pages"] == 0


def test_search_invalid_parameters_return_422(client: TestClient, user_headers: dict):
    # Page size exceeds max 100
    assert client.get("/items/search?page_size=101", headers=user_headers).status_code == 422

    # Page < 1
    assert client.get("/items/search?page=0", headers=user_headers).status_code == 422

    # Invalid sort field
    assert client.get("/items/search?sort_by=hacked_column", headers=user_headers).status_code == 422

    # Invalid sort order
    assert client.get("/items/search?sort_order=sideways", headers=user_headers).status_code == 422

    # from_date after to_date
    now = datetime.now(timezone.utc)
    from_d = now.isoformat()
    to_d = (now - timedelta(days=1)).isoformat()
    resp = client.get(
        "/items/search",
        params={"from_date": from_d, "to_date": to_d},
        headers=user_headers,
    )
    assert resp.status_code == 422
    assert "from_date cannot be after to_date" in resp.json()["detail"]


def test_search_unauthenticated_returns_401(client: TestClient):
    resp = client.get("/items/search?q=test")
    assert resp.status_code == 401


def test_search_sql_injection_safe(client: TestClient, user_headers: dict, seed_search_items):
    # SQL injection payload in keyword
    payload = "' OR 1=1; --"
    resp = client.get(f"/items/search?q={payload}", headers=user_headers)
    assert resp.status_code == 200
    # Parameterized query treats it as literal string, matching 0 items
    assert resp.json()["total"] == 0
