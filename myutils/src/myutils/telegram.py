import os

import httpx


def send_telegram(body: str, chat_id: int = int(os.environ.get("TELEGRAM_CHAT_ID", 1))) -> None:
    # replace breaks with line breaks suitable for Telegram
    body = body.replace("<br/>", chr(10)).replace("<br>", chr(10))

    url = f"https://api.telegram.org/{os.environ.get('TELEGRAM_API_KEY')}/sendMessage"
    data = {"chat_id": chat_id, "parse_mode": "HTML", "text": body, "disable_web_page_preview": 1}
    httpx.post(url, data=data)
