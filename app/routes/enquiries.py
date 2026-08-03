from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Enquiry, User, UserWishlist
from app.schemas import (
    EnquiryCreate,
    EnquiryListResponse,
    EnquiryResponse,
)


router = APIRouter(
    prefix="/api/enquiries",
    tags=["Enquiries"],
)


@router.get(
    "",
    response_model=EnquiryListResponse,
)
def get_enquiries(
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    statement = (
        select(Enquiry)
        .where(
            Enquiry.user_id == current_user.id,
        )
        .order_by(
            Enquiry.created_at.desc(),
        )
    )

    items = list(
        database.scalars(statement).all()
    )

    return EnquiryListResponse(
        items=[
            EnquiryResponse.model_validate(item)
            for item in items
        ],
        count=len(items),
    )


@router.post(
    "",
    response_model=EnquiryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_enquiry(
    data: EnquiryCreate,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    enquiry = Enquiry(
        user_id=current_user.id,
        product_id=data.product_id,
        product_slug=data.product_slug,
        product_name=data.product_name,
        customer_name=data.customer_name,
        email=data.email,
        phone=data.phone,
        message=data.message,
        status="submitted",
    )

    database.add(enquiry)

    wishlist_statement = select(
        UserWishlist
    ).where(
        UserWishlist.user_id == current_user.id,
        UserWishlist.product_id == data.product_id,
    )

    wishlist_item = database.scalar(
        wishlist_statement
    )

    if wishlist_item is not None:
        database.delete(wishlist_item)

    database.commit()
    database.refresh(enquiry)

    return enquiry