import requests
from django.conf import settings


def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    try:
        requests.post(url, json=payload, timeout=5)
    except requests.RequestException:
        pass