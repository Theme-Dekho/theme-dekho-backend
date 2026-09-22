import hashlib
import json
import os
import secrets
from datetime import datetime, timezone

from app.redis_client import redis_client


ADMIN_SESSION_EXPIRE_DAYS = int(
    os.getenv("ADMIN_SESSION_EXPIRE_DAYS", "1")
)

ADMIN_SESSION_TTL_SECONDS = (
    ADMIN_SESSION_EXPIRE_DAYS * 24 * 60 * 60
)


def generate_admin_session_id() -> str:
    return secrets.token_urlsafe(48)


def hash_admin_session_id(
    session_id: str,
) -> str:
    return hashlib.sha256(
        session_id.encode("utf-8")
    ).hexdigest()


def create_admin_session(
    admin_id: int,
    username: str,
    role: str,
) -> str:

    raw_session_id = generate_admin_session_id()

    session_hash = hash_admin_session_id(
        raw_session_id
    )

    redis_key = (
        f"admin_session:{session_hash}"
    )

    session_data = {
        "admin_id": int(admin_id),
        "username": username,
        "role": role,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    result = redis_client.setex(
        redis_key,
        ADMIN_SESSION_TTL_SECONDS,
        json.dumps(session_data),
    )

    if not result:
        raise RuntimeError(
            "Redis failed to create the admin session."
        )

    return raw_session_id


def get_admin_session(
    raw_session_id: str,
) -> dict | None:

    session_hash = hash_admin_session_id(
        raw_session_id
    )

    stored = redis_client.get(
        f"admin_session:{session_hash}"
    )

    if stored is None:
        return None

    if isinstance(stored, bytes):
        stored = stored.decode("utf-8")

    try:
        return json.loads(stored)
    except json.JSONDecodeError:
        return None


def delete_admin_session(
    raw_session_id: str,
) -> None:

    session_hash = hash_admin_session_id(
        raw_session_id
    )

    redis_client.delete(
        f"admin_session:{session_hash}"
    )