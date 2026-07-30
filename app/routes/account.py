from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.session_service import get_session


router = APIRouter(
    prefix="/api/account",
    tags=["Account"],
)


class UpdateProfileRequest(BaseModel):
    name: str | None = None


@router.patch("/profile")
async def update_profile(
    data: UpdateProfileRequest,
    request: Request,
    database: Session = Depends(get_db),
):
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

    user = database.get(
        User,
        session_data["user_id"],
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    user.name = (
        data.name.strip()
        if data.name
        else None
    )

    database.commit()
    database.refresh(user)

    return {
        "status": "success",
        "user": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name,
        },
    }