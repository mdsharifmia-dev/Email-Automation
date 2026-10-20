import json
import re
import urllib.request
import urllib.error
import logging
from typing import Dict, Any, List
from src.config import Config

logger = logging.getLogger(__name__)

# Automated system senders and domains
AUTOMATED_PATTERNS = [
    r"no-?reply",
    r"notification",
    r"security@",
    r"alert@",
    r"support@",
    r"billing@",
    r"newsletter",
    r"updates@",
    r"facebookmail\.com",
    r"accounts\.google\.com",
    r"google\.com",
    r"meta\.com",
    r"instagram\.com",
    r"github\.com",
    r"canva\.com",
    r"nvidia\.com",
    r"make\.com",
    r"openrouter\.ai",
]

SECURITY_KEYWORDS = [
    "security",
    "login",
    "log in",
    "logged in",
    "device",
    "password",
    "verification",
    "verify",
    "2-step",
    "two-step",
    "alert",
    "unrecognized",
    "suspicious",
    "code",
    "otp",
    "sign-in",
    "signin",
    "sign in",
]


def is_automated_sender(sender_email: str) -> bool:
    """Check if an email originates from an automated platform or bot."""
    email_clean = (sender_email or "").lower()
    for pattern in AUTOMATED_PATTERNS:
        if re.search(pattern, email_clean):
            return True
    return False


def is_security_notice(subject: str, body: str) -> bool:
    """Check if subject or body contains account security warning triggers."""
    text = f"{subject} {body[:500]}".lower()
    return any(k in text for k in SECURITY_KEYWORDS)


class AIBrain:
    """Uses Google Gemini API to categorize emails and generate intelligent summaries & drafts."""

    MODELS: List[str] = [
        "gemini-3-flash-preview",
        "gemini-3.8-flash",
        "gemini-flash-latest",
        "gemini-2.5-flash"
    ]

    def __init__(self, api_key: str = None):
        self.api_key = api_key or Config.GEMINI_API_KEY

    def analyze_email(self, sender_name: str, sender_email: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Analyze email content and return:
        - category: 'client' | 'relative' | 'security' | 'professional'
        - priority: 'high' | 'medium' | 'low'
        - summary: Bengali 1-2 line summary of what the email is about
        - suggested_reply: Suggested professional reply draft if client, otherwise empty
        """
        automated = is_automated_sender(sender_email)
        security_signal = is_security_notice(subject, body)

        # Pre-filter: If it is an automated sender with security keywords, it is definitely a security alert
        if automated and security_signal:
            return {
                "category": "security",
                "priority": "high",
                "summary": f"{sender_name} থেকে অ্যাকাউন্ট সিকিউরিটি/লগইন অ্যালার্ট এসেছে: {subject}",
                "suggested_reply": "",
            }

        prompt = f"""
You are an intelligent executive email assistant for MD Sharif Mia.
Analyze this incoming email carefully:

From Name: {sender_name}
From Email: {sender_email}
Subject: {subject}
Body:
{body[:3500]}

Categorization Rules:
1. 'client': Real human clients asking for work, business inquiries, project proposals, hiring, technical questions, price requests, contracts.
   CRITICAL: Automated platforms, social media, or no-reply addresses are NEVER clients.
2. 'relative': Personal friends, family members, relatives, personal greetings.
3. 'security': Critical account security alerts, new device login warnings, OTP/2FA verification codes, password change notices from Facebook, Google, Meta, GitHub, bank, etc.
4. 'professional': General marketing ads, newsletters, promotions, platform digests, non-urgent transactional receipts.

Respond ONLY with a valid JSON object (without markdown code fences or backticks):
{{
  "category": "client" | "relative" | "security" | "professional",
  "priority": "high" | "medium" | "low",
  "summary": "ইমেইলটির মূল কথা সংক্ষেপে বাংলায় ১-২ লাইনে লিখুন",
  "suggested_reply": "যদি category 'client' হয়, তবে ক্লায়েন্টের জন্য একটি মার্জিত ও পেশাদার খসড়া (Draft) রিপ্লাই তৈরি করুন। অন্যথায় এটি খালি স্ট্রিং রাখুন।"
}}
"""

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        req_data = json.dumps(payload).encode("utf-8")

        for model_name in self.MODELS:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=req_data,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=12) as response:
                    resp_json = json.loads(response.read().decode("utf-8"))
                    candidate = resp_json.get("candidates", [{}])[0]
                    content_text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "{}")

                    clean_json_str = re.sub(r"^```json\s*", "", content_text.strip(), flags=re.IGNORECASE)
                    clean_json_str = re.sub(r"^```\s*", "", clean_json_str)
                    clean_json_str = re.sub(r"```$", "", clean_json_str.strip())

                    result = json.loads(clean_json_str)
                    cat = str(result.get("category", "professional")).lower().strip()

                    if "security" in cat or (automated and security_signal):
                        category = "security"
                    elif "client" in cat and not automated:
                        category = "client"
                    elif "relative" in cat or "friend" in cat:
                        category = "relative"
                    else:
                        category = "professional"

                    return {
                        "category": category,
                        "priority": result.get("priority", "medium"),
                        "summary": result.get("summary", "ইমেইলের মূল বিষয়বস্তু পর্যালোচনা প্রয়োজন।"),
                        "suggested_reply": result.get("suggested_reply", "").strip() if category == "client" else "",
                    }

            except urllib.error.HTTPError as e:
                logger.warning(f"[AIBrain] Model {model_name} HTTP {e.code}, trying fallback model...")
                continue
            except Exception as e:
                logger.warning(f"[AIBrain] Model {model_name} error: {e}, trying fallback model...")
                continue

        # Smart fallback if all Gemini models fail or timeout
        logger.error("[AIBrain] All Gemini models failed or timed out. Using safe rule-based fallback.")
        if security_signal:
            return {
                "category": "security",
                "priority": "high",
                "summary": f"অ্যাকাউন্ট সিকিউরিটি সংক্রান্ত সতর্কতা: {subject}",
                "suggested_reply": "",
            }

        if automated:
            return {
                "category": "professional",
                "priority": "low",
                "summary": f"অটোমেটেড প্ল্যাটফর্ম নোটিফিকেশন: {subject}",
                "suggested_reply": "",
            }

        # If from a human email address, safe client notification
        return {
            "category": "client",
            "priority": "medium",
            "summary": f"ইমেইল এসেছে: {subject}",
            "suggested_reply": "Thank you for reaching out. I have received your email and will get back to you shortly.",
        }
