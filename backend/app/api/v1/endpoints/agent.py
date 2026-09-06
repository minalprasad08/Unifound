import time
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.mcp.context import MCPAuthContext
from app.mcp.client import UniFoundMCPClient
from app.services.audit_service import audit_service
from app.agents.models import AgentRequest, AgentResponse
from app.agents.orchestrator import ReActOrchestrator
from app.core.rate_limiter import rate_limit_agent

logger = logging.getLogger("unifound.api.agent")

router = APIRouter()


@router.post(
    "/query",
    response_model=AgentResponse,
    summary="Submit natural language request to the autonomous ReAct agent",
    description="Uses dynamic MCP tool discovery and the ReAct orchestration loop to fulfill user inquiries safely.",
    dependencies=[Depends(rate_limit_agent)],
)
async def agent_query(
    request_in: AgentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentResponse:
    start_time = time.time()

    # User identity is strictly derived from JWT; body IDs are ignored
    auth_ctx = MCPAuthContext(
        user_id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        full_name=current_user.full_name,
    )

    # Initialize MCP client with shared DB session for request consistency
    mcp_client = UniFoundMCPClient(db_session=db)
    orchestrator = ReActOrchestrator(mcp_client=mcp_client)

    try:
        response = await orchestrator.run(
            message=request_in.message,
            auth_context=auth_ctx,
        )
    except Exception as e:
        logger.error("Agent query execution exception: %s", e, exc_info=True)
        # Log failure audit
        audit_service.log(
            db=db,
            action="AGENT_QUERY_EXECUTION",
            entity_type="AGENT",
            actor_id=current_user.id,
            details=f"Query failed: {request_in.message[:80]}... Error: {str(e)}",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent reasoning loop encountered an internal error. Please try again.",
        )

    duration = time.time() - start_time

    # Safe audit log (never stores raw thoughts or credentials)
    audit_service.log(
        db=db,
        action="AGENT_QUERY_EXECUTION",
        entity_type="AGENT",
        actor_id=current_user.id,
        details=(
            f"Query: '{request_in.message[:80]}' | Status: {response.execution_status} | "
            f"Steps: {response.steps_count} | Tools: {', '.join(response.tools_used) or 'none'} | "
            f"Duration: {duration:.2f}s"
        ),
    )

    return response
