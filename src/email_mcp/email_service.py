"""Email service module for Gmail API operations."""

import base64
from email.mime.text import MIMEText

from .gmail_auth import get_gmail_service


async def fetch_unread_emails(limit: int = 10) -> list[dict]:
    """Fetch unread emails from Gmail using Gmail API.

    Args:
        limit: Maximum number of emails to fetch

    Returns:
        List of email dictionaries with:
        - id: Message ID
        - thread_id: Thread ID (for creating threaded replies)
        - from: Sender email address
        - subject: Email subject
        - date: Date received
        - body: Email body text (plain text preferred, falls back to snippet)
    """
    service = get_gmail_service()

    # Query for unread messages in inbox
    results = service.users().messages().list(
        userId="me",
        q="is:unread",
        maxResults=limit
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        return []

    emails = []

    for msg in messages:
        # Fetch full message details
        message = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        # Extract headers
        headers = message.get("payload", {}).get("headers", [])
        subject = _get_header(headers, "Subject")
        from_addr = _get_header(headers, "From")
        date = _get_header(headers, "Date")

        # Extract body
        body = _get_message_body(message)

        email_info = {
            "id": message["id"],
            "thread_id": message["threadId"],
            "from": from_addr,
            "subject": subject,
            "date": date,
            "body": body,
        }

        emails.append(email_info)

    return emails


async def create_draft_reply(thread_id: str, reply_body: str) -> dict:
    """Create a draft reply to an email thread.

    Args:
        thread_id: The Gmail thread ID to reply to
        reply_body: The body text of the reply

    Returns:
        Dictionary with draft information:
        - draft_id: ID of the created draft
        - message_id: ID of the draft message
        - thread_id: Thread ID the draft belongs to
    """
    service = get_gmail_service()

    # Get the original thread to extract necessary info for proper threading
    thread = service.users().threads().get(
        userId="me",
        id=thread_id
    ).execute()

    # Get the last message in the thread (the one we're replying to)
    messages = thread.get("messages", [])
    if not messages:
        raise ValueError(f"No messages found in thread {thread_id}")

    original_message = messages[-1]
    headers = original_message.get("payload", {}).get("headers", [])

    # Extract headers needed for proper threading
    to_addr = _get_header(headers, "From")  # Reply to the sender
    subject = _get_header(headers, "Subject")
    message_id = _get_header(headers, "Message-ID")
    references = _get_header(headers, "References") or ""

    # Build References header for proper threading
    # References should include all previous Message-IDs plus the one we're replying to
    if references:
        references_list = references.strip().split()
        if message_id and message_id not in references_list:
            references_list.append(message_id)
        new_references = " ".join(references_list)
    else:
        new_references = message_id if message_id else ""

    # Ensure subject has "Re:" prefix if not already present
    if subject and not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    # Create the MIME message
    message = MIMEText(reply_body)
    message["To"] = to_addr
    message["Subject"] = subject

    # Critical headers for proper threading
    if message_id:
        message["In-Reply-To"] = message_id
    if new_references:
        message["References"] = new_references

    # Encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    # Create the draft with threadId for proper threading
    draft_body = {
        "message": {
            "raw": raw_message,
            "threadId": thread_id,  # Critical: ensures draft appears in the thread
        }
    }

    draft = service.users().drafts().create(
        userId="me",
        body=draft_body
    ).execute()

    return {
        "draft_id": draft["id"],
        "message_id": draft["message"]["id"],
        "thread_id": draft["message"]["threadId"],
    }


def _get_header(headers: list[dict], name: str) -> str:
    """Extract a specific header value from email headers.

    Args:
        headers: List of header dictionaries
        name: Header name to find

    Returns:
        Header value or empty string if not found
    """
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")
    return ""


def _get_message_body(message: dict) -> str:
    """Extract the plain text body from a Gmail message.

    Args:
        message: Gmail message object

    Returns:
        Plain text body, or snippet if body extraction fails
    """
    payload = message.get("payload", {})

    # Try to get the body from the payload
    body = _extract_body_from_payload(payload)

    # Fall back to snippet if we couldn't extract the body
    if not body:
        body = message.get("snippet", "")

    return body


def _extract_body_from_payload(payload: dict) -> str:
    """Recursively extract text/plain body from message payload.

    Args:
        payload: Message payload object

    Returns:
        Decoded plain text body
    """
    # Check if this part has a body
    if "body" in payload and "data" in payload["body"]:
        mime_type = payload.get("mimeType", "")
        if mime_type == "text/plain":
            # Decode the base64-encoded body
            body_data = payload["body"]["data"]
            return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")

    # If multipart, recursively search parts
    if "parts" in payload:
        for part in payload["parts"]:
            # Prefer text/plain over text/html
            if part.get("mimeType") == "text/plain":
                result = _extract_body_from_payload(part)
                if result:
                    return result

        # If no text/plain found, try any part
        for part in payload["parts"]:
            result = _extract_body_from_payload(part)
            if result:
                return result

    return ""
