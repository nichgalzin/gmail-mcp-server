"""MCP tool handlers for email operations."""

import mcp.types as types

from . import email_service


async def handle_list_tools() -> list[types.Tool]:
    """Return list of available MCP tools."""
    return [
        types.Tool(
            name="send_email",
            description="Send an email",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"},
                },
                "required": ["to", "subject", "body"],
            },
        ),
        types.Tool(
            name="get_unread_emails",
            description="Fetch unread emails from Gmail folder. Default is Gmail's Important folder (like Primary tab). Use 'INBOX' for all emails, or 'Personal', 'Work', etc. for specific categories.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of emails to fetch (default: 10)",
                        "default": 10,
                    },
                    "folder": {
                        "type": "string",
                        "description": "Gmail folder to search (default: [Gmail]/Important). Options: INBOX, Personal, Work, [Gmail]/Important, etc.",
                        "default": "[Gmail]/Important",
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="debug_gmail_folders",
            description="Debug: List Gmail folders and labels to understand IMAP structure",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name="debug_email_filtering",
            description="Debug: Show how email filtering is working on recent unread emails",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of emails to analyze (default: 5)",
                        "default": 5,
                    },
                },
                "required": [],
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
    if name == "send_email":
        to = arguments["to"]
        subject = arguments["subject"]
        body = arguments["body"]

        await email_service.send_email(to, subject, body)
        return [types.TextContent(type="text", text=f"✓ Email sent to {to}")]

    elif name == "get_unread_emails":
        limit = arguments.get("limit", 10)
        folder = arguments.get("folder", "[Gmail]/Important")
        emails = await email_service.fetch_unread_emails(limit, folder)

        if not emails:
            return [types.TextContent(type="text", text="No unread emails found")]

        # Format the email list for display
        email_list = []
        for email in emails:
            email_summary = f"ID: {email['id']}\n"
            email_summary += f"From: {email['from']}\n"
            email_summary += f"Subject: {email['subject']}\n"
            email_summary += f"Date: {email['date']}\n"
            email_summary += f"Body: {email['body'][:100]}...\n"
            email_summary += "-" * 50
            email_list.append(email_summary)

        result = f"Found {len(emails)} unread email(s):\n\n" + "\n\n".join(email_list)
        return [types.TextContent(type="text", text=result)]

    elif name == "debug_gmail_folders":
        debug_info = await email_service.debug_gmail_folders()

        folders_text = "Gmail Folders:\n"
        for folder in debug_info["folders"]:
            folders_text += f"  {folder}\n"

        flags_text = "\nSample Message Info:\n"
        if debug_info["sample_flags"]:
            flags_text += str(debug_info["sample_flags"])
        else:
            flags_text += "No messages found"

        result = folders_text + flags_text
        return [types.TextContent(type="text", text=result)]

    elif name == "debug_email_filtering":
        limit = arguments.get("limit", 5)
        debug_info = await email_service.debug_email_filtering(limit)

        if not debug_info:
            return [
                types.TextContent(type="text", text="No unread emails found to analyze")
            ]

        result = f"Email Filtering Analysis (showing {len(debug_info)} emails):\n\n"

        for email in debug_info:
            result += f"Email ID: {email['id']}\n"
            result += f"From: {email['from']}\n"
            result += f"Subject: {email['subject']}\n"
            result += f"Is Promotional: {email['is_promotional']}\n"
            if email["matched_patterns"]:
                result += f"Matched Patterns: {', '.join(email['matched_patterns'])}\n"
            result += "-" * 50 + "\n\n"

        return [types.TextContent(type="text", text=result)]

    raise ValueError(f"Unknown tool: {name}")
