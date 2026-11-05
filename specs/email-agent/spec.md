# Functional Specification: AI Email Agent

## 1. Feature Overview
A dedicated Python service that continuously monitors Gmail for unread messages, leverages Google Gemini AI to classify each message, and dispatches real-time Telegram alerts tailored to the category of the message.

---

## 2. User Scenarios & Acceptance Criteria

### Scenario 1: Client Email Received
- **Given** an unread email from a potential client, client domain, or containing project/business inquiries arrives.
- **When** the agent processes the email.
- **Then**:
  1. The agent classifies it as `client`.
  2. The agent generates a concise 2-line Bengali summary of the client's request/inquiry.
  3. The agent prepares a professional suggested draft reply.
  4. The agent dispatches an immediate Telegram alert with:
     -  Header indicating Client Email.
     - Sender Name & Email.
     - Subject.
     -  Attachment indicator (if any files are attached).
     -  Bengali Summary.
     - ️ Suggested Reply Draft.
  5. The email is recorded in the SQLite database.
  6. The email remains unread/marked safely in Gmail for Sharif to reply personally.

### Scenario 2: Friend or Relative Email Received
- **Given** an unread email from a friend, family member, or personal contact arrives.
- **When** the agent processes the email.
- **Then**:
  1. The agent classifies it as `relative`.
  2. The agent does NOT send any auto-reply.
  3. The agent dispatches an immediate Telegram alert:
     -  Header: *"আপনার বন্ধু বা রিলেটিভ একটি মেইল পাঠিয়েছেন!"*
     - Sender Name & Email.
     - Subject.
     -  Summary in Bengali.
  4. The email is recorded in the SQLite database.

### Scenario 3: Professional / Marketing / Newsletter / Ad Email Received
- **Given** a promotional email, newsletter, marketing pitch, or automated transactional alert arrives.
- **When** the agent processes the email.
- **Then**:
  1. The agent classifies it as `professional` / `promotional`.
  2. The agent silences the email (NO Telegram alert).
  3. The agent marks it as processed in SQLite.

### Scenario 4: Network Disconnection or Failure
- **Given** a Wi-Fi or network disconnect.
- **When** IMAP connection drops.
- **Then** the agent logs the error, waits with backoff, and automatically reconnects without crashing.

### Scenario 5: Security / Account Alert Received
- **Given** an account security warning, new login notice, OTP, or password alert arrives (e.g. from Facebook, Google, Meta, GitHub).
- **When** the agent processes the email.
- **Then**:
  1. The agent classifies it as `security`.
  2. The agent sends an explicit Telegram alert titled: ` সিকিউরিটি অ্যালার্ট! (Security Alert)` with platform name, subject, and Bengali summary.
  3. No suggested draft reply is generated.
  4. The event is recorded in the SQLite database.
