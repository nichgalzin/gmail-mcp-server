# Gmail API Setup Guide

This guide walks you through setting up Google Cloud Platform, enabling the Gmail API, and configuring OAuth 2.0 credentials for this MCP server.

## Prerequisites

- A Google account (Gmail)
- ~10-15 minutes

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click the project dropdown at the top of the page (next to "Google Cloud")
4. Click **"NEW PROJECT"**
5. Enter a project name (e.g., "Gmail MCP Server")
6. Click **"CREATE"**
7. Wait for the project to be created, then select it from the project dropdown

## Step 2: Enable the Gmail API

1. With your project selected, go to the [Gmail API page](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
   - Or: Use the search bar at the top and search for "Gmail API"
2. Click **"ENABLE"**
3. Wait for the API to be enabled (this takes a few seconds)

## Step 3: Configure OAuth Consent Screen

Before creating credentials, you need to configure the OAuth consent screen.

1. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
   - Or: Navigate to **APIs & Services → OAuth consent screen** in the left sidebar
2. Select **"External"** as the User Type (unless you have a Google Workspace account)
3. Click **"CREATE"**

### Fill in the required fields:

**App information:**
- **App name:** Gmail MCP Server (or your preferred name)
- **User support email:** Your email address
- **Developer contact email:** Your email address

**App domain (optional):** Leave blank for now

4. Click **"SAVE AND CONTINUE"**

### Add Scopes:

5. Click **"ADD OR REMOVE SCOPES"**
6. In the filter box, search for "Gmail API"
7. Select these two scopes:
   - `https://www.googleapis.com/auth/gmail.readonly` - Read emails
   - `https://www.googleapis.com/auth/gmail.compose` - Create drafts
8. Click **"UPDATE"**
9. Click **"SAVE AND CONTINUE"**

### Add Test Users:

10. Click **"ADD USERS"**
11. Enter your Gmail address (the one you want to read emails from)
12. Click **"ADD"**
13. Click **"SAVE AND CONTINUE"**
14. Review the summary and click **"BACK TO DASHBOARD"**

## Step 4: Create OAuth 2.0 Credentials

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
   - Or: Navigate to **APIs & Services → Credentials** in the left sidebar
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**

### Configure the OAuth client:

4. **Application type:** Select **"Desktop app"**
5. **Name:** Gmail MCP Client (or your preferred name)
6. Click **"CREATE"**

### Download Credentials:

7. A dialog will appear with your client ID and secret
8. Click **"DOWNLOAD JSON"**
9. Save the file as `credentials.json` in your project root directory:
   ```
   /Users/dropout/webdev/mcp-servers/email/credentials.json
   ```

## Step 5: Verify Your Setup

Your project directory should now have:

```
/Users/dropout/webdev/mcp-servers/email/
├── credentials.json          ← Downloaded from Google Cloud
├── .env.example              ← Template (already exists)
├── requirements.txt          ← Dependencies
└── src/
    └── email_mcp/
        ├── gmail_auth.py     ← OAuth handling
        └── ...
```

## Step 6: First-Time Authentication

The first time you run the MCP server, it will:

1. Open your default web browser
2. Ask you to sign in to your Google account
3. Show a warning: **"Google hasn't verified this app"**
   - Click **"Advanced"**
   - Click **"Go to Gmail MCP Server (unsafe)"**
   - This is safe because YOU created the app
4. Review the permissions and click **"Allow"**
5. The browser will show "The authentication flow has completed"
6. A `token.json` file will be created in your project root
7. Future runs will use `token.json` (no browser popup needed)

## Understanding the Scopes

The two Gmail API scopes we're using:

- **`gmail.readonly`** - Allows reading emails (for `get_unread_emails` tool)
- **`gmail.compose`** - Allows creating drafts (for `create_draft_reply` tool)

These are the minimum required scopes. The server cannot:
- Send emails directly
- Delete emails
- Modify existing emails
- Access other Google services

## Troubleshooting

### "Access blocked: This app's request is invalid"
- Make sure you added your email as a test user in Step 3
- Make sure both required scopes are enabled

### "The OAuth client was not found"
- Make sure you selected "Desktop app" as the application type
- Try creating a new OAuth client ID

### `credentials.json` not found
- Make sure you downloaded the JSON file
- Make sure it's named exactly `credentials.json`
- Make sure it's in the project root (same directory as `email_server.py`)

### Browser doesn't open during authentication
- Check your terminal for a URL you can manually copy and paste
- Make sure no firewall is blocking local ports

## Security Notes

- **Never commit `credentials.json` or `token.json` to git** (already in `.gitignore`)
- These files contain secrets that give access to your Gmail account
- `credentials.json` - Your OAuth client credentials
- `token.json` - Your personal access token (created after first auth)
- If compromised, revoke access in [Google Account Security](https://myaccount.google.com/permissions)

## Next Steps

Once you have `credentials.json`:
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server (will trigger first-time OAuth flow)
3. Configure Claude Desktop to use this MCP server

---

**Need help?** Check the [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python) for more details.
