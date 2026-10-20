import html
import json
import urllib.request
import urllib.error
import logging
from typing import List, Optional
from src.config import Config

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Dispatches formatted, real-time alerts to Telegram."""

    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or Config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or Config.TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def _send_message(self, text_html: str) -> bool:
        """Send HTML-formatted message to Telegram."""
        if not self.bot_token or not self.chat_id:
            logger.error("[Notifier] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing!")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": text_html,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.api_url,
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res.get("ok", False)
        except urllib.error.HTTPError as e:
            logger.error(f"[Notifier] Telegram HTTP Error {e.code}: {e.read().decode()}")
            return False
        except Exception as e:
            logger.error(f"[Notifier] Failed to send Telegram alert: {e}")
            return False

    def send_client_alert(
        self,
        sender_name: str,
        sender_email: str,
        subject: str,
        summary: str,
        suggested_reply: str,
        attachments: Optional[List[str]] = None,
    ) -> bool:
        """Send rich alert for incoming Client emails."""
        safe_name = html.escape(sender_name or "Unknown")
        safe_email = html.escape(sender_email or "")
        safe_subject = html.escape(subject or "(No Subject)")
        safe_summary = html.escape(summary or "")
        safe_reply = html.escape(suggested_reply or "")

        att_text = ""
        if attachments:
            clean_atts = [html.escape(a) for a in attachments]
            att_text = f"\n📎 <b>সংযুক্তি:</b> {', '.join(clean_atts)}"

        msg = (
            f"📩 <b>নতুন ক্লায়েন্ট ইমেইল এসেছে!</b>\n\n"
            f"👤 <b>প্রেরক:</b> {safe_name} ({safe_email})\n"
            f"📌 <b>বিষয়:</b> {safe_subject}{att_text}\n\n"
            f"📝 <b>সারসংক্ষেপ:</b>\n{safe_summary}\n\n"
            f"✍️ <b>প্রস্তাবিত ড্রাফট রিপ্লাই:</b>\n<i>\"{safe_reply}\"</i>\n\n"
            f"💡 <i>নোট: আপনার জিমেইল অ্যাপে গিয়ে দেখে-শুনে রিপ্লাই দিতে পারেন।</i>"
        )
        return self._send_message(msg)

    def send_relative_notification(
        self,
        sender_name: str,
        sender_email: str,
        subject: str,
        summary: str,
        attachments: Optional[List[str]] = None,
    ) -> bool:
        """Send notification for friend / family / relative emails."""
        safe_name = html.escape(sender_name or "Unknown")
        safe_email = html.escape(sender_email or "")
        safe_subject = html.escape(subject or "(No Subject)")
        safe_summary = html.escape(summary or "")

        att_text = ""
        if attachments:
            clean_atts = [html.escape(a) for a in attachments]
            att_text = f"\n📎 <b>সংযুক্তি:</b> {', '.join(clean_atts)}"

        msg = (
            f"💌 <b>আপনার বন্ধু বা রিলেটিভ একটি মেইল পাঠিয়েছেন!</b>\n\n"
            f"👤 <b>প্রেরক:</b> {safe_name} ({safe_email})\n"
            f"📌 <b>বিষয়:</b> {safe_subject}{att_text}\n\n"
            f"📝 <b>সারসংক্ষেপ:</b>\n{safe_summary}\n\n"
            f"💡 <i>নোট: কোনো অটো-রিপ্লাই দেওয়া হয়নি। সুবিধামতো যোগাযোগ করুন।</i>"
        )
        return self._send_message(msg)

    def send_security_alert(
        self,
        sender_name: str,
        sender_email: str,
        subject: str,
        summary: str,
    ) -> bool:
        """Send explicit security alert for login, OTP, or account security notices."""
        safe_name = html.escape(sender_name or "Security System")
        safe_email = html.escape(sender_email or "")
        safe_subject = html.escape(subject or "Security Notice")
        safe_summary = html.escape(summary or "")

        msg = (
            f"🚨 <b>সিকিউরিটি অ্যালার্ট! (Security Alert)</b>\n\n"
            f"🛡️ <b>প্ল্যাটফর্ম / প্রেরক:</b> {safe_name} ({safe_email})\n"
            f"📌 <b>বিষয়:</b> {safe_subject}\n\n"
            f"📝 <b>সারসংক্ষেপ:</b>\n{safe_summary}\n\n"
            f"⚠️ <i>সতর্কতা: এটি যদি আপনার দ্বারা না হয়ে থাকে, তবে দ্রুত পাসওয়ার্ড বা নিরাপত্তা যাচাই করুন।</i>"
        )
        return self._send_message(msg)

    def send_system_status(self, text: str) -> bool:
        """Send general system update/health notification."""
        safe_text = html.escape(text)
        return self._send_message(f"⚙️ <b>AI Email Agent Status:</b>\n{safe_text}")
