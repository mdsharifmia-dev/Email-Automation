import sqlite3
from typing import Optional, List, Dict, Any
from src.config import Config


class Database:
    """Manages SQLite storage for tracking processed emails and avoiding duplicates."""

    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DB_PATH
        self.ensure_dir()
        self.init_db()

    def ensure_dir(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_emails (
                    message_id TEXT PRIMARY KEY,
                    sender TEXT,
                    sender_name TEXT,
                    subject TEXT,
                    category TEXT,
                    summary TEXT,
                    has_attachment INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

    def is_processed(self, message_id: str) -> bool:
        """Check if an email message ID has already been handled."""
        if not message_id:
            return False
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM processed_emails WHERE message_id = ?", (message_id,))
            return cursor.fetchone() is not None

    def mark_processed(
        self,
        message_id: str,
        sender: str,
        sender_name: str,
        subject: str,
        category: str,
        summary: str,
        has_attachment: bool = False,
    ) -> None:
        """Save processed email to prevent duplicate alerts/replies."""
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO processed_emails 
                (message_id, sender, sender_name, subject, category, summary, has_attachment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    sender,
                    sender_name,
                    subject,
                    category,
                    summary,
                    1 if has_attachment else 0,
                ),
            )
            conn.commit()

    def get_stats(self) -> Dict[str, int]:
        """Get summary statistics of processed emails."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM processed_emails")
            total = cursor.fetchone()["total"]

            cursor.execute("SELECT category, COUNT(*) as count FROM processed_emails GROUP BY category")
            category_counts = {row["category"]: row["count"] for row in cursor.fetchall()}

            return {"total": total, "by_category": category_counts}
