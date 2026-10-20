# Project Constitution: Autonomous AI Email Agent

## Core Principles

### 1. Spec-First & High Context Integrity
- Every feature, behavioral rule, and categorization policy must be explicitly specified in `specs/email-agent/` before execution.
- No code shall be generated without an approved specification and task breakdown.

### 2. Zero-Trust Security & Privacy
- **Strictly No Hardcoded Secrets:** Credentials (`GMAIL_USER`, `GMAIL_APP_PASSWORD`, `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) MUST reside in `.env`.
- `.env` must be added to `.gitignore`.
- Raw email credentials or sensitive personal email content must never be logged to external public servers.

### 3. Human-in-the-Loop Supremacy
- The agent is an intelligence and triage assistant, NOT an autonomous email sender.
- **NO automated email replies** are sent to clients or relatives without explicit human action.
- Crucial notifications (Client and Relative/Friend emails) must be surfaced immediately to the user via Telegram.

### 4. Zero Data Loss & Fault Tolerance
- Unprocessed or unhandled exceptions must never cause the background service to terminate silently.
- Automatic reconnection with exponential backoff on IMAP/network dropouts.
- SQLite database guarantees idempotency (`message_id` tracking) so no duplicate alerts are ever triggered.
