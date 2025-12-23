"""MCP tool handlers for email operations."""

import mcp.types as types

from . import email_service


async def handle_list_tools() -> list[types.Tool]:
    """Return list of available MCP tools."""
    return [
        types.Tool(
            name="get_unread_emails",
            description="Fetch unread emails from Gmail inbox. Returns sender, subject, date, body, message ID, and thread ID for each email.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of emails to fetch (default: 10)",
                        "default": 10,
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="create_draft_reply",
            description="Create a draft reply to an email thread. The draft will appear in the original email thread in Gmail.",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_id": {
                        "type": "string",
                        "description": "The thread ID from get_unread_emails to reply to",
                    },
                    "reply_body": {
                        "type": "string",
                        "description": "The body text of your reply",
                    },
                },
                "required": ["thread_id", "reply_body"],
            },
        ),
    ]


async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle MCP tool calls.

    Args:
        name: Tool name to execute
        arguments: Tool arguments

    Returns:
        List of text content responses

    Raises:
        ValueError: If tool name is unknown
    """
    if name == "get_unread_emails":
        limit = arguments.get("limit", 10)
        emails = await email_service.fetch_unread_emails(limit)

        if not emails:
            return [types.TextContent(type="text", text="No unread emails found")]

        # Format the email list for display
        email_list = []
        for email in emails:
            email_summary = f"Thread ID: {email['thread_id']}\n"
            email_summary += f"Message ID: {email['id']}\n"
            email_summary += f"From: {email['from']}\n"
            email_summary += f"Subject: {email['subject']}\n"
            email_summary += f"Date: {email['date']}\n"
            email_summary += f"Body:\n{email['body']}\n"
            email_summary += "-" * 80
            email_list.append(email_summary)

        result = f"Found {len(emails)} unread email(s):\n\n" + "\n\n".join(email_list)
        return [types.TextContent(type="text", text=result)]

    elif name == "create_draft_reply":
        thread_id = arguments["thread_id"]
        reply_body = arguments["reply_body"]

        draft_info = await email_service.create_draft_reply(thread_id, reply_body)

        result = (
            f"✓ Draft reply created successfully!\n\n"
            f"Draft ID: {draft_info['draft_id']}\n"
            f"Thread ID: {draft_info['thread_id']}\n\n"
            f"The draft has been added to the email thread in Gmail."
        )
        return [types.TextContent(type="text", text=result)]

    raise ValueError(f"Unknown tool: {name}")
