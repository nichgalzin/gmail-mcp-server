"""Email service module for IMAP/SMTP operations."""

import os
import smtplib
from email import message_from_bytes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from imapclient import IMAPClient


async def send_email(to: str, subject: str, body: str) -> None:
    """Send an email via SMTP.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
    """
    email_user = os.environ["EMAIL_USER"]
    email_password = os.environ["EMAIL_APP_PASSWORD"]

    msg = MIMEMultipart()
    msg["From"] = email_user
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)


async def fetch_unread_emails(
    limit: int = 10, folder: str = "[Gmail]/Important"
) -> list[dict]:
    """Fetch unread emails from Gmail via IMAP.

    Args:
        limit: Maximum number of emails to fetch
        folder: Gmail folder to search

    Returns:
        List of email dictionaries with id, from, subject, date, and body
    """
    email_user = os.environ["EMAIL_USER"]
    email_password = os.environ["EMAIL_APP_PASSWORD"]

    # Connect to Gmail IMAP server
    with IMAPClient("imap.gmail.com", ssl=True) as client:
        # Login with your credentials
        client.login(email_user, email_password)

        # Select the specified folder
        client.select_folder(folder)

        # Search for unread emails
        unread_messages = client.search("UNSEEN")

        # Limit the number of emails to process
        limited_messages = (
            unread_messages[:limit] if len(unread_messages) > limit else unread_messages
        )

        emails = []

        # Fetch basic info for each unread email
        for msg_id in limited_messages:
            # Fetch the email data
            fetch_data = client.fetch([msg_id], ["RFC822"])
            raw_message = fetch_data[msg_id][b"RFC822"]

            # Parse the email - ensure we have bytes
            if isinstance(raw_message, bytes):
                email_message = message_from_bytes(raw_message)
            else:
                continue  # Skip if not proper format

            # Extract basic information
            email_info = {
                "id": str(msg_id),
                "from": email_message.get("From", ""),
                "subject": email_message.get("Subject", ""),
                "date": email_message.get("Date", ""),
                "body": _get_email_body(email_message),
            }

            emails.append(email_info)

        return emails


def _get_email_body(email_message) -> str:
    """Extract the body text from an email message.

    Args:
        email_message: Parsed email message object

    Returns:
        Email body as string
    """
    if email_message.is_multipart():
        # Handle multipart emails (HTML + text)
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode("utf-8", errors="ignore")
    else:
        # Handle simple text emails
        return email_message.get_payload(decode=True).decode("utf-8", errors="ignore")

    return ""


async def debug_gmail_folders() -> dict:
    """Debug function to see what folders/labels Gmail exposes via IMAP.

    Returns:
        Dictionary with folders and sample message flags
    """
    email_user = os.environ["EMAIL_USER"]
    email_password = os.environ["EMAIL_APP_PASSWORD"]

    with IMAPClient("imap.gmail.com", ssl=True) as client:
        client.login(email_user, email_password)

        # List all folders
        folders = client.list_folders()

        # Also check what's in INBOX
        client.select_folder("INBOX")

        # Get a sample of messages to see their flags/labels
        all_messages = client.search("ALL")
        sample_flags = None
        if all_messages:
            sample_msg = all_messages[0]
            fetch_data = client.fetch([sample_msg], ["FLAGS", "X-GM-LABELS"])
            sample_flags = fetch_data

        return {
            "folders": folders,
            "sample_flags": sample_flags,
        }


async def debug_email_filtering(limit: int = 5) -> list[dict]:
    """Debug function to show email filtering details.

    Args:
        limit: Number of emails to analyze

    Returns:
        List of email debug information
    """
    email_user = os.environ["EMAIL_USER"]
    email_password = os.environ["EMAIL_APP_PASSWORD"]

    with IMAPClient("imap.gmail.com", ssl=True) as client:
        client.login(email_user, email_password)
        client.select_folder("INBOX")

        # Get unread messages
        unread_messages = client.search("UNSEEN")
        limited_messages = (
            unread_messages[:limit] if len(unread_messages) > limit else unread_messages
        )

        debug_info = []

        for msg_id in limited_messages:
            fetch_data = client.fetch([msg_id], ["RFC822"])
            raw_message = fetch_data[msg_id][b"RFC822"]

            if isinstance(raw_message, bytes):
                email_message = message_from_bytes(raw_message)

                from_addr = email_message.get("From", "")
                subject = email_message.get("Subject", "")

                # Check promotional patterns
                promotional_patterns = [
                    "noreply",
                    "no-reply",
                    "donotreply",
                    "do-not-reply",
                    "newsletter",
                    "marketing",
                    "promo",
                    "offer",
                    "automated",
                    "notification",
                    "alert",
                    "support",
                ]

                matched_patterns = [
                    p for p in promotional_patterns if p in from_addr.lower()
                ]
                is_promotional = len(matched_patterns) > 0

                debug_info.append(
                    {
                        "id": str(msg_id),
                        "from": from_addr,
                        "subject": subject,
                        "is_promotional": is_promotional,
                        "matched_patterns": matched_patterns,
                    }
                )

        return debug_info
