import sys
import logging
from typing import Optional, Dict, Any
from mcp.server.mcpserver import MCPServer
from app.core.config import settings
from app.mcp.tools import (
    mcp_search_items,
    mcp_get_item,
    mcp_find_matches,
    mcp_analyze_image,
    mcp_create_claim,
    mcp_get_claim_status,
)

logger = logging.getLogger("unifound.mcp.server")


def create_mcp_server() -> MCPServer:
    """
    Create and configure the official UniFound MCP Server.
    Registers all 6 UniFound tools that delegate strictly to the application service layer.
    """
    server = MCPServer(
        name=settings.MCP_SERVER_NAME,
        instructions="UniFound MCP Server – Exposes campus lost & found services for autonomous AI agents.",
        version=settings.VERSION,
    )

    @server.tool(
        description="Search lost and found items by keyword, item type (LOST/FOUND), category, location, status, or date range."
    )
    def search_items(
        keyword: Optional[str] = None,
        item_type: Optional[str] = None,
        category: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """Search items in the lost-and-found registry."""
        return mcp_search_items(
            keyword=keyword,
            item_type=item_type,
            category=category,
            location=location,
            status=status,
            from_date=from_date,
            to_date=to_date,
            page=page,
            page_size=page_size,
        )

    @server.tool(
        description="Retrieve public details of a specific item report by its ID."
    )
    def get_item(item_id: int) -> Dict[str, Any]:
        """Get item report details."""
        return mcp_get_item(item_id=item_id)

    @server.tool(
        description="Find opposite-type potential matches (LOST <-> FOUND) for an item using multi-factor similarity scoring."
    )
    def find_matches(
        item_id: int,
        min_confidence: float = 40.0,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """Find candidate matches for an item report."""
        return mcp_find_matches(
            item_id=item_id,
            min_confidence=min_confidence,
            page=page,
            page_size=page_size,
        )

    @server.tool(
        description="Extract structured visual attributes (colors, brand, traits) from an item's uploaded image. Requires item owner or admin."
    )
    def analyze_image(item_id: int) -> Dict[str, Any]:
        """Analyze item image visual attributes."""
        return mcp_analyze_image(item_id=item_id)

    @server.tool(
        description="Submit an ownership claim for an item. Claimant identity is securely derived from authenticated context."
    )
    def create_claim(
        item_id: int,
        description: str,
        evidence: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submit an ownership claim for an item."""
        return mcp_create_claim(
            item_id=item_id,
            description=description,
            evidence=evidence,
        )

    @server.tool(
        description="Inspect the status and details of an ownership claim. Requires claimant, item reporter, or admin permissions."
    )
    def get_claim_status(claim_id: int) -> Dict[str, Any]:
        """Get claim status and details."""
        return mcp_get_claim_status(claim_id=claim_id)

    return server


_server_instance: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    """Singleton getter for the UniFound MCP Server."""
    global _server_instance
    if _server_instance is None:
        _server_instance = create_mcp_server()
    return _server_instance


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="UniFound MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse", "streamable-http"], default="stdio", help="MCP transport protocol")
    parser.add_argument("--host", default=settings.MCP_SERVER_HOST, help="Host to bind for SSE/HTTP transport")
    parser.add_argument("--port", type=int, default=settings.MCP_SERVER_PORT, help="Port to bind for SSE/HTTP transport")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger.info("Starting UniFound MCP Server (%s transport on %s:%s)...", args.transport, args.host, args.port)
    server = get_mcp_server()
    try:
        if args.transport == "sse":
            server.run(transport="sse", host=args.host, port=args.port)
        elif args.transport == "streamable-http":
            server.run(transport="streamable-http", host=args.host, port=args.port)
        else:
            server.run(transport="stdio")
    except (KeyboardInterrupt, SystemExit):
        logger.info("UniFound MCP Server stopped.")

