"""Main MCP server setup and initialization."""

import asyncio

import mcp.server.stdio
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from . import handlers


def create_server() -> Server:
    """Create and configure the MCP server.

    Returns:
        Configured MCP Server instance
    """
    server = Server("email-server")

    # Register tool list handler
    @server.list_tools()
    async def handle_list_tools():
        return await handlers.handle_list_tools()

    # Register tool call handler
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        return await handlers.handle_call_tool(name, arguments)

    return server


async def run_server():
    """Run the MCP server with stdio transport."""
    server = create_server()

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="email-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main():
    """Entry point for the email MCP server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
