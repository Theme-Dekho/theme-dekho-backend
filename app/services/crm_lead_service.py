
import os
import requests
from typing import Any


CRM_WEBSITE_LEAD_URL = os.getenv(
    "CRM_WEBSITE_LEAD_URL",
    "",
).strip()

CRM_WEBSITE_API_KEY = os.getenv(
    "CRM_WEBSITE_API_KEY",
    "",
).strip()


class CRMLeadError(RuntimeError):
    """Raised when the CRM rejects or cannot receive a lead."""


def send_lead_to_crm(
    name: str,
    phone: str,
    email: str,
    source: str,
    notes: str,
) -> dict[str, Any]:
    """Forward a Theme Dekho lead to CRM Smart Solutions."""

    if not CRM_WEBSITE_LEAD_URL:
        raise CRMLeadError("CRM_WEBSITE_LEAD_URL is missing.")

    if not CRM_WEBSITE_API_KEY:
        raise CRMLeadError("CRM_WEBSITE_API_KEY is missing.")

    payload = {
        "name": name.strip(),
        "phone": phone.strip(),
        "email": email.strip(),
        "source": source.strip(),
        "notes": notes.strip(),
    }

    headers = {
        "x-api-key": CRM_WEBSITE_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            CRM_WEBSITE_LEAD_URL,
            json=payload,
            headers=headers,
            timeout=20,
        )
    except requests.RequestException as error:
        raise CRMLeadError(
            f"Could not connect to CRM: {error}"
        ) from error

    if not response.ok:
        raise CRMLeadError(
            f"CRM rejected the lead. HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    try:
        return response.json()
    except ValueError:
        return {
            "success": True,
            "status_code": response.status_code,
        }
