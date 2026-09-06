import json
import asyncio
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from mcp.server.mcpserver import MCPServer
from app.core.config import settings
from app.mcp.context import MCPAuthContext, mcp_auth_context, mcp_db_session
from app.mcp.server import get_mcp_server

logger = logging.getLogger("unifound.mcp.client")


class MCPClientError(Exception):
    """Base exception for MCP client operations."""
    pass


class MCPToolNotFoundError(MCPClientError):
    """Raised when an agent attempts to invoke an unregistered tool."""
    pass


class MCPConnectionError(MCPClientError):
    """Raised when connecting to or communicating with the MCP server fails."""
    pass


class MCPTimeoutError(MCPClientError):
    """Raised when tool execution exceeds configured timeout."""
    pass


class UniFoundMCPClient:
    """
    Production client abstraction for interacting with the UniFound MCP Server.
    Provides dynamic tool discovery, schema inspection, authenticated tool calling,
    timeout handling, and graceful shutdown.
    """

    def __init__(
        self,
        server: Optional[MCPServer] = None,
        default_auth_context: Optional[MCPAuthContext] = None,
        timeout: Optional[float] = None,
        db_session: Optional[Session] = None,
    ):
        self._server = server
        self.default_auth_context = default_auth_context
        self.timeout = timeout if timeout is not None else float(settings.MCP_REQUEST_TIMEOUT)
        self.db_session = db_session
        self._connected = False
        self._cached_tools: Dict[str, Any] = {}

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def server(self) -> MCPServer:
        if self._server is None:
            self._server = get_mcp_server()
        return self._server

    async def connect(self) -> None:
        """Establish connection and dynamically discover available tools."""
        try:
            # Perform initial dynamic tool discovery to confirm server readiness
            tools = await self.server.list_tools()
            self._cached_tools = {t.name: t for t in tools}
            self._connected = True
            logger.info("Connected to UniFound MCP Server. Discovered %d tools.", len(self._cached_tools))
        except Exception as e:
            self._connected = False
            raise MCPConnectionError(f"Failed to connect to MCP server: {str(e)}")

    async def disconnect(self) -> None:
        """Clean shutdown of the client connection."""
        self._connected = False
        self._cached_tools.clear()
        logger.info("Disconnected from UniFound MCP Server.")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Dynamically query available tools from the MCP server (tools/list).
        Returns tool metadata without hardcoding tool definitions.
        """
        if not self._connected:
            await self.connect()

        try:
            server_tools = await self.server.list_tools()
            self._cached_tools = {t.name: t for t in server_tools}
            return [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.input_schema,
                }
                for t in server_tools
            ]
        except Exception as e:
            raise MCPConnectionError(f"Failed to discover tools: {str(e)}")

    async def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve schema and description for a specific tool by name."""
        if not self._connected:
            await self.connect()

        tool = self._cached_tools.get(tool_name)
        if not tool:
            # Refresh tools in case new tools were added dynamically
            await self.list_tools()
            tool = self._cached_tools.get(tool_name)

        if not tool:
            return None

        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,
        }

    async def call_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        auth_context: Optional[MCPAuthContext] = None,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Execute an MCP tool (tools/call) with authenticated context and timeout enforcement.
        Never trusts unauthenticated input.
        """
        if not self._connected:
            await self.connect()

        if tool_name not in self._cached_tools:
            # Refresh tools to verify
            await self.list_tools()
            if tool_name not in self._cached_tools:
                raise MCPToolNotFoundError(f"Tool '{tool_name}' is not registered on the MCP server.")

        arguments = arguments or {}
        context = auth_context or self.default_auth_context
        sess = db_session or self.db_session

        # Immediate timeout check
        if self.timeout <= 0:
            raise MCPTimeoutError(f"Tool execution for '{tool_name}' timed out after {self.timeout}s.")

        # Set task-local authenticated execution context & database session
        token = mcp_auth_context.set(context)
        db_token = mcp_db_session.set(sess) if sess is not None else None
        try:
            call_coro = self.server.call_tool(tool_name, arguments)
            result = await asyncio.wait_for(call_coro, timeout=self.timeout)

            # Parse structured content or text JSON from CallToolResult
            if result.is_error:
                return {
                    "error": "Tool execution indicated error",
                    "code": "TOOL_ERROR",
                    "content": [c.text for c in result.content if hasattr(c, "text")],
                }

            data = {}
            if result.structured_content is not None:
                data = result.structured_content
            elif result.content:
                text_content = result.content[0].text if hasattr(result.content[0], "text") else ""
                try:
                    data = json.loads(text_content)
                except Exception:
                    data = {"result": text_content}

            if isinstance(data, dict) and "result" in data and isinstance(data["result"], dict) and len(data) == 1:
                return data["result"]
            return data
        except asyncio.TimeoutError:
            logger.error("MCP tool '%s' timed out after %ss", tool_name, self.timeout)
            raise MCPTimeoutError(f"Tool execution for '{tool_name}' timed out after {self.timeout} seconds.")
        except MCPClientError:
            raise
        except Exception as e:
            logger.error("Error executing MCP tool '%s': %s", tool_name, e)
            raise MCPClientError(f"Failed to execute tool '{tool_name}': {str(e)}")
        finally:
            mcp_auth_context.reset(token)
            if db_token is not None:
                mcp_db_session.reset(db_token)

