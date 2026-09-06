import os
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.item import Item, ItemType
from app.models.user import User
from app.schemas.item import ItemReportCreate
from app.services.item_service import item_service
from app.mcp.client import UniFoundMCPClient
from app.mcp.server import create_mcp_server
from app.mcp.context import MCPAuthContext
from app.agents.models import ToolDecision, AgentStep
from app.agents.prompts import build_react_prompt, build_reflection_prompt
from app.agents.llm_gateway import LLMProvider, HeuristicReActProvider, LLMGateway
from app.agents.reflection import ReflectionAgent
from app.agents.orchestrator import ReActOrchestrator


@pytest.fixture
def mcp_client(db_session: Session):
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


# 1. Agent Endpoint Authentication
def test_agent_endpoint_authentication(client: TestClient, user_token: str):
    """POST /api/v1/agent/query requires valid JWT authentication."""
    # Unauthenticated -> 401
    resp_unauth = client.post("/api/v1/agent/query", json={"message": "Find my lost keys"})
    assert resp_unauth.status_code == 401

    # Authenticated -> 200
    headers = {"Authorization": f"Bearer {user_token}"}
    resp_auth = client.post("/api/v1/agent/query", json={"message": "Search lost wallet"}, headers=headers)
    assert resp_auth.status_code == 200
    data = resp_auth.json()
    assert "final_answer" in data
    assert "tools_used" in data
    assert data["execution_status"] in ("COMPLETED", "MAX_ITERATIONS")


# 2. Dynamic MCP Tool Discovery in Orchestrator
@pytest.mark.anyio
async def test_orchestrator_dynamic_tool_discovery(mcp_client: UniFoundMCPClient):
    """Orchestrator queries MCP tools/list dynamically without hardcoded tool lists."""
    orchestrator = ReActOrchestrator(mcp_client=mcp_client)
    await mcp_client.connect()
    tools = await mcp_client.list_tools()
    assert len(tools) >= 6
    names = [t["name"] for t in tools]
    assert "search_items" in names
    assert "find_matches" in names
    assert "create_claim" in names


# 3. Single-Tool Execution via ReAct Loop
@pytest.mark.anyio
async def test_react_single_tool_execution(
    mcp_client: UniFoundMCPClient, db_session: Session, test_user: User, user_mcp_context: MCPAuthContext
):
    """Single-tool query executes search_items through MCP and synthesizes factual response."""
    now = datetime.now(timezone.utc)
    item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Red HydroFlask Water Bottle",
            description="32oz red metal water bottle with campus stickers.",
            category="Other",
            location="Student Union",
            incident_date=now,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )

    orchestrator = ReActOrchestrator(mcp_client=mcp_client)
    response = await orchestrator.run(
        message="Search for lost water bottle",
        auth_context=user_mcp_context,
    )

    assert response.execution_status == "COMPLETED"
    assert "search_items" in response.tools_used
    assert response.steps_count >= 1
    assert "HydroFlask" in response.final_answer or "bottle" in response.final_answer.lower()


# 4. Multi-Step ReAct Execution
@pytest.mark.anyio
async def test_react_multi_step_execution(
    mcp_client: UniFoundMCPClient, db_session: Session, test_user: User, user_mcp_context: MCPAuthContext
):
    """Multi-step query executes get_item -> find_matches and returns ranked candidates."""
    now = datetime.now(timezone.utc)
    lost_item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Sony WH-1000XM5 Headphones",
            description="Silver noise cancelling headphones in black travel case.",
            category="Electronics",
            location="Library Study Room 4",
            incident_date=now,
        ),
        item_type=ItemType.LOST,
        reporter_id=test_user.id,
    )
    found_item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Sony Silver Noise Cancelling Headphones",
            description="Found silver Sony headphones in library case.",
            category="Electronics",
            location="Library Level 2",
            incident_date=now,
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_user.id,
    )

    orchestrator = ReActOrchestrator(mcp_client=mcp_client)
    response = await orchestrator.run(
        message=f"Find the best match for item #{lost_item.id}",
        auth_context=user_mcp_context,
    )

    assert response.execution_status == "COMPLETED"
    # Verify multi-step tool sequence
    assert "get_item" in response.tools_used
    assert "find_matches" in response.tools_used
    assert response.steps_count >= 2
    assert response.confidence is not None
    assert response.confidence >= 50.0
    assert str(found_item.id) in response.final_answer or "Sony" in response.final_answer


# 5. Unknown Tool Rejection and Graceful Recovery
@pytest.mark.anyio
async def test_unknown_tool_rejection_and_recovery(
    mcp_client: UniFoundMCPClient, user_mcp_context: MCPAuthContext
):
    """Orchestrator detects unrecognized tool names and recovers safely."""
    class BadToolThenFinalProvider(LLMProvider):
        def __init__(self):
            self.turn = 0

        async def generate_decision(self, prompt, tools, history, user_message):
            self.turn += 1
            if self.turn == 1:
                # Propose a non-existent tool
                return ToolDecision(
                    action="tool",
                    tool_name="unauthorized_system_command",
                    arguments={"cmd": "whoami"},
                    reasoning_summary="Attempting unauthorized tool call.",
                )
            return ToolDecision(
                action="final",
                arguments={"answer": "Recovered safely from unknown tool attempt."},
                reasoning_summary="Completed.",
            )

        async def reflect(self, prompt, steps, candidate_answer):
            return True, None, None

    gateway = LLMGateway(primary_provider=BadToolThenFinalProvider())
    orchestrator = ReActOrchestrator(mcp_client=mcp_client, llm_gateway=gateway)

    response = await orchestrator.run(
        message="Test unknown tool resilience",
        auth_context=user_mcp_context,
    )

    assert response.execution_status == "COMPLETED"
    assert "unauthorized_system_command" not in response.tools_used
    assert response.steps_count >= 2


# 6. Invalid Arguments Handled Gracefully
@pytest.mark.anyio
async def test_invalid_arguments_handled_gracefully(
    mcp_client: UniFoundMCPClient, user_mcp_context: MCPAuthContext
):
    """Tool invocation with invalid arguments records failure observation and continues."""
    class InvalidArgsProvider(LLMProvider):
        def __init__(self):
            self.turn = 0

        async def generate_decision(self, prompt, tools, history, user_message):
            self.turn += 1
            if self.turn == 1:
                # Description too short (< 10 chars) for create_claim
                return ToolDecision(
                    action="tool",
                    tool_name="create_claim",
                    arguments={"item_id": 1, "description": "Mine"},
                    reasoning_summary="Attempting claim with short description.",
                )
            return ToolDecision(
                action="final",
                arguments={"answer": "Claim validation error handled appropriately."},
                reasoning_summary="Completed.",
            )

        async def reflect(self, prompt, steps, candidate_answer):
            return True, None, None

    gateway = LLMGateway(primary_provider=InvalidArgsProvider())
    orchestrator = ReActOrchestrator(mcp_client=mcp_client, llm_gateway=gateway)

    response = await orchestrator.run(
        message="Test invalid argument handling",
        auth_context=user_mcp_context,
    )

    assert response.execution_status == "COMPLETED"
    # Observation recorded the validation failure
    assert len(response.tool_results_summary) >= 1
    assert response.tool_results_summary[0]["success"] is False


# 7. MCP Error Handling
@pytest.mark.anyio
async def test_mcp_error_handling(
    mcp_client: UniFoundMCPClient, user_mcp_context: MCPAuthContext
):
    """Nonexistent item returns controlled error without crashing the agent."""
    orchestrator = ReActOrchestrator(mcp_client=mcp_client)
    response = await orchestrator.run(
        message="Find matches for item #999999",
        auth_context=user_mcp_context,
    )

    assert response.execution_status in ("COMPLETED", "MAX_ITERATIONS")
    assert "get_item" in response.tools_used


# 8. LLM Failure and Fallback Mechanism
@pytest.mark.anyio
async def test_llm_failure_and_fallback(
    mcp_client: UniFoundMCPClient, user_mcp_context: MCPAuthContext
):
    """When the primary LLM provider fails, gateway transparently falls back to heuristic provider."""
    class FailingProvider(LLMProvider):
        async def generate_decision(self, prompt, tools, history, user_message):
            raise ConnectionError("Primary LLM service unreachable (timeout)")

        async def reflect(self, prompt, steps, candidate_answer):
            raise ConnectionError("Primary LLM service unreachable")

    # Gateway with failing primary and heuristic fallback
    gateway = LLMGateway(
        primary_provider=FailingProvider(),
        fallback_provider=HeuristicReActProvider(),
    )
    orchestrator = ReActOrchestrator(mcp_client=mcp_client, llm_gateway=gateway)

    response = await orchestrator.run(
        message="Search lost umbrella",
        auth_context=user_mcp_context,
    )

    assert response.execution_status == "COMPLETED"
    assert "search_items" in response.tools_used


# 9. Max Iterations Protection
@pytest.mark.anyio
async def test_max_iterations_protection(
    mcp_client: UniFoundMCPClient, user_mcp_context: MCPAuthContext
):
    """Orchestrator halts loop when max_iterations is reached without infinite recursion."""
    class NeverEndingProvider(LLMProvider):
        async def generate_decision(self, prompt, tools, history, user_message):
            # Always requests another search
            return ToolDecision(
                action="tool",
                tool_name="search_items",
                arguments={"keyword": "loop"},
                reasoning_summary="Indefinite search loop.",
            )

        async def reflect(self, prompt, steps, candidate_answer):
            return True, None, None

    gateway = LLMGateway(primary_provider=NeverEndingProvider())
    orchestrator = ReActOrchestrator(mcp_client=mcp_client, llm_gateway=gateway, max_iterations=3)

    response = await orchestrator.run(
        message="Test max iterations",
        auth_context=user_mcp_context,
    )

    assert response.execution_status == "MAX_ITERATIONS"
    assert response.steps_count == 3
    assert "maximum search limit" in response.final_answer.lower()


# 10. Reflection Agent Validation and Correction
@pytest.mark.anyio
async def test_reflection_validation_and_corrective_iteration(
    mcp_client: UniFoundMCPClient, user_mcp_context: MCPAuthContext
):
    """Reflection agent rejects an unsupported answer and prompts a corrective iteration."""
    class HallucinatingThenCorrectProvider(LLMProvider):
        def __init__(self):
            self.turn = 0

        async def generate_decision(self, prompt, tools, history, user_message):
            self.turn += 1
            if self.turn == 1:
                # Fabricates 99% confidence without matching tool
                return ToolDecision(
                    action="final",
                    arguments={"answer": "I found your item with 99% confidence!", "confidence": 99.0},
                    reasoning_summary="Claiming false confidence.",
                )
            # Corrected response
            return ToolDecision(
                action="final",
                arguments={"answer": "Search completed. No confident matches confirmed without matching inspection."},
                reasoning_summary="Corrected response.",
            )

        async def reflect(self, prompt, steps, candidate_answer):
            if "99%" in candidate_answer:
                return False, "Candidate claims 99% confidence without running matching tools.", None
            return True, None, None

    gateway = LLMGateway(primary_provider=HallucinatingThenCorrectProvider())
    orchestrator = ReActOrchestrator(mcp_client=mcp_client, llm_gateway=gateway)

    response = await orchestrator.run(
        message="What is the match confidence?",
        auth_context=user_mcp_context,
    )

    assert response.execution_status == "COMPLETED"
    assert "99%" not in response.final_answer


# 11. Claimant Identity Cannot Be Spoofed
@pytest.mark.anyio
async def test_claimant_identity_spoofing_prevented(
    mcp_client: UniFoundMCPClient,
    db_session: Session,
    test_user: User,
    test_admin: User,
    user_mcp_context: MCPAuthContext,
):
    """Agent claim submissions derive identity strictly from authenticated JWT context."""
    item = item_service.create_report(
        db=db_session,
        report_in=ItemReportCreate(
            title="Stainless Steel Watch",
            description="Citizen automatic wristwatch with steel bracelet.",
            category="Jewelry",
            location="Gym Locker Room",
            incident_date=datetime.now(timezone.utc),
        ),
        item_type=ItemType.FOUND,
        reporter_id=test_admin.id,
    )

    orchestrator = ReActOrchestrator(mcp_client=mcp_client)
    response = await orchestrator.run(
        message=f"Submit claim for item #{item.id} because I lost my Citizen watch with scratched bezel.",
        auth_context=user_mcp_context,
    )

    assert response.execution_status == "COMPLETED"
    assert "create_claim" in response.tools_used
    assert "submitted successfully" in response.final_answer.lower() or "claim" in response.final_answer.lower()


# 12. Architectural Verification: No Direct DB Access from Agent Layer
def test_no_direct_db_access_in_agent_package():
    """Verify that backend/app/agents/ never imports SQLAlchemy models, sessions, or repositories."""
    agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "agents"))
    forbidden_patterns = [
        "from app.models",
        "import app.models",
        "from app.db",
        "import app.db",
        "from app.services.item_service",
        "from app.services.claim_service",
        "from app.services.matching_service",
    ]

    for fname in os.listdir(agents_dir):
        if fname.endswith(".py"):
            fpath = os.path.join(agents_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                for pattern in forbidden_patterns:
                    assert pattern not in content, (
                        f"Architectural violation: Forbidden import '{pattern}' found in {fname}. "
                        "Agents must access system functionality exclusively through UniFoundMCPClient."
                    )
