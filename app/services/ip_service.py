import hashlib
import hmac
import ipaddress

from fastapi import Request
# from app.config import settings
from app.config import IP_HASH_SECRET

def get_client_ip(request: Request) -> str | None:
    """
    Return the client IP address.

    Only trust proxy headers when requests reach FastAPI
    through your own trusted reverse proxy or Cloudflare.
    """

    cloudflare_ip = request.headers.get(
        "cf-connecting-ip"
    )

    if cloudflare_ip:
        candidate = cloudflare_ip.strip()
    else:
        forwarded_for = request.headers.get(
            "x-forwarded-for"
        )

        if forwarded_for:
            candidate = forwarded_for.split(",")[0].strip()
        else:
            real_ip = request.headers.get("x-real-ip")

            if real_ip:
                candidate = real_ip.strip()
            elif request.client:
                candidate = request.client.host
            else:
                return None

    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return None


def hash_ip_address(ip_address: str | None) -> str | None:
    """
    Create a stable one-way HMAC hash of an IP address.
    """

    if not ip_address:
        return None

    # secret = settings.ip_hash_secret.encode("utf-8")
    secret = IP_HASH_SECRET.encode("utf-8")
    normalized_ip = ip_address.strip().lower().encode("utf-8")

    return hmac.new(
        secret,
        normalized_ip,
        hashlib.sha256,
    ).hexdigest()


def get_hashed_client_ip(
    request: Request,
) -> str | None:
    client_ip = get_client_ip(request)

    return hash_ip_address(client_ip)