from typing import Any

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ActivityEvent
from app.schemas import AnalyticsEventCreate
from app.services.ip_service import get_hashed_client_ip
from app.services.session_service import get_session

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)

ALLOWED_EVENTS = {
    "page_view",
    "button_clicked",
    "category_selected",
    "subcategory_selected",
    "form_started",
    "form_submitted",
    "otp_requested",
    "otp_verified",
    "otp_failed",
    "website_generation_started",
    "website_generation_completed",
    "website_generation_failed",
    "template_previewed",
    "website_downloaded",
    "login",
    "logout",
    "add_to_cart",
    "remove_from_cart",
}


def sanitize_metadata(
    metadata: dict[str, Any],
) -> dict[str, Any]:
    blocked_keys = {
        "password",
        "otp",
        "token",
        "access_token",
        "refresh_token",
        "phone",
        "email",
        "card_number",
        "cvv",
        "message",
    }

    cleaned_metadata: dict[str, Any] = {}

    for key, value in metadata.items():
        normalized_key = key.strip().lower()

        if normalized_key in blocked_keys:
            continue

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        ) or value is None:
            cleaned_metadata[key] = value

        elif isinstance(value, list):
            cleaned_metadata[key] = [
                item
                for item in value
                if isinstance(
                    item,
                    (
                        str,
                        int,
                        float,
                        bool,
                    ),
                )
                or item is None
            ][:20]

    return cleaned_metadata


@router.post(
    "/events",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_event(
    payload: AnalyticsEventCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    if payload.event_name not in ALLOWED_EVENTS:
        return {
            "accepted": False,
            "reason": "event_not_allowed",
        }

    # This should be set by your authentication/session middleware.
    # Do not accept user_id from the frontend.
    # user_id = getattr(
    #     request.state,
    #     "user_id",
    #     None,
    # )
    session_cookie = request.cookies.get(
    "session_id"
    )

    user_id: int | None = None

    if session_cookie:
        session_data = get_session(
            session_cookie
        )

        if session_data:
            stored_user_id = session_data.get(
                "user_id"
            )

            if stored_user_id is not None:
                try:
                    user_id = int(stored_user_id)
                except (TypeError, ValueError):
                    user_id = None

    # event = ActivityEvent(
    #     session_id=payload.session_id,
    #     user_id=user_id,
    #     event_name=payload.event_name,
    #     page_url=payload.page_url,
    #     element_name=payload.element_name,
    #     event_metadata=sanitize_metadata(
    #         payload.metadata,
    #     ),
    # )
    ip_hash = get_hashed_client_ip(request)

    event = ActivityEvent(
        session_id=payload.session_id,
        user_id=user_id,
        ip_hash=ip_hash,
        event_name=payload.event_name,
        page_url=payload.page_url,
        element_name=payload.element_name,
        event_metadata=sanitize_metadata(
            payload.metadata,
        ),
    )

    db.add(event)
    db.commit()

    return {
        "accepted": True,
    }