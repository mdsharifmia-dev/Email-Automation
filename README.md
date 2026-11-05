# Autonomous AI Email Agent for Md Sharif Mia

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Google Gemini](https://img.shields.io/badge/AI_Engine-Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Telegram](https://img.shields.io/badge/Alerts-Telegram_Bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org)
[![Security: Zero-Trust](https://img.shields.io/badge/Security-Zero--Trust_IMAP-green?style=for-the-badge&logo=auth0&logoColor=white)](https://github.com/mdsharifmia-dev/Email-Automation)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**An autonomous background AI email intelligence assistant with zero external pip dependencies.**  
*IMAP SSL • BODY.PEEK Safety • Multi-Model Fallback • Telegram Dispatch • SQLite Idempotency*

</div>

---

## Core Capabilities & Policy Routing

| Category | AI Role | Telegram Dispatch |
| :--- | :--- | :--- |
| **Client Inquiries** | Deep context analysis with intelligent proposed reply draft. Zero blind auto-replies. | **Urgent Priority:** Sender, subject, attachment metadata, structured Bengali summary, and ready-to-use proposed response draft. |
| **Friends & Family** | Relationship-preserving classification with natural human warmth. Zero robotic automated templates. | **Notification:** Personalized notice indicating sender, subject, and essential message overview. |
| **Newsletters & Promotions** | High-precision classification filtering marketing digests, newsletters, and social blasts. | **Suppressed:** Completely muted without distracting alerts. |

---

## Project Structure & File Map

```text
Email-Automation/
├── .env                  # Environment configuration (Gmail, Gemini API Key, Telegram Bot)
├── .env.example          # Sanitized configuration template (zero credentials)
├── .gitignore            # Strict isolation rules
├── data/
│   └── emails.db         # Embedded SQLite database for idempotency & deduplication
├── specs/                # Spec-Kit specifications & task checklists
│   └── email-agent/
│       ├── spec.md       # Requirements specification
│       ├── plan.md       # Technical architecture
│       └── tasks.md      # Implementation tasks
├── src/
│   ├── config.py         # Environment validation
│   ├── db.py             # SQLite storage & idempotency tracker
│   ├── email_parser.py   # MIME & RFC822 parser with attachment inspection
│   ├── email_client.py   # IMAP SSL client with BODY.PEEK inbox safety
│   ├── ai_brain.py       # Google Gemini AI engine with multi-model fallback
│   ├── notifier.py       # Telegram notification dispatcher with HTML formatting
│   └── agent.py          # Central orchestrator & daemon loop
├── run_agent.py          # Command-line entrypoint & CLI flags
├── start.sh              # Background daemon startup script
└── stop.sh               # Background daemon shutdown script
```

---

## Quick Start & Installation

### 1. Configure Gmail App Password
1. Navigate to [Google Account App Passwords](https://myaccount.google.com/apppasswords).
2. Create an App Password for `EmailAgent`.
3. Copy the 16-character code into `.env`:
   ```env
   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

### 2. Execution Modes

- **Start Background Daemon:**
  ```bash
  ./start.sh
  ```
- **Single Run (--once mode):**
  ```bash
  python3 run_agent.py --once
  ```
- **Inspect Processing Statistics:**
  ```bash
  python3 run_agent.py --status
  ```
- **Stop Background Daemon:**
  ```bash
  ./stop.sh
  ```

---

## Security & Reliability Standards
1. **Zero External Pip Dependencies:** Built entirely with Python's standard library (`imaplib`, `urllib`, `sqlite3`, `email`). Zero dependency drift or version conflicts.
2. **Gmail Inbox Safety:** Reads emails using `BODY.PEEK[]` flags, keeping messages marked unread in Gmail for normal personal viewing.
3. **Strict Idempotency:** The local SQLite database tracks every processed `Message-ID`, guaranteeing zero duplicate notifications.

---

## Engineering & Contact

- **Developer:** [Md Sharif Mia](https://github.com/mdsharifmia-dev)
- **Email:** [mdsharifmia.dev@gmail.com](mailto:mdsharifmia.dev@gmail.com)
- **GitHub:** [github.com/mdsharifmia-dev](https://github.com/mdsharifmia-dev)
