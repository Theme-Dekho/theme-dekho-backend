from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, UserWishlist
from app.schemas import (
    WishlistItemCreate,
    WishlistItemResponse,
    WishlistResponse,
)


router = APIRouter(
    prefix="/api/wishlist",
    tags=["Wishlist"],
)


@router.get(
    "",
    response_model=WishlistResponse,
)
def get_wishlist(
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    statement = (
        select(UserWishlist)
        .where(
            UserWishlist.user_id == current_user.id,
        )
        .order_by(
            UserWishlist.created_at.desc(),
        )
    )

    items = list(
        database.scalars(statement).all()
    )

    return WishlistResponse(
        items=[
            WishlistItemResponse.model_validate(item)
            for item in items
        ],
        count=len(items),
    )


@router.post(
    "",
    response_model=WishlistItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_to_wishlist(
    data: WishlistItemCreate,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    existing_statement = select(UserWishlist).where(
        UserWishlist.user_id == current_user.id,
        UserWishlist.product_id == data.product_id,
    )

    existing_item = database.scalar(
        existing_statement
    )

    if existing_item is not None:
        return existing_item

    item = UserWishlist(
        user_id=current_user.id,
        product_id=data.product_id,
        product_slug=data.product_slug,
        product_name=data.product_name,
        product_label=data.product_label,
        product_image=data.product_image,
    )

    database.add(item)

    try:
        database.commit()
    except IntegrityError:
        database.rollback()

        existing_item = database.scalar(
            existing_statement
        )

        if existing_item is None:
            raise HTTPException(
                status_code=409,
                detail="Wishlist item already exists.",
            )

        return existing_item

    database.refresh(item)

    return item


@router.delete(
    "/{product_id}",
)
def remove_from_wishlist(
    product_id: str,
    current_user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
):
    statement = select(UserWishlist).where(
        UserWishlist.user_id == current_user.id,
        UserWishlist.product_id == product_id,
    )

    item = database.scalar(statement)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Wishlist item not found.",
        )

    database.delete(item)
    database.commit()

    remaining_count = database.query(
        UserWishlist
    ).filter(
        UserWishlist.user_id == current_user.id,
    ).count()

    return {
        "status": "success",
        "message": "Product removed from wishlist.",
        "count": remaining_count,
    }