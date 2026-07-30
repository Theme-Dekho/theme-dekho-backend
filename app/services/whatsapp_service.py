import os
import re
from typing import Any

import requests

from app.config import (
    ACCESS_TOKEN,
    PHONE_NUMBER_ID,
    GRAPH_VERSION,
)

WHATSAPP_TEMPLATE_NAME = os.getenv(
    "WHATSAPP_TEMPLATE_NAME",
    "otp_template",
).strip()

WHATSAPP_TEMPLATE_LANGUAGE = os.getenv(
    "WHATSAPP_TEMPLATE_LANGUAGE",
    "en_US",
).strip()

URL = (
    f"https://graph.facebook.com/"
    f"{GRAPH_VERSION}/"
    f"{PHONE_NUMBER_ID}/messages"
)


class WhatsAppAPIError(RuntimeError):
    """Raised when Meta rejects or cannot process a WhatsApp request."""


def normalize_indian_phone(phone: str) -> str:
    """
    Convert an Indian mobile number into WhatsApp format.

    Accepted input:
    - 8121512131
    - 918121512131
    - +918121512131

    Returned format:
    - 918121512131
    """
    digits = re.sub(r"\D", "", phone)

    if re.fullmatch(r"[6-9]\d{9}", digits):
        return f"91{digits}"

    if re.fullmatch(r"91[6-9]\d{9}", digits):
        return digits

    raise ValueError(
        "Invalid Indian mobile number. "
        "Expected a 10-digit number starting from 6, 7, 8, or 9."
    )


def parse_meta_response(response: requests.Response) -> dict[str, Any]:
    try:
        response_data = response.json()
    except ValueError as error:
        raise WhatsAppAPIError(
            "Meta returned a non-JSON response: "
            f"{response.text or response.status_code}"
        ) from error

    if response.ok:
        return response_data

    meta_error = response_data.get("error", {})

    message = meta_error.get(
        "message",
        "WhatsApp API request failed",
    )

    error_code = meta_error.get("code")
    error_subcode = meta_error.get("error_subcode")

    details = (
        meta_error
        .get("error_data", {})
        .get("details")
    )

    error_parts = [message]

    if error_code is not None:
        error_parts.append(f"code={error_code}")

    if error_subcode is not None:
        error_parts.append(f"subcode={error_subcode}")

    if details:
        error_parts.append(details)

    raise WhatsAppAPIError(" | ".join(error_parts))


def send_otp(phone: str, otp: str) -> dict[str, Any]:
    """
    Send an OTP using an approved WhatsApp authentication template.

    auth.py should call:
        send_whatsapp_otp(data.phone, otp)

    Do not add 91 inside auth.py.
    """
    recipient = normalize_indian_phone(phone)
    otp = str(otp).strip()

    if not re.fullmatch(r"\d{4,6}", otp):
        raise ValueError("OTP must contain 4 to 6 digits.")

    if not ACCESS_TOKEN:
        raise RuntimeError("WHATSAPP_ACCESS_TOKEN is missing.")

    if not PHONE_NUMBER_ID:
        raise RuntimeError("WHATSAPP_PHONE_NUMBER_ID is missing.")

    if not WHATSAPP_TEMPLATE_NAME:
        raise RuntimeError("WHATSAPP_TEMPLATE_NAME is missing.")

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "template",
        "template": {
            "name": WHATSAPP_TEMPLATE_NAME,
            "language": {
                "code": WHATSAPP_TEMPLATE_LANGUAGE,
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": otp,
                        }
                    ],
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        {
                            "type": "text",
                            "text": otp,
                        }
                    ],
                },
            ],
        },
    }


    try:
        response = requests.post(
            URL,
            headers=headers,
            json=payload,
            timeout=20,
        )
    except requests.Timeout as error:
        raise WhatsAppAPIError(
            "WhatsApp API request timed out."
        ) from error
    except requests.RequestException as error:
        raise WhatsAppAPIError(
            f"Could not connect to WhatsApp API: {error}"
        ) from error


    return parse_meta_response(response)