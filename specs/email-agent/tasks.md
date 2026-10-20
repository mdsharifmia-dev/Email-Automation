# Implementation Tasks: AI Email Agent

## Phase 1: Environment & Foundations
- [x] Task 1.1: Create `requirements.txt` (`requests`, `python-dotenv`)
- [x] Task 1.2: Create `.env.example` with clear documentation
- [x] Task 1.3: Create `.gitignore` to prevent any credential leakage (`.env`, `data/`, `__pycache__/`)
- [x] Task 1.4: Implement `src/config.py` with environment variable loading and validation

## Phase 2: Database & Storage
- [x] Task 2.1: Implement `src/db.py` SQLite database manager (idempotency checks, insert, query)
- [x] Task 2.2: Unit test database storage and duplicate suppression

## Phase 3: Email Ingestion & Parsing
- [x] Task 3.1: Implement `src/email_parser.py` (MIME decode, text/plain vs text/html extraction, attachment detection)
- [x] Task 3.2: Implement `src/email_client.py` (IMAP SSL connection, unread fetcher, auto-reconnection loop)

## Phase 4: AI Intelligence & Classification
- [x] Task 4.1: Implement `src/ai_brain.py` (Gemini API integration with JSON output schema and prompt for client vs relative vs professional)
- [x] Task 4.2: Verify AI categorization and fallback behavior

## Phase 5: Telegram Notification Dispatcher
- [x] Task 5.1: Implement `src/notifier.py` with custom formatting for Client vs Relative alerts
- [x] Task 5.2: Test Telegram notification delivery

## Phase 6: Orchestration & Service Scripts
- [x] Task 6.1: Implement `run_agent.py` continuous daemon loop
- [x] Task 6.2: Create `start.sh` and `stop.sh` bash scripts for background process management
- [x] Task 6.3: End-to-end integration test with live email
