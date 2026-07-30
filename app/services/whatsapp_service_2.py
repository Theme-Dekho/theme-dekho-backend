import requests

from app.config import (
    MSG91_AUTH_KEY,
    MSG91_INTEGRATED_NUMBER
)

URL = "https://api.msg91.com/api/v5/whatsapp/whatsapp-outbound-message/"


def send_otp(phone: str, otp: str):

    headers = {
        "authkey": MSG91_AUTH_KEY,
        "Content-Type": "application/json"
    }

    payload = {

        "integrated_number": MSG91_INTEGRATED_NUMBER,

        "content_type": "text",

        "payload": {

            "messaging_product": "whatsapp",

            "type": "text",

            "to": phone,

            "text": {

                "body": f"Your OTP is {otp}. It will expire shortly."

            }

        }

    }

    response = requests.post(
        URL,
        headers=headers,
        json=payload,
        timeout=15
    )

    response.raise_for_status()

    return response.json()
