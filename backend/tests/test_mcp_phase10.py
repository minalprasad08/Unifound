import os
import pytest
from datetime import datetime, timezone, timedelta
from PIL import Image as PILImage
from sqlalchemy.orm import Session
from app.models.item import Item, ItemType, ItemStatus
from app.models.user import User, UserRole
from app.schemas.item import ItemReportCreate
from app.services.item_service import item_service
from app.mcp.context import MCPAuthContext
from app.mcp.client import UniFoundMCPClient, MCPToolNotFoundError, MCPTimeoutError
from app.mcp.server import create_mcp_server, get_mcp_server


@pytest.fixture
def mcp_client(db_session: Session):
    """Create an MCP client instance connected to the UniFound MCP server."""
    return UniFoundMCPClient(server=create_mcp_server(), db_session=db_session)


@pytest.fixture
def user_mcp_context(test_user: User) -> MCPAuthContext:
    return MCPAuthContext(
        user_id=test_user.id,
        email=test_user.email,
        role=test_user.role,
        is_active=test_user.is_active,
        full_name=test_user.full_name,
    )


@pytest.fixture
def admin_mcp_context(test_admin: User) -> MCPAuthContext:
    return MCPAuthContext(
        user_id=test_admin.id,
        email=test_admin.email,
        role=test_admin.role,
        is_active=test_admin.is_active,
        full_name=test_admin.full_name,
    )


@pytest.fixture
def sample_image_path():
    img = PILImage.new("RGB", (150, 150), color=(30, 80, 200))
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
    os.makedirs(uploads_dir, exist_ok=True)
    file_path = os.path.join(uploads_dir, "test_phase10_sample.jpg")
    img.save(file_path, "JPEG")
    return "/uploads/test_phase10_sample.jpg"


@pytest.mark.anyio
async def test_mcp_server_metadata_and_dynamic_discovery(mcp_client: UniFoundMCPClient):
    """MCP server reports correct metadata and dynamic tools/list returns all 6 tools."""
    await mcp_client.connect()
    assert mcp_client.is_connected

    # Verify server metadata
    server = mcp_client.server
    assert server.name == "unifound"
    assert "UniFound" in server.instructions

    # Dynamic tool discovery (tools/list)
    tools = await mcp_client.list_tools()
    assert len(tools) == 6

    tool_names = [t["name"] for t in tools]
    expected_tools = [
        "search_items",
        "get_item",
        "find_matches",
        "analyze_image",
        "create_claim",
        "get_claim_status",
    ]
    for expected in expected_tools:
        assert expected in tool_names

    # Check input schemas exist and are typed
    for t in tools:
        assert "description" in t
        assert len(t["description"]) > 0
        assert "input_schema" in t
        assert t["input_schema"]["type"] == "object"
        assert "properties" in t["input_schema"]

    await mcp_client.disconnect()


@pytest.mark.anyio
async def test_mcp_unauthenticated_request_rejected(mcp_client: UniFoundMCPClient):
    """Tools reject unauthenticated requests with controlled AUTH_ERROR."""
    async with mcp_client:
        res = await mcp_client.call_tool("search_items", {"keyword": "laptop"})
        assert res.get("code") == "AUTH_ERROR"
        assert "Authentication required" in res.get("error", "")


@pytest.mark.anyio
async def test_mcp_search_items_tool(
    mcp_client: UniFoundMCPClient, db_session: Session, test_user: User, user_mcp_context: MCPAuthContext
):
    """search_items tool returns paginated search results via service layer."""
    now = datetime.now(timezone.utc)
    item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Black Dell Precision Laptop",
            description="Lost in campus library computer lounge.",
            category="Electronics",
            location="Library Lounge",
            incident_date=now,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    async with mcp_client:
        res = await mcp_client.call_tool(
            "search_items",
            {"keyword": "Dell Precision", "item_type": "LOST", "page": 1, "page_size": 5},
            auth_context=user_mcp_context,
        )

        assert "items" in res
        assert res["total"] >= 1
        assert res["page"] == 1
        found = False
        for it in res["items"]:
            if "Dell Precision" in it["title"]:
                found = True
                assert it["item_type"] == "LOST"
                assert it["category"] == "Electronics"
                # Ensure no sensitive database or internal columns are leaked
                assert "password" not in it
                assert "password_hash" not in it
        assert found


@pytest.mark.anyio
async def test_mcp_get_item_tool(
    mcp_client: UniFoundMCPClient, db_session: Session, test_user: User, user_mcp_context: MCPAuthContext
):
    """get_item tool retrieves item details safely."""
    item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Car Keys with Blue Tag",
            description="Honda car keys with a blue tag.",
            category="Keys",
            location="Parking Lot B",
            incident_date=datetime.now(timezone.utc),
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )

    async with mcp_client:
        res = await mcp_client.call_tool(
            "get_item",
            {"item_id": item.id},
            auth_context=user_mcp_context,
        )

        assert res.get("id") == item.id
        assert res.get("title") == "Car Keys with Blue Tag"
        assert res.get("status") == "OPEN"
        assert "password" not in res
        assert "password_hash" not in res


@pytest.mark.anyio
async def test_mcp_find_matches_tool(
    mcp_client: UniFoundMCPClient, db_session: Session, test_user: User, user_mcp_context: MCPAuthContext
):
    """find_matches tool returns scored match candidates between opposite types."""
    now = datetime.now(timezone.utc)
    lost = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Bose Noise Cancelling Headphones",
            description="Black over-ear wireless headphones.",
            category="Electronics",
            location="Campus Center",
            incident_date=now,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )
    found = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Bose Wireless Headphones Black",
            description="Found black Bose headphones in campus center.",
            category="Electronics",
            location="Campus Center Lounge",
            incident_date=now,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )

    async with mcp_client:
        res = await mcp_client.call_tool(
            "find_matches",
            {"item_id": lost.id, "min_confidence": 50.0},
            auth_context=user_mcp_context,
        )

        assert res.get("source_item_id") == lost.id
        assert "matches" in res
        assert len(res["matches"]) >= 1

        top_match = res["matches"][0]
        assert top_match["item_id"] == found.id
        assert top_match["confidence"] >= 50.0
        assert "explanation" in top_match


@pytest.mark.anyio
async def test_mcp_analyze_image_and_ownership_enforcement(
    mcp_client: UniFoundMCPClient,
    db_session: Session,
    test_user: User,
    test_admin: User,
    user_mcp_context: MCPAuthContext,
    admin_mcp_context: MCPAuthContext,
    sample_image_path: str,
):
    """analyze_image tool respects ownership: reporter or admin only."""
    # Item owned by test_user
    item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Dell USB-C Charger",
            description="Black Dell laptop adapter.",
            category="Electronics",
            location="Library",
            incident_date=datetime.now(timezone.utc),
            image_url=sample_image_path,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    async with mcp_client:
        # Owner can analyze
        res_owner = await mcp_client.call_tool(
            "analyze_image",
            {"item_id": item.id},
            auth_context=user_mcp_context,
        )
        assert "image_analysis" in res_owner
        assert res_owner["image_analysis"]["brand"] == "Dell"

        # Item owned by admin
        admin_item = item_service.create_report(
            db=db_session,
            report_in=ItemReportCreate(
                title="Apple AirPods Pro",
                description="White wireless earbuds.",
                category="Electronics",
                location="Gym",
                incident_date=datetime.now(timezone.utc),
                image_url=sample_image_path,
            ),
            item_type=ItemType.FOUND,
            reporter_id=test_admin.id,
        )

        # Normal user cannot analyze admin's item
        res_forbidden = await mcp_client.call_tool(
            "analyze_image",
            {"item_id": admin_item.id},
            auth_context=user_mcp_context,
        )
        assert res_forbidden.get("code") in ("HTTP_403", "AUTH_ERROR")

        # Admin can analyze any item
        res_admin = await mcp_client.call_tool(
            "analyze_image",
            {"item_id": admin_item.id},
            auth_context=admin_mcp_context,
        )
        assert "image_analysis" in res_admin


@pytest.mark.anyio
async def test_mcp_create_claim_and_identity_spoof_prevention(
    mcp_client: UniFoundMCPClient,
    db_session: Session,
    test_user: User,
    test_admin: User,
    user_mcp_context: MCPAuthContext,
):
    """create_claim tool securely derives claimant from context; claimant cannot be spoofed."""
    # Item reported by admin
    item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Scientific Calculator",
            description="Silver Casio graphing calculator.",
            category="Electronics",
            location="Science Hall",
            incident_date=datetime.now(timezone.utc),
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_admin.id,
    )

    async with mcp_client:
        # Create claim with authenticated user
        res = await mcp_client.call_tool(
            "create_claim",
            {
                "item_id": item.id,
                "description": "This is my Casio calculator lost during chemistry lab.",
                "evidence": "Engraved serial number on back casing.",
            },
            auth_context=user_mcp_context,
        )

        assert "claim_id" in res
        assert res["item_id"] == item.id
        # Claimant ID is strictly the authenticated test_user.id
        assert res["claimant_id"] == test_user.id
        assert res["status"] == "PENDING"


@pytest.mark.anyio
async def test_mcp_get_claim_status_tool(
    mcp_client: UniFoundMCPClient,
    db_session: Session,
    test_user: User,
    test_admin: User,
    user_mcp_context: MCPAuthContext,
    admin_mcp_context: MCPAuthContext,
):
    """get_claim_status tool returns claim details only for authorized parties."""
    # Item by admin
    item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Leather Cardholder",
            description="Brown cardholder with student ID.",
            category="Wallets",
            location="Cafeteria",
            incident_date=datetime.now(timezone.utc),
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_admin.id,
    )

    async with mcp_client:
        # Submit claim by user
        claim_res = await mcp_client.call_tool(
            "create_claim",
            {
                "item_id": item.id,
                "description": "Lost my brown cardholder with my campus badge.",
            },
            auth_context=user_mcp_context,
        )
        claim_id = claim_res["claim_id"]

        # Claimant can view status
        status_res = await mcp_client.call_tool(
            "get_claim_status",
            {"claim_id": claim_id},
            auth_context=user_mcp_context,
        )
        assert status_res.get("claim_id") == claim_id
        assert status_res.get("status") == "PENDING"

        # Admin can view status
        admin_status_res = await mcp_client.call_tool(
            "get_claim_status",
            {"claim_id": claim_id},
            auth_context=admin_mcp_context,
        )
        assert admin_status_res.get("claim_id") == claim_id


@pytest.mark.anyio
async def test_mcp_error_handling_and_missing_resources(
    mcp_client: UniFoundMCPClient, user_mcp_context: MCPAuthContext
):
    """Handles missing resources and invalid tool names gracefully."""
    async with mcp_client:
        # Missing item
        res_item = await mcp_client.call_tool(
            "get_item",
            {"item_id": 999999},
            auth_context=user_mcp_context,
        )
        assert res_item.get("code") == "ITEM_NOT_FOUND"

        # Missing claim
        res_claim = await mcp_client.call_tool(
            "get_claim_status",
            {"claim_id": 999999},
            auth_context=user_mcp_context,
        )
        assert res_claim.get("code") == "CLAIM_NOT_FOUND"

        # Nonexistent tool raises MCPToolNotFoundError
        with pytest.raises(MCPToolNotFoundError):
            await mcp_client.call_tool("nonexistent_tool", {})


@pytest.mark.anyio
async def test_mcp_client_timeout_handling(db_session: Session, user_mcp_context: MCPAuthContext):
    """MCP client enforces configurable request timeout."""
    # Client configured with 0 second timeout triggers MCPTimeoutError
    client = UniFoundMCPClient(server=create_mcp_server(), timeout=0, db_session=db_session)
    async with client:
        with pytest.raises(MCPTimeoutError):
            await client.call_tool(
                "search_items",
                {"keyword": "wallet"},
                auth_context=user_mcp_context,
            )
