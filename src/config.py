import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(filepath: Path) -> None:
    """Zero-dependency .env loader."""
    if not filepath.exists():
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = val
    except Exception as e:
        print(f"[Config] Warning loading .env: {e}")


# Load .env file
load_env_file(BASE_DIR / ".env")


class Config:
    """Application configuration loaded from environment variables."""

    # Gmail Credentials
    GMAIL_USER = os.getenv("GMAIL_USER", "").strip()
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip().replace(" ", "")

    # Gemini AI
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    # IMAP Configuration
    IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com").strip()
    IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))

    # Database
    DATA_DIR = BASE_DIR / "data"
    DB_PATH = DATA_DIR / "emails.db"

    @classmethod
    def validate(cls, check_gmail: bool = True) -> list[str]:
        """Validate required configuration values. Returns list of missing settings."""
        missing = []
        if check_gmail:
            if not cls.GMAIL_USER:
                missing.append("GMAIL_USER")
            if not cls.GMAIL_APP_PASSWORD:
                missing.append("GMAIL_APP_PASSWORD")
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not cls.TELEGRAM_CHAT_ID:
            missing.append("TELEGRAM_CHAT_ID")
        return missing
