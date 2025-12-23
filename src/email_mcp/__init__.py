"""Email MCP Server - An MCP server for Gmail email operations."""

__version__ = "1.0.0"

from .server import create_server, main, run_server

__all__ = ["create_server", "run_server", "main"]
