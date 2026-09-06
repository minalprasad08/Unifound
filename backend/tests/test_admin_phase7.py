import pytest
from starlette.testclient import TestClient


def test_admin_stats_authorized(client: TestClient, admin_headers: dict):
    """Administrator can successfully fetch system stats."""
    resp = client.get("/admin/stats", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_users" in data
    assert "total_items" in data
    assert "items_by_type" in data
    assert "LOST" in data["items_by_type"]
    assert "FOUND" in data["items_by_type"]
    assert "items_by_status" in data
    assert "OPEN" in data["items_by_status"]
    assert "pending_claims" in data
    assert "total_claims" in data
    assert isinstance(data["recent_activity"], list)


def test_regular_user_blocked_from_admin_stats(client: TestClient, user_headers: dict):
    """Standard user is blocked from /admin/stats with 403."""
    resp = client.get("/admin/stats", headers=user_headers)
    assert resp.status_code == 403


def test_unauthenticated_blocked_from_admin_stats(client: TestClient):
    """Unauthenticated visitor is blocked from /admin/stats with 401."""
    resp = client.get("/admin/stats")
    assert resp.status_code == 401
