from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import (get_current_user, get_optional_current_user)
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


@router.delete(
    "/{enquiry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_enquiry(
    enquiry_id: int,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    statement = select(Enquiry).where(
        Enquiry.id == enquiry_id,
        Enquiry.user_id == current_user.id,
    )

    enquiry = database.scalar(statement)

    if enquiry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enquiry not found.",
        )

    database.delete(enquiry)
    database.commit()

    return None


@router.post(
    "",
    response_model=EnquiryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_enquiry(
    data: EnquiryCreate,
    current_user: User | None = Depends(get_optional_current_user),
    database: Session = Depends(get_db),
):
    enquiry = Enquiry(
        user_id=(
            current_user.id
            if current_user is not None
            else None
        ),
        product_id=data.product_id,
        product_slug=data.product_slug,
        product_name=data.product_name,
        customer_name=data.customer_name,
        email=data.email,
        phone=data.phone,
        city=data.city,
        selected_addons=data.selected_addons,
        message=data.message,
        status="submitted",
    )

    database.add(enquiry)

    # wishlist_statement = select(
    #     UserWishlist
    # ).where(
    #     UserWishlist.user_id == current_user.id,
    #     UserWishlist.product_id == data.product_id,
    # )

    # wishlist_item = database.scalar(
    #     wishlist_statement
    # )

    # if wishlist_item is not None:
    #     database.delete(wishlist_item)
    if current_user is not None:
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