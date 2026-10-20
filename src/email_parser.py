import re
import email
from email.header import decode_header
from email.message import Message
from typing import Dict, Any, List


def decode_mime_words(header_value: str) -> str:
    """Decode encoded MIME header strings (e.g. =?UTF-8?B?...?=)."""
    if not header_value:
        return ""
    decoded_fragments = []
    for fragment, charset in decode_header(header_value):
        if isinstance(fragment, bytes):
            try:
                decoded_fragments.append(fragment.decode(charset or "utf-8", errors="replace"))
            except (LookupError, UnicodeDecodeError):
                decoded_fragments.append(fragment.decode("utf-8", errors="replace"))
        else:
            decoded_fragments.append(str(fragment))
    return "".join(decoded_fragments).strip()


def strip_html_tags(html: str) -> str:
    """Simple regex HTML stripper to convert HTML email body to readable text."""
    clean = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r"<script[^>]*>.*?</script>", "", clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r"<br\s*/?>", "\n", clean, flags=re.IGNORECASE)
    clean = re.sub(r"</p>", "\n\n", clean, flags=re.IGNORECASE)
    clean = re.sub(r"<[^>]+>", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def parse_email_message(raw_bytes: bytes) -> Dict[str, Any]:
    """Parse raw RFC822 email bytes into a clean, structured dictionary."""
    msg = email.message_from_bytes(raw_bytes)

    # 1. Message ID
    message_id = msg.get("Message-ID", "").strip()

    # 2. Subject
    subject = decode_mime_words(msg.get("Subject", "(No Subject)"))

    # 3. From header
    from_raw = decode_mime_words(msg.get("From", ""))
    from_name, from_email = email.utils.parseaddr(from_raw)
    if not from_name:
        from_name = from_email

    # 4. Date
    date_str = msg.get("Date", "")

    # 5. Extract body and attachments
    plain_body = ""
    html_body = ""
    attachments: List[str] = []

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            # Check for attachments
            filename = part.get_filename()
            if filename:
                filename = decode_mime_words(filename)
                attachments.append(filename)
            elif "attachment" in content_disposition.lower():
                attachments.append("unnamed_attachment")

            # Check for text body
            if "attachment" not in content_disposition.lower():
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        text = payload.decode(charset, errors="replace")
                    except (LookupError, UnicodeDecodeError):
                        text = payload.decode("utf-8", errors="replace")

                    if content_type == "text/plain" and not plain_body:
                        plain_body = text
                    elif content_type == "text/html" and not html_body:
                        html_body = text
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            try:
                text = payload.decode(charset, errors="replace")
            except (LookupError, UnicodeDecodeError):
                text = payload.decode("utf-8", errors="replace")

            if msg.get_content_type() == "text/plain":
                plain_body = text
            elif msg.get_content_type() == "text/html":
                html_body = text

    # Select best text representation
    final_body = plain_body.strip()
    if not final_body and html_body:
        final_body = strip_html_tags(html_body)

    # Limit body text size for Gemini context (max 6000 chars)
    if len(final_body) > 6000:
        final_body = final_body[:6000] + "\n...[truncated]..."

    return {
        "message_id": message_id,
        "from_email": from_email,
        "from_name": from_name,
        "subject": subject,
        "date": date_str,
        "body": final_body,
        "attachments": attachments,
        "has_attachment": len(attachments) > 0,
    }
