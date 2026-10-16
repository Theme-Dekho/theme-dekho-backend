from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_admin
from app.models import (
    AdminUser,
    Category,
    Subcategory,
    Product,
    ProductDetail,
    ProductDetailFeature,
    ProductDetailPackage,
    ProductDetailAddon,
    ProductDetailSpecification,
    ProductDetailGallery,
    ProductDetailReview,
)

from pydantic import BaseModel, Field


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


class ProductDetailFields(BaseModel):
    tagline: str
    currentPrice: str
    oldPrice: str
    discount: str
    priceRange: str
    rating: str
    reviewCount: int = Field(ge=0)
    purchases: int = Field(ge=0)
    previewUrl: str | None = None
    mainImage: str


class ProductBasicFields(BaseModel):
    name: str
    slug: str
    price: int = Field(ge=0)
    priceDisplay: str
    priceTier: str
    discount: int = Field(ge=0, le=100)
    img: str
    alt: str
    previewUrl: str
    badges: list[dict] = Field(default_factory=list)
    sold: str
    rating: str
    tags: list[str] = Field(default_factory=list)
    status: str = "active"


class ProductFeatureInput(BaseModel):
    icon: str
    title: str
    description: str
    iconBackground: str
    sortOrder: int = Field(ge=0)


class ProductPackageInput(BaseModel):
    title: str
    description: str
    sortOrder: int = Field(ge=0)


class ProductAddonInput(BaseModel):
    addonId: str
    icon: str
    name: str
    description: str
    price: str
    sortOrder: int = Field(ge=0)


class ProductSpecificationInput(BaseModel):
    label: str
    value: str
    badge: str | None = None
    sortOrder: int = Field(ge=0)


class ProductGalleryInput(BaseModel):
    image: str
    sortOrder: int = Field(ge=0)


class ProductReviewInput(BaseModel):
    reviewId: str
    name: str
    initials: str
    location: str
    role: str
    rating: int = Field(ge=1, le=5)
    text: str
    avatarBackground: str
    sortOrder: int = Field(ge=0)


class ProductDetailSaveRequest(BaseModel):
    product: ProductBasicFields
    details: ProductDetailFields
    features: list[ProductFeatureInput] = Field(default_factory=list)
    packageIncludes: list[ProductPackageInput] = Field(default_factory=list)
    addons: list[ProductAddonInput] = Field(default_factory=list)
    specifications: list[ProductSpecificationInput] = Field(default_factory=list)
    gallery: list[ProductGalleryInput] = Field(default_factory=list)
    reviews: list[ProductReviewInput] = Field(default_factory=list)



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



@router.get("/public/products/{slug}/details")
def get_public_product_details(
    slug: str,
    database: Session = Depends(get_db),
):
    product = database.scalar(
        select(Product).where(
            Product.slug == slug,
            Product.status == "active",
        )
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    detail = database.scalar(
        select(ProductDetail).where(
            ProductDetail.product_id == product.id
        )
    )

    if not detail:
        raise HTTPException(
            status_code=404,
            detail="Product details not found",
        )

    features = database.scalars(
        select(ProductDetailFeature)
        .where(
            ProductDetailFeature.product_detail_id == detail.id
        )
        .order_by(ProductDetailFeature.sort_order)
    ).all()

    packages = database.scalars(
        select(ProductDetailPackage)
        .where(
            ProductDetailPackage.product_detail_id == detail.id
        )
        .order_by(ProductDetailPackage.sort_order)
    ).all()

    addons = database.scalars(
        select(ProductDetailAddon)
        .where(
            ProductDetailAddon.product_detail_id == detail.id
        )
        .order_by(ProductDetailAddon.sort_order)
    ).all()

    specifications = database.scalars(
        select(ProductDetailSpecification)
        .where(
            ProductDetailSpecification.product_detail_id == detail.id
        )
        .order_by(ProductDetailSpecification.sort_order)
    ).all()

    gallery = database.scalars(
        select(ProductDetailGallery)
        .where(
            ProductDetailGallery.product_detail_id == detail.id
        )
        .order_by(ProductDetailGallery.sort_order)
    ).all()

    reviews = database.scalars(
        select(ProductDetailReview)
        .where(
            ProductDetailReview.product_detail_id == detail.id
        )
        .order_by(ProductDetailReview.sort_order)
    ).all()

    return {
        "product": {
            "id": product.id,
            "slug": product.slug,
            "name": product.name,
            "category": product.subcategory_id,
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
        },
        # "details": {
        #     "tagline": detail.tagline,
        #     "currentPrice": detail.current_price,
        #     "oldPrice": detail.old_price,
        #     "discount": detail.discount,
        #     "priceRange": detail.price_range,
        #     "rating": detail.rating,
        #     "reviewCount": detail.review_count,
        #     "purchases": detail.purchases,
        #     "previewUrl": detail.preview_url,
        #     "mainImage": detail.main_image,
        # },
        "details": {
        "tagline": detail.tagline,
        "currentPrice": detail.current_price,
        "oldPrice": detail.old_price,
        "discount": detail.discount,
        "priceRange": detail.price_range,
        "rating": detail.rating,
        "reviewCount": detail.review_count,
        "purchases": detail.purchases,
        "previewUrl": detail.preview_url,
        "mainImage": detail.main_image,
        # "ratingBreakdown": [
        #     {
        #         "stars": 5,
        #         "count": round(detail.review_count * 0.82),
        #         "percentage": 82,
        #     },
        #     {
        #         "stars": 4,
        #         "count": round(detail.review_count * 0.12),
        #         "percentage": 12,
        #     },
        #     {
        #         "stars": 3,
        #         "count": round(detail.review_count * 0.04),
        #         "percentage": 4,
        #     },
        #     {
        #         "stars": 2,
        #         "count": round(detail.review_count * 0.01),
        #         "percentage": 1,
        #     },
        #     {
        #         "stars": 1,
        #         "count": round(detail.review_count * 0.01),
        #         "percentage": 1,
        #     },
        # ],
        "ratingBreakdown": [
            {
                "stars": 5,
                "count": round(detail.review_count * 0.82),
                "percentage": 82,
            },
            {
                "stars": 4,
                "count": round(detail.review_count * 0.12),
                "percentage": 12,
            },
            {
                "stars": 3,
                "count": round(detail.review_count * 0.04),
                "percentage": 4,
            },
            {
                "stars": 2,
                "count": max(
                    0,
                    detail.review_count
                    - round(detail.review_count * 0.82)
                    - round(detail.review_count * 0.12)
                    - round(detail.review_count * 0.04),
                ),
                "percentage": 2,
            },
            {
                "stars": 1,
                "count": 0,
                "percentage": 0,
            },
        ],
    },
        "features": [
            {
                "id": feature.id,
                "icon": feature.icon,
                "title": feature.title,
                "description": feature.description,
                "iconBackground": feature.icon_background,
                "sortOrder": feature.sort_order,
            }
            for feature in features
        ],
        "packageIncludes": [
            {
                "id": package.id,
                "title": package.title,
                "description": package.description,
                "sortOrder": package.sort_order,
            }
            for package in packages
        ],
        "addons": [
            {
                "id": addon.id,
                "addonId": addon.addon_id,
                "icon": addon.icon,
                "name": addon.name,
                "description": addon.description,
                "price": addon.price,
                "sortOrder": addon.sort_order,
            }
            for addon in addons
        ],
        "specifications": [
            {
                "id": specification.id,
                "label": specification.label,
                "value": specification.value,
                "badge": specification.badge,
                "sortOrder": specification.sort_order,
            }
            for specification in specifications
        ],
        "gallery": [
            {
                "id": image.id,
                "image": image.image,
                "sortOrder": image.sort_order,
            }
            for image in gallery
        ],
        "reviews": [
            {
                "id": review.id,
                "reviewId": review.review_id,
                "name": review.name,
                "initials": review.initials,
                "location": review.location,
                "role": review.role,
                "rating": review.rating,
                "text": review.text,
                "avatarBackground": review.avatar_background,
                "sortOrder": review.sort_order,
            }
            for review in reviews
        ],
    }



@router.put("/products/{product_id}/details")
def save_product_details(
    product_id: int,
    payload: ProductDetailSaveRequest,
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

    if payload.product.status not in {"active", "inactive"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid product status",
        )

    if any(
        specification.badge not in {None, "included", "addon"}
        for specification in payload.specifications
    ):
        raise HTTPException(
            status_code=400,
            detail="Specification badge must be included, addon, or null",
        )

    duplicate_slug = database.scalar(
        select(Product).where(
            Product.slug == payload.product.slug,
            Product.id != product_id,
        )
    )

    if duplicate_slug:
        raise HTTPException(
            status_code=409,
            detail="This product slug is already in use",
        )

    detail = database.scalar(
        select(ProductDetail).where(
            ProductDetail.product_id == product_id
        )
    )

    try:
        # Update the existing product listing fields.
        product.name = payload.product.name
        product.slug = payload.product.slug
        product.price = payload.product.price
        product.price_display = payload.product.priceDisplay
        product.price_tier = payload.product.priceTier
        product.discount = payload.product.discount
        product.image = payload.product.img
        product.alt = payload.product.alt
        product.preview_url = payload.product.previewUrl
        product.badges = payload.product.badges
        product.sold = payload.product.sold
        product.rating = payload.product.rating
        product.tags = payload.product.tags
        product.status = payload.product.status

        # Create the detail record if this product has none.
        if detail is None:
            detail = ProductDetail(
                product_id=product_id,
                current_price=payload.details.currentPrice,
                old_price=payload.details.oldPrice,
                discount=payload.details.discount,
                price_range=payload.details.priceRange,
                main_image=payload.details.mainImage,
            )
            database.add(detail)
            database.flush()

        # Update the  product detail fields.
        detail.tagline = payload.details.tagline
        detail.current_price = payload.details.currentPrice
        detail.old_price = payload.details.oldPrice
        detail.discount = payload.details.discount
        detail.price_range = payload.details.priceRange
        detail.rating = payload.details.rating
        detail.review_count = payload.details.reviewCount
        detail.purchases = payload.details.purchases
        detail.preview_url = (
            payload.details.previewUrl or payload.product.previewUrl
        )
        detail.main_image = payload.details.mainImage

        database.flush()

        # Replace child records with the submitted lists.
        child_models = [
            ProductDetailFeature,
            ProductDetailPackage,
            ProductDetailAddon,
            ProductDetailSpecification,
            ProductDetailGallery,
            ProductDetailReview,
        ]

        for model in child_models:
            database.execute(
                delete(model).where(
                    model.product_detail_id == detail.id
                )
            )

        database.add_all([
            ProductDetailFeature(
                product_detail_id=detail.id,
                icon=item.icon,
                title=item.title,
                description=item.description,
                icon_background=item.iconBackground,
                sort_order=item.sortOrder,
            )
            for item in payload.features
        ])

        database.add_all([
            ProductDetailPackage(
                product_detail_id=detail.id,
                title=item.title,
                description=item.description,
                sort_order=item.sortOrder,
            )
            for item in payload.packageIncludes
        ])

        database.add_all([
            ProductDetailAddon(
                product_detail_id=detail.id,
                addon_id=item.addonId,
                icon=item.icon,
                name=item.name,
                description=item.description,
                price=item.price,
                sort_order=item.sortOrder,
            )
            for item in payload.addons
        ])

        database.add_all([
            ProductDetailSpecification(
                product_detail_id=detail.id,
                label=item.label,
                value=item.value,
                badge=item.badge,
                sort_order=item.sortOrder,
            )
            for item in payload.specifications
        ])

        database.add_all([
            ProductDetailGallery(
                product_detail_id=detail.id,
                image=item.image,
                sort_order=item.sortOrder,
            )
            for item in payload.gallery
        ])

        database.add_all([
            ProductDetailReview(
                product_detail_id=detail.id,
                review_id=item.reviewId,
                name=item.name,
                initials=item.initials,
                location=item.location,
                role=item.role,
                rating=item.rating,
                text=item.text,
                avatar_background=item.avatarBackground,
                sort_order=item.sortOrder,
            )
            for item in payload.reviews
        ])

        database.commit()
        database.refresh(product)
        database.refresh(detail)

        return {
            "message": "Product details saved successfully",
            "productId": product.id,
            "slug": product.slug,
            "detailId": detail.id,
        }

    except Exception:
        database.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save product details. No changes were committed.",
        )


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