import contextvars
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.models.user import User, UserRole


class MCPAuthError(Exception):
    """Raised when an MCP tool invocation lacks valid authenticated context."""
    pass


class MCPForbiddenError(Exception):
    """Raised when an MCP tool invocation lacks required role or ownership permission."""
    pass


class MCPAuthContext(BaseModel):
    """Authenticated identity propagated through the MCP execution context."""
    user_id: int = Field(..., description="Unique database ID of authenticated user")
    email: str = Field(..., description="Email address of authenticated user")
    role: UserRole = Field(..., description="Role of authenticated user (USER or ADMIN)")
    is_active: bool = Field(True, description="Whether the account is active")
    full_name: Optional[str] = Field(None, description="Full name of user")


# Thread-safe and task-local authenticated execution context
mcp_auth_context: contextvars.ContextVar[Optional[MCPAuthContext]] = contextvars.ContextVar(
    "mcp_auth_context", default=None
)

# Optional task-local database session context (allows test isolation and request session sharing)
mcp_db_session: contextvars.ContextVar[Optional[Session]] = contextvars.ContextVar(
    "mcp_db_session", default=None
)


def get_current_mcp_user(db: Session) -> User:
    """
    Retrieve and validate the current authenticated user from the MCP execution context.
    Never trusts tool arguments; derives identity strictly from authenticated context.
    """
    ctx = mcp_auth_context.get()
    if ctx is None:
        raise MCPAuthError("Authentication required: No authenticated MCP context found.")

    user = db.get(User, ctx.user_id)
    if not user:
        raise MCPAuthError(f"Authenticated user with ID {ctx.user_id} does not exist.")

    if not user.is_active:
        raise MCPAuthError("User account is inactive or has been deactivated.")

    return user


def require_mcp_admin(db: Session) -> User:
    """Validate that the authenticated MCP caller has administrator privileges."""
    user = get_current_mcp_user(db)
    if user.role != UserRole.ADMIN:
        raise MCPForbiddenError("Forbidden: Administrator privileges required for this MCP tool.")
    return user
