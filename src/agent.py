import time
import logging
from typing import Dict, Any
from src.config import Config
from src.db import Database
from src.email_client import EmailClient
from src.ai_brain import AIBrain
from src.notifier import TelegramNotifier

logger = logging.getLogger(__name__)


class EmailAgent:
    """Core autonomous agent coordinating email ingestion, AI classification, and Telegram alerting."""

    def __init__(self):
        self.db = Database()
        self.client = EmailClient()
        self.brain = AIBrain()
        self.notifier = TelegramNotifier()
        self.running = False

    def process_cycle(self) -> int:
        """Execute one complete scan and triage cycle. Returns count of new emails processed."""
        unread_emails = self.client.fetch_unread_emails()
        if not unread_emails:
            return 0

        processed_count = 0
        logger.info(f"[Agent] Found {len(unread_emails)} unread emails. Evaluating with AI...")

        for item in unread_emails:
            msg_id = item["message_id"]

            # Idempotency check: prevent duplicate processing
            if self.db.is_processed(msg_id):
                continue

            from_name = item["from_name"]
            from_email = item["from_email"]
            subject = item["subject"]
            body = item["body"]
            attachments = item.get("attachments", [])
            has_attachment = item.get("has_attachment", False)

            logger.info(f"[Agent] Processing email from '{from_name}' <{from_email}>: '{subject}'")

            # AI Analysis
            analysis = self.brain.analyze_email(from_name, from_email, subject, body)
            category = analysis.get("category", "professional")
            summary = analysis.get("summary", "")
            suggested_reply = analysis.get("suggested_reply", "")

            # Action Routing
            if category == "client":
                logger.info(f"[Agent] Category: CLIENT -> Sending instant Telegram alert with suggested draft.")
                self.notifier.send_client_alert(
                    sender_name=from_name,
                    sender_email=from_email,
                    subject=subject,
                    summary=summary,
                    suggested_reply=suggested_reply,
                    attachments=attachments,
                )

            elif category == "relative":
                logger.info(f"[Agent] Category: RELATIVE/FRIEND -> Sending Telegram notification.")
                self.notifier.send_relative_notification(
                    sender_name=from_name,
                    sender_email=from_email,
                    subject=subject,
                    summary=summary,
                    attachments=attachments,
                )

            elif category == "security":
                logger.info(f"[Agent] Category: SECURITY -> Sending explicit Security Alert to Telegram.")
                self.notifier.send_security_alert(
                    sender_name=from_name,
                    sender_email=from_email,
                    subject=subject,
                    summary=summary,
                )

            else:
                logger.info(f"[Agent] Category: PROFESSIONAL/MARKETING -> Muted (no notification sent).")

            # Record in SQLite database
            self.db.mark_processed(
                message_id=msg_id,
                sender=from_email,
                sender_name=from_name,
                subject=subject,
                category=category,
                summary=summary,
                has_attachment=has_attachment,
            )
            processed_count += 1
            time.sleep(1.5)

        return processed_count

    def run_forever(self, interval_seconds: int = None):
        """Continuously run the agent daemon loop."""
        interval = interval_seconds or Config.CHECK_INTERVAL
        self.running = True
        logger.info(f"[Agent] Started AI Email Agent loop. Polling interval: {interval}s.")

        try:
            while self.running:
                try:
                    new_count = self.process_cycle()
                    if new_count > 0:
                        logger.info(f"[Agent] Cycle finished. Processed {new_count} new email(s).")
                except Exception as e:
                    logger.error(f"[Agent] Unexpected error during cycle: {e}")

                time.sleep(interval)
        except (KeyboardInterrupt, SystemExit):
            logger.info("[Agent] Stopping agent service gracefully...")
        finally:
            self.client.close()
            logger.info("[Agent] Agent stopped.")

    def stop(self):
        """Signal agent to stop."""
        self.running = False
