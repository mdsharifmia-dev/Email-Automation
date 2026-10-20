#!/usr/bin/env python3
import sys
import logging
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import Config
from src.agent import EmailAgent
from src.db import Database

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("agent.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("Main")


def main():
    parser = argparse.ArgumentParser(description="Autonomous AI Email Agent for MD Sharif Mia")
    parser.add_argument("--once", action="store_true", help="Run a single email check cycle and exit")
    parser.add_argument("--interval", type=int, default=Config.CHECK_INTERVAL, help="Polling interval in seconds (default: 60)")
    parser.add_argument("--status", action="store_true", help="Display stats of processed emails")
    args = parser.parse_args()

    # Check status
    if args.status:
        db = Database()
        stats = db.get_stats()
        print("\n📊 === AI Email Agent Statistics ===")
        print(f"Total Processed Emails: {stats['total']}")
        print("By Category:")
        for cat, cnt in stats.get("by_category", {}).items():
            print(f"  - {cat.capitalize()}: {cnt}")
        print("=====================================\n")
        return

    # Configuration validation
    missing = Config.validate(check_gmail=True)
    if missing:
        if "GMAIL_APP_PASSWORD" in missing:
            print("\n" + "=" * 60)
            print("⚠️  GMAIL_APP_PASSWORD প্রয়োজন!")
            print("=" * 60)
            print("আপনার জিমেইল পড়ার জন্য গুগলের ১৬ অক্ষরের App Password প্রয়োজন।")
            print("১. ব্রাউজারে যান: https://myaccount.google.com/apppasswords")
            print("২. নাম দিন: EmailAgent এবং Create চাপুন।")
            print("৩. পাওয়া ১৬ অক্ষরের কোডটি .env ফাইলে GMAIL_APP_PASSWORD= ঘরে বসিয়ে দিন।")
            print("=" * 60 + "\n")
            sys.exit(1)
        else:
            logger.error(f"Missing required configuration settings in .env: {', '.join(missing)}")
            sys.exit(1)

    agent = EmailAgent()

    if args.once:
        logger.info("[Main] Running single check cycle (--once)...")
        count = agent.process_cycle()
        logger.info(f"[Main] Completed single cycle. Processed {count} new email(s).")
    else:
        logger.info(f"[Main] Starting AI Email Agent continuous daemon (Interval: {args.interval}s)...")
        agent.run_forever(interval_seconds=args.interval)


if __name__ == "__main__":
    main()
