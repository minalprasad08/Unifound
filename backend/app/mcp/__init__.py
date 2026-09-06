"""
UniFound MCP (Model Context Protocol) Module.
Provides the MCP Server, tools, and client abstraction for AI agent interactions.
"""
from app.mcp.context import MCPAuthContext, mcp_auth_context
from app.mcp.server import create_mcp_server, get_mcp_server
from app.mcp.client import UniFoundMCPClient

__all__ = [
    "MCPAuthContext",
    "mcp_auth_context",
    "create_mcp_server",
    "get_mcp_server",
    "UniFoundMCPClient",
]
