import imaplib
import time
import logging
from typing import List, Dict, Any, Optional
from src.config import Config
from src.email_parser import parse_email_message

logger = logging.getLogger(__name__)


class EmailClient:
    """IMAP client to monitor and fetch incoming unread emails from Gmail."""

    def __init__(self):
        self.server_host = Config.IMAP_SERVER
        self.server_port = Config.IMAP_PORT
        self.user = Config.GMAIL_USER
        self.password = Config.GMAIL_APP_PASSWORD
        self.client: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> bool:
        """Establish SSL connection to Gmail IMAP server and login."""
        if not self.user or not self.password:
            logger.error("[EmailClient] GMAIL_USER or GMAIL_APP_PASSWORD is not set!")
            return False

        try:
            logger.info(f"[EmailClient] Connecting to {self.server_host}:{self.server_port}...")
            self.client = imaplib.IMAP4_SSL(self.server_host, self.server_port)
            self.client.login(self.user, self.password)
            logger.info("[EmailClient] Successfully authenticated with Gmail IMAP.")
            return True
        except imaplib.IMAP4.error as e:
            logger.error(f"[EmailClient] IMAP Authentication failed: {e}")
            self.client = None
            return False
        except Exception as e:
            logger.error(f"[EmailClient] Failed to connect: {e}")
            self.client = None
            return False

    def is_connected(self) -> bool:
        """Check if IMAP connection is alive."""
        if not self.client:
            return False
        try:
            status, _ = self.client.noop()
            return status == "OK"
        except Exception:
            return False

    def ensure_connection(self) -> bool:
        """Ensure connection is healthy, reconnecting if necessary with backoff."""
        if self.is_connected():
            return True

        logger.warning("[EmailClient] Connection dropped or not established. Reconnecting...")
        for attempt in range(1, 4):
            if self.connect():
                return True
            wait_time = attempt * 5
            logger.info(f"[EmailClient] Retrying connection in {wait_time}s (attempt {attempt}/3)...")
            time.sleep(wait_time)
        return False

    def fetch_unread_emails(self, max_count: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch unread emails from INBOX.
        Uses BODY.PEEK[] so messages remain UNREAD in Gmail for user visibility!
        """
        if not self.ensure_connection():
            return []

        messages: List[Dict[str, Any]] = []
        try:
            # Select INBOX in read-write mode (or readonly)
            status, _ = self.client.select("INBOX", readonly=False)
            if status != "OK":
                logger.error("[EmailClient] Failed to select INBOX.")
                return []

            # Search for unread messages
            status, search_data = self.client.search(None, "UNSEEN")
            if status != "OK" or not search_data or not search_data[0]:
                return []

            email_ids = search_data[0].split()
            # Fetch latest first, up to max_count
            email_ids = email_ids[-max_count:]

            for eid in reversed(email_ids):
                try:
                    # BODY.PEEK[] ensures Gmail keeps the message UNSEEN (unread)
                    fetch_status, fetch_data = self.client.fetch(eid, "(BODY.PEEK[])")
                    if fetch_status != "OK" or not fetch_data:
                        continue

                    raw_bytes = None
                    for part in fetch_data:
                        if isinstance(part, tuple) and len(part) >= 2:
                            raw_bytes = part[1]
                            break

                    if raw_bytes:
                        parsed = parse_email_message(raw_bytes)
                        parsed["imap_id"] = eid.decode() if isinstance(eid, bytes) else str(eid)
                        # Fallback for empty message_id
                        if not parsed["message_id"]:
                            parsed["message_id"] = f"imap_{parsed['imap_id']}_{parsed['date']}"
                        messages.append(parsed)

                except Exception as e:
                    logger.error(f"[EmailClient] Error parsing message {eid}: {e}")

        except Exception as e:
            logger.error(f"[EmailClient] Error during fetch_unread_emails: {e}")
            self.client = None

        return messages

    def close(self):
        """Gracefully close IMAP connection."""
        if self.client:
            try:
                self.client.close()
                self.client.logout()
            except Exception:
                pass
            finally:
                self.client = None
