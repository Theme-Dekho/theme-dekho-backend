from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_optional_current_user
from app.models import QuoteRequest, User
from app.schemas import (
    QuoteRequestCreate,
    QuoteRequestResponse,
)


router = APIRouter(
    prefix="/api/quote-requests",
    tags=["Quote Requests"],
)


@router.post(
    "",
    response_model=QuoteRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_quote_request(
    data: QuoteRequestCreate,
    current_user: User | None = Depends(
        get_optional_current_user,
    ),
    database: Session = Depends(get_db),
):
    quote_request = QuoteRequest(
        user_id=(
            current_user.id
            if current_user is not None
            else None
        ),
        business_name=data.business_name,
        whatsapp_number=data.whatsapp_number,
        website_type=data.website_type,
        status="submitted",
    )

    database.add(quote_request)
    database.commit()
    database.refresh(quote_request)

    return quote_request