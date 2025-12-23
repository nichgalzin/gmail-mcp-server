"""Gmail API OAuth 2.0 authentication module."""

import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
# gmail.readonly - read emails
# gmail.compose - create drafts
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]


def get_gmail_service():
    """Authenticate and return Gmail API service.

    This handles the OAuth 2.0 flow:
    1. Checks if token.json exists (saved credentials)
    2. If valid, uses it
    3. If expired, refreshes it
    4. If missing, starts OAuth flow (opens browser)

    Returns:
        Gmail API service object

    Raises:
        FileNotFoundError: If credentials.json is missing
    """
    creds = None

    # Get the project root directory (3 levels up from this file)
    project_root = Path(__file__).parent.parent.parent

    # Get paths from environment or use defaults relative to project root
    credentials_path = os.getenv(
        "GOOGLE_CREDENTIALS_PATH", str(project_root / "credentials.json")
    )
    token_path = os.getenv("GOOGLE_TOKEN_PATH", str(project_root / "token.json"))

    # Convert to Path objects for better handling
    credentials_file = Path(credentials_path)
    token_file = Path(token_path)

    # Check if we have saved credentials (token.json)
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    # If credentials are invalid or don't exist, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired credentials
            try:
                creds.refresh(Request())
            except Exception as e:
                raise RuntimeError(
                    f"Failed to refresh credentials: {e}\n"
                    "You may need to delete token.json and re-authenticate."
                )
        else:
            # Start new OAuth flow
            if not credentials_file.exists():
                raise FileNotFoundError(
                    f"Credentials file not found: {credentials_file}\n"
                    "Download it from Google Cloud Console:\n"
                    "https://console.cloud.google.com/apis/credentials"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_file), SCOPES
            )
            # This will open a browser for authentication
            creds = flow.run_local_server(port=0)

        # Save credentials for next time
        token_file.write_text(creds.to_json())

    # Build and return the Gmail API service
    try:
        return build("gmail", "v1", credentials=creds)
    except Exception as e:
        raise RuntimeError(f"Failed to build Gmail service: {e}")
