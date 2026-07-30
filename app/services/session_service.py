import hashlib
import json
import os
import secrets
from datetime import datetime, timezone

from app.redis_client import redis_client


SESSION_EXPIRE_DAYS = int(
    os.getenv("SESSION_EXPIRE_DAYS", "30")
)

SESSION_TTL_SECONDS = (
    SESSION_EXPIRE_DAYS * 24 * 60 * 60
)


def generate_session_id() -> str:
    return secrets.token_urlsafe(48)


def hash_session_id(session_id: str) -> str:
    return hashlib.sha256(
        session_id.encode("utf-8")
    ).hexdigest()


# def create_session(
#     user_id: int,
#     phone: str,
# ) -> str:
#     raw_session_id = generate_session_id()
#     session_hash = hash_session_id(raw_session_id)

#     session_data = {
#         "user_id": user_id,
#         "phone": phone,
#         "created_at": datetime.now(
#             timezone.utc
#         ).isoformat(),
#     }

#     redis_client.setex(
#         f"session:{session_hash}",
#         SESSION_TTL_SECONDS,
#         json.dumps(session_data),
#     )

#     return raw_session_id

def create_session(
    user_id: int,
    phone: str,
) -> str:
    raw_session_id = generate_session_id()
    session_hash = hash_session_id(raw_session_id)

    redis_key = f"session:{session_hash}"

    session_data = {
        "user_id": int(user_id),
        "phone": phone,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    result = redis_client.setex(
        redis_key,
        SESSION_TTL_SECONDS,
        json.dumps(session_data),
    )

    stored_value = redis_client.get(redis_key)
    ttl = redis_client.ttl(redis_key)

    print("Redis session key:", redis_key)
    print("Redis setex result:", result)
    print("Redis stored value:", stored_value)
    print("Redis session TTL:", ttl)

    if not result:
        raise RuntimeError(
            "Redis failed to create the session."
        )

    return raw_session_id


def get_session(
    raw_session_id: str,
) -> dict | None:
    session_hash = hash_session_id(raw_session_id)

    stored = redis_client.get(
        f"session:{session_hash}"
    )

    if stored is None:
        return None

    if isinstance(stored, bytes):
        stored = stored.decode("utf-8")

    try:
        return json.loads(stored)
    except json.JSONDecodeError:
        return None


def delete_session(
    raw_session_id: str,
) -> None:
    session_hash = hash_session_id(raw_session_id)

    redis_client.delete(
        f"session:{session_hash}"
    )