from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserAttribution
from app.services.session_service import get_session


router = APIRouter(
    prefix="/api/attribution",
    tags=["Attribution"],
)


class AttributionRequest(BaseModel):
    landing_category: str | None = None
    landing_page: str | None = None
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    utm_content: str | None = None


@router.post("")
async def save_attribution(
    data: AttributionRequest,
    request: Request,
    database: Session = Depends(get_db),
):
    session_id = request.cookies.get("session_id")

    user_id = None

    if session_id:
        session_data = get_session(session_id)

        if session_data:
            user_id = session_data.get("user_id")

    attribution = UserAttribution(
        user_id=int(user_id) if user_id else None,
        session_id=session_id,
        landing_category=data.landing_category,
        landing_page=data.landing_page,
        utm_source=data.utm_source,
        utm_medium=data.utm_medium,
        utm_campaign=data.utm_campaign,
        utm_content=data.utm_content,
    )

    try:
        database.add(attribution)
        database.commit()
        database.refresh(attribution)

    except Exception:
        database.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save attribution.",
        )

    return {
        "status": "success",
        "attribution_id": attribution.id,
    }