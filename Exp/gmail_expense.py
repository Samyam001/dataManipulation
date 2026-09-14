#!/usr/bin/env python3
"""
Gmail Expense Calculator
------------------------
Connects directly to your Gmail account via the Gmail API, searches for
statement/transaction emails, extracts the text, and runs it through the
same parsing/categorizing logic as expense_calculator.py.

ONE-TIME SETUP (takes about 5 minutes):

1. Go to https://console.cloud.google.com/
2. Create a new project (or use an existing one)
3. Enable the "Gmail API" for that project:
   APIs & Services -> Library -> search "Gmail API" -> Enable
4. Create credentials:
   APIs & Services -> Credentials -> Create Credentials -> OAuth client ID
     - Application type: Desktop app
     - Name it anything, e.g. "Expense Calculator"
5. Download the resulting JSON file, rename it to "credentials.json",
   and place it in the SAME FOLDER as this script.
6. Install the required packages:
     pip install --upgrade google-auth-oauthlib google-auth-httplib2 google-api-python-client

FIRST RUN:
  python3 gmail_expense_calculator.py
  - A browser window will open asking you to log in to Google and approve
    access. This creates a "token.json" file so you won't have to log in
    again on future runs (until the token expires).

USAGE:
  python3 gmail_expense_calculator.py                     # uses default search (see SEARCH_QUERY below)
  python3 gmail_expense_calculator.py --query "from:chase.com subject:statement"
  python3 gmail_expense_calculator.py --days 30            # only look at last 30 days
  python3 gmail_expense_calculator.py --max 5               # check up to 5 matching emails

WHAT IT SEARCHES FOR BY DEFAULT:
  Emails from the last 90 days whose subject contains "statement" OR
  "transaction" OR "account summary". Edit SEARCH_QUERY below to match
  your bank's actual subject lines/sender address for better results.
"""

import argparse
import base64
import os
import re
import sys
from datetime import datetime, timedelta

# Reuse the parsing/categorizing/report logic from the other script.
# Keep expense_calculator.py in the same folder.
from expenses import parse_statement, print_report

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("Missing required packages. Install them with:\n")
    print("  pip install --upgrade google-auth-oauthlib google-auth-httplib2 "
          "google-api-python-client")
    sys.exit(1)


# Gmail API scope: read-only access to your mail (cannot send/delete anything)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

# Default search - EDIT THIS to match your bank's emails, e.g.:
#   "from:alerts@chase.com subject:statement"
#   "from:americanexpress.com"
DEFAULT_SEARCH_QUERY = "subject:(statement OR transaction OR \"account summary\")"


def get_gmail_service():
    """Authenticate and return an authorized Gmail API client."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"Missing '{CREDENTIALS_FILE}'. See the setup steps "
                      "at the top of this script.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def search_messages(service, query: str, max_results: int):
    """Return a list of message IDs matching the Gmail search query."""
    results = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()
    return results.get("messages", [])


def extract_plain_text(payload) -> str:
    """
    Recursively walk a Gmail message payload and pull out the best
    available plain-text (or HTML, stripped of tags) content.
    """
    text_parts = []

    def walk(part):
        mime_type = part.get("mimeType", "")
        body = part.get("body", {})
        data = body.get("data")

        if mime_type == "text/plain" and data:
            decoded = base64.urlsafe_b64decode(data).decode("utf-8", "ignore")
            text_parts.append(decoded)
        elif mime_type == "text/html" and data and not text_parts:
            decoded = base64.urlsafe_b64decode(data).decode("utf-8", "ignore")
            # crude tag strip - good enough for pulling out amounts/dates
            stripped = re.sub(r"<[^>]+>", " ", decoded)
            stripped = re.sub(r"&nbsp;|&amp;|&#39;", " ", stripped)
            text_parts.append(stripped)

        for sub_part in part.get("parts", []):
            walk(sub_part)

    walk(payload)
    return "\n".join(text_parts)


def fetch_statement_text(service, query: str, max_results: int) -> str:
    """Fetch matching emails and concatenate their extracted text."""
    messages = search_messages(service, query, max_results)

    if not messages:
        print(f"No emails found matching: {query}")
        return ""

    print(f"Found {len(messages)} matching email(s). Fetching content...\n")

    combined_text = []
    for msg_ref in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
        subject = headers.get("Subject", "(no subject)")
        sender = headers.get("From", "(unknown sender)")
        print(f"  - {subject}  [{sender}]")

        body_text = extract_plain_text(msg["payload"])
        combined_text.append(body_text)

    return "\n\n".join(combined_text)


def main():
    parser = argparse.ArgumentParser(description="Fetch and parse statement emails from Gmail.")
    parser.add_argument("--query", default=DEFAULT_SEARCH_QUERY,
                         help="Gmail search query (same syntax as the Gmail search bar)")
    parser.add_argument("--days", type=int, default=90,
                         help="Only look at emails from the last N days (default: 90)")
    parser.add_argument("--max", type=int, default=10,
                         help="Max number of matching emails to fetch (default: 10)")
    args = parser.parse_args()

    since_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y/%m/%d")
    full_query = f"{args.query} after:{since_date}"

    print(f"Searching Gmail for: {full_query}\n")

    service = get_gmail_service()
    text = fetch_statement_text(service, full_query, args.max)

    if not text.strip():
        return

    transactions = parse_statement(text)
    print()
    print_report(transactions)


if __name__ == "__main__":
    main()