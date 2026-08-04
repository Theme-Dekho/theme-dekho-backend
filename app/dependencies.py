from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.session_service import get_session


def get_current_user(
    request: Request,
    database: Session = Depends(get_db),
) -> User:
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated.",
        )

    session_data = get_session(session_id)

    if session_data is None:
        raise HTTPException(
            status_code=401,
            detail="Session expired or invalid.",
        )

    user_id = session_data.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid session data.",
        )

    user = database.get(
        User,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    if user.status != "active":
        raise HTTPException(
            status_code=403,
            detail="User account is inactive.",
        )

    return user

def get_optional_current_user(
    request: Request,
    database: Session = Depends(get_db),
) -> User | None:
    session_id = request.cookies.get("session_id")

    if not session_id:
        return None

    session_data = get_session(session_id)

    if session_data is None:
        return None

    user_id = session_data.get("user_id")

    if user_id is None:
        return None

    user = database.get(User, user_id)

    if user is None or user.status != "active":
        return None

    return user