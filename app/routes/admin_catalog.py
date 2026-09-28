from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_admin
from app.models import AdminUser, Category, Subcategory, Product
from pydantic import BaseModel


router = APIRouter(prefix="/api/admin/catalog", tags=["Admin Catalog"])


class ProductUpdateRequest(BaseModel):
    name: str
    price: int | None = None
    priceDisplay: str | None = None
    discount: int | None = None
    rating: str | None = None
    sold: str | None = None
    status: str
    img: str | None = None
    previewUrl: str | None = None


@router.get("/categories/{category_slug}/subcategories/{subcategory_slug}/products")
def get_subcategory_products(
    category_slug: str,
    subcategory_slug: str,
    database: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    category = database.scalar(
        select(Category).where(Category.slug == category_slug)
    )

    if not category:
        return {
            "category": None,
            "subcategory": None,
            "products": [],
        }

    subcategory = database.scalar(
        select(Subcategory).where(
            Subcategory.category_id == category.id,
            Subcategory.slug == subcategory_slug,
        )
    )

    if not subcategory:
        return {
            "category": {
                "slug": category.slug,
                "name": category.name,
            },
            "subcategory": None,
            "products": [],
        }

    products = database.scalars(
        select(Product)
        .where(Product.subcategory_id == subcategory.id)
        .order_by(Product.id)
    ).all()

    return {
        "category": {
            "slug": category.slug,
            "name": category.name,
        },
        "subcategory": {
            "slug": subcategory.slug,
            "name": subcategory.name,
        },
        "products": [
            {
                "id": product.id,
                "slug": product.slug,
                "name": product.name,
                "price": product.price,
                "priceDisplay": product.price_display,
                "priceTier": product.price_tier,
                "discount": product.discount,
                "img": product.image,
                "alt": product.alt,
                "previewUrl": product.preview_url,
                "badges": product.badges,
                "sold": product.sold,
                "rating": product.rating,
                "tags": product.tags,
                "status": product.status,
            }
            for product in products
        ],
    }


# Modification updates 28/SEP/2026
@router.get("/public/categories/{category_slug}/subcategories/{subcategory_slug}/products")
def get_public_subcategory_products(
    category_slug: str,
    subcategory_slug: str,
    database: Session = Depends(get_db),
):
    category = database.scalar(
        select(Category).where(Category.slug == category_slug)
    )

    if not category:
        return {
            "category": None,
            "subcategory": None,
            "products": [],
        }

    subcategory = database.scalar(
        select(Subcategory).where(
            Subcategory.category_id == category.id,
            Subcategory.slug == subcategory_slug,
        )
    )

    if not subcategory:
        return {
            "category": {
                "slug": category.slug,
                "name": category.name,
            },
            "subcategory": None,
            "products": [],
        }

    products = database.scalars(
        select(Product)
        .where(
            Product.subcategory_id == subcategory.id,
            Product.status == "active",
        )
        .order_by(Product.id)
    ).all()

    return {
        "category": {
            "slug": category.slug,
            "name": category.name,
        },
        "subcategory": {
            "slug": subcategory.slug,
            "name": subcategory.name,
        },
        "products": [
            {
                "id": product.id,
                "slug": product.slug,
                "name": product.name,
                "category": subcategory.slug,
                "subCategoryLabel": subcategory.name,
                "price": product.price,
                "priceDisplay": product.price_display,
                "priceTier": product.price_tier,
                "discount": product.discount,
                "img": product.image,
                "alt": product.alt,
                "previewUrl": product.preview_url,
                "badges": product.badges,
                "sold": product.sold,
                "rating": product.rating,
                "tags": product.tags,
                "status": product.status,
            }
            for product in products
        ],
    }


@router.get("/public/categories/{category_slug}/products")
def get_public_category_products(
    category_slug: str,
    database: Session = Depends(get_db),
):
    category = database.scalar(
        select(Category).where(Category.slug == category_slug)
    )

    if not category:
        return {
            "category": None,
            "products": [],
        }

    rows = database.execute(
        select(Product, Subcategory)
        .join(
            Subcategory,
            Product.subcategory_id == Subcategory.id,
        )
        .where(
            Subcategory.category_id == category.id,
            Product.status == "active",
        )
        .order_by(Product.id)
    ).all()

    return {
        "category": {
            "slug": category.slug,
            "name": category.name,
        },
        "products": [
            {
                "id": product.id,
                "slug": product.slug,
                "name": product.name,
                "category": subcategory.slug,
                "subCategoryLabel": subcategory.name,
                "price": product.price,
                "priceDisplay": product.price_display,
                "priceTier": product.price_tier,
                "discount": product.discount,
                "img": product.image,
                "alt": product.alt,
                "previewUrl": product.preview_url,
                "badges": product.badges,
                "sold": product.sold,
                "rating": product.rating,
                "tags": product.tags,
                "status": product.status,
            }
            for product, subcategory in rows
        ],
    }


@router.put(
    "/products/{product_id}"
)
def update_product(
    product_id: int,
    payload: ProductUpdateRequest,
    database: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    product = database.scalar(
        select(Product).where(Product.id == product_id)
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    if payload.status not in {"active", "inactive"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid product status",
        )

    product.name = payload.name
    product.price = payload.price
    product.price_display = payload.priceDisplay
    product.discount = payload.discount
    product.rating = payload.rating
    product.sold = payload.sold
    product.status = payload.status
    product.image = payload.img
    product.preview_url = payload.previewUrl

    database.commit()
    database.refresh(product)

    return {
        "message": "Product updated successfully",
        "product": {
            "id": product.id,
            "slug": product.slug,
            "name": product.name,
            "price": product.price,
            "priceDisplay": product.price_display,
            "discount": product.discount,
            "rating": product.rating,
            "sold": product.sold,
            "status": product.status,
            "img": product.image,
            "previewUrl": product.preview_url,
        },
    }