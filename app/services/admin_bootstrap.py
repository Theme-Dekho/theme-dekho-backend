import os
from sqlalchemy import select
from app.database import SessionLocal
from app.models import AdminUser, Permission, Category, Subcategory, Product
from app.security import hash_password


def ensure_permissions() -> None:
    permissions = [
        {
            "permission_key": "products.view",
            "permission_name": "View Products",
            "module": "products",
            "description": "Allows viewing products.",
        },
        {
            "permission_key": "products.create",
            "permission_name": "Create Products",
            "module": "products",
            "description": "Allows creating products.",
        },
        {
            "permission_key": "products.edit",
            "permission_name": "Edit Products",
            "module": "products",
            "description": "Allows editing products.",
        },
        {
            "permission_key": "products.delete",
            "permission_name": "Delete Products",
            "module": "products",
            "description": "Allows deleting products.",
        },
        {
            "permission_key": "categories.view",
            "permission_name": "View Categories",
            "module": "categories",
            "description": "Allows viewing categories.",
        },
        {
            "permission_key": "categories.create",
            "permission_name": "Create Categories",
            "module": "categories",
            "description": "Allows creating categories.",
        },
        {
            "permission_key": "categories.edit",
            "permission_name": "Edit Categories",
            "module": "categories",
            "description": "Allows editing categories.",
        },
        {
            "permission_key": "categories.delete",
            "permission_name": "Delete Categories",
            "module": "categories",
            "description": "Allows deleting categories.",
        },
        {
            "permission_key": "enquiries.view",
            "permission_name": "View Enquiries",
            "module": "enquiries",
            "description": "Allows viewing enquiries.",
        },
        {
            "permission_key": "enquiries.create",
            "permission_name": "Create Enquiries",
            "module": "enquiries",
            "description": "Allows creating enquiries.",
        },
        {
            "permission_key": "enquiries.edit",
            "permission_name": "Edit Enquiries",
            "module": "enquiries",
            "description": "Allows editing enquiries.",
        },
        {
            "permission_key": "enquiries.delete",
            "permission_name": "Delete Enquiries",
            "module": "enquiries",
            "description": "Allows deleting enquiries.",
        },
        {
            "permission_key": "analytics.view",
            "permission_name": "View Analytics",
            "module": "analytics",
            "description": "Allows viewing analytics.",
        },
    ]

    database = SessionLocal()

    try:
        for item in permissions:
            existing_permission = database.scalar(
                select(Permission).where(
                    Permission.permission_key == item["permission_key"]
                )
            )

            if existing_permission is not None:
                continue

            database.add(Permission(**item))

        database.commit()

    finally:
        database.close()


def ensure_catalog_categories():
    categories = [
        {
            "slug": "interior-architecture",
            "name": "Interior & Architecture",
            "description": (
                "Website designs for interior designers, architects, "
                "studios, and contractors."
            ),
            "subcategories": [
                {
                    "slug": "interior-firm",
                    "name": "Interior Firm",
                },
                {
                    "slug": "architect-firm",
                    "name": "Architect Firm",
                },
                {
                    "slug": "interior-architect",
                    "name": "Interior & Architect Firm",
                },
                {
                    "slug": "interior-portfolio",
                    "name": "Interior Designer Portfolio",
                },
                {
                    "slug": "architect-portfolio",
                    "name": "Architect Portfolio",
                },
            ],
        },
        {
            "slug": "healthcare",
            "name": "Healthcare & Clinic",
            "description": (
                "Website designs for hospitals, clinics, doctors, "
                "and healthcare businesses."
            ),
            "subcategories": [
                {
                    "slug": "hospital",
                    "name": "Hospital",
                },
                {
                    "slug": "dental-clinic",
                    "name": "Dental Clinic",
                },
                {
                    "slug": "ivf-center",
                    "name": "IVF Center",
                },
                {
                    "slug": "physiotherapy",
                    "name": "Physiotherapy",
                },
                {
                    "slug": "dermatology",
                    "name": "Dermatology",
                },
                {
                    "slug": "diagnostic-center",
                    "name": "Diagnostic Center",
                },
            ],
        },
    ]

    database = SessionLocal()

    try:
        for category_data in categories:
            category = database.scalar(
                select(Category).where(
                    Category.slug == category_data["slug"]
                )
            )

            if not category:
                category = Category(
                    slug=category_data["slug"],
                    name=category_data["name"],
                    description=category_data["description"],
                    status="active",
                )
                database.add(category)
                database.flush()

            for subcategory_data in category_data["subcategories"]:
                subcategory = database.scalar(
                    select(Subcategory).where(
                        Subcategory.category_id == category.id,
                        Subcategory.slug == subcategory_data["slug"],
                    )
                )

                if not subcategory:
                    database.add(
                        Subcategory(
                            category_id=category.id,
                            slug=subcategory_data["slug"],
                            name=subcategory_data["name"],
                            status="active",
                        )
                    )

        database.commit()

    finally:
        database.close()


def ensure_catalog_products():
    products = [
        {
            "id": 1,
            "slug": "decorpot",
            "name": "Decorpot",
            "category": "interior-firm",
            "price": 14999,
            "price_display": "₹14,999",
            "price_tier": "Up to 30 Pages",
            "discount": 68,
            "image": "/images/templates/interior/interior1.webp",
            "alt": "Decorpot Interior Design Website",
            "preview_url": "https://www.decorpot.com",
            "badges": [{"type": "badge-hot", "label": "Popular"}],
            "sold": "98",
            "rating": "4.8",
            "tags": ["AI Chat Bot", "CRM", "Price Calculator", "BOQ"],
        },
        {
            "id": 2,
            "slug": "gopesh-interior",
            "name": "Gopesh Interior Furniture House",
            "category": "interior-firm",
            "price": 9999,
            "price_display": "₹9,999",
            "price_tier": "Up to 15 Pages",
            "discount": 55,
            "image": "/images/templates/interior/interior2.webp",
            "alt": "Gopesh Interior Furniture House Website",
            "preview_url": "https://gifhouse.in",
            "badges": [{"type": "badge-hot", "label": "Popular"}],
            "sold": "33",
            "rating": "4.5",
            "tags": ["AI Chat Bot", "CRM", "Price Calculator", "BOQ"],
        },
        {
            "id": 3,
            "slug": "modern-architect-studio",
            "name": "Modern Architect Studio",
            "category": "architect-firm",
            "price": 19999,
            "price_display": "₹19,999",
            "price_tier": "Up to 40 Pages",
            "discount": 61,
            "image": "/images/templates/interior/architect.webp",
            "alt": "Modern Architecture Studio Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [{"type": "badge-premium", "label": "Premium"}],
            "sold": "67",
            "rating": "4.9",
            "tags": ["Project Gallery", "CRM", "Lead Form", "SEO"],
        },
        {
            "id": 4,
            "slug": "interior-portfolio-pro",
            "name": "Interior Portfolio Pro",
            "category": "interior-portfolio",
            "price": 12999,
            "price_display": "₹12,999",
            "price_tier": "Up to 20 Pages",
            "discount": 58,
            "image": "/images/templates/interior/inter-portfolio.webp",
            "alt": "Interior Designer Portfolio Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [{"type": "badge-new", "label": "New"}],
            "sold": "41",
            "rating": "4.7",
            "tags": ["Portfolio", "Gallery", "WhatsApp", "Inquiry Form"],
        },
        {
            "id": 5,
            "slug": "architect-portfolio",
            "name": "Architect Portfolio",
            "category": "architect-portfolio",
            "price": 15999,
            "price_display": "₹15,999",
            "price_tier": "Up to 25 Pages",
            "discount": 60,
            "image": "/images/theme.webp",
            "alt": "Professional Architect Portfolio Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [{"type": "badge-hot", "label": "Popular"}],
            "sold": "76",
            "rating": "4.8",
            "tags": ["Project Showcase", "Gallery", "CRM", "Contact Form"],
        },
        {
            "id": 6,
            "slug": "interior-architect-firm",
            "name": "Interior & Architect Firm",
            "category": "interior-architect",
            "price": 17999,
            "price_display": "₹17,999",
            "price_tier": "Up to 35 Pages",
            "discount": 63,
            "image": "/images/theme.webp",
            "alt": "Interior and Architecture Firm Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [{"type": "badge-premium", "label": "Premium"}],
            "sold": "52",
            "rating": "4.9",
            "tags": ["Price Calculator", "CRM", "BOQ", "AI Chat Bot"],
        },
        {
            "id": 7,
            "slug": "urban-space-interiors",
            "name": "Urban Space Interiors",
            "category": "interior-firm",
            "price": 8999,
            "price_display": "₹8,999",
            "price_tier": "Up to 15 Pages",
            "discount": 50,
            "image": "/images/templates/interior/interior3.webp",
            "alt": "Urban Space Interiors Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "42",
            "rating": "4.6",
            "tags": ["AI Chat Bot", "CRM", "Price Calculator", "BOQ"],
        },
        {
            "id": 8,
            "slug": "elite-home-interiors",
            "name": "Elite Home Interiors",
            "category": "interior-firm",
            "price": 10999,
            "price_display": "₹10,999",
            "price_tier": "Up to 20 Pages",
            "discount": 56,
            "image": "/images/templates/interior/interior4.webp",
            "alt": "Elite Home Interiors Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "58",
            "rating": "4.7",
            "tags": ["AI Chat Bot", "CRM", "Price Calculator", "BOQ"],
        },
        {
            "id": 9,
            "slug": "signature-interior-studio",
            "name": "Signature Interior Studio",
            "category": "interior-firm",
            "price": 12999,
            "price_display": "₹12,999",
            "price_tier": "Up to 20 Pages",
            "discount": 58,
            "image": "/images/templates/interior/interior5.webp",
            "alt": "Signature Interior Studio Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "71",
            "rating": "4.8",
            "tags": ["AI Chat Bot", "CRM", "Price Calculator", "BOQ"],
        },
        {
            "id": 10,
            "slug": "dreamline-interiors",
            "name": "Dreamline Interiors",
            "category": "interior-firm",
            "price": 7999,
            "price_display": "₹7,999",
            "price_tier": "Up to 12 Pages",
            "discount": 45,
            "image": "/images/templates/interior/interior6.webp",
            "alt": "Dreamline Interiors Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "36",
            "rating": "4.5",
            "tags": ["AI Chat Bot", "CRM", "Price Calculator", "BOQ"],
        },
        {
            "id": 11,
            "slug": "living-space-designs",
            "name": "Living Space Designs",
            "category": "interior-firm",
            "price": 14999,
            "price_display": "₹14,999",
            "price_tier": "Up to 25 Pages",
            "discount": 60,
            "image": "/images/templates/interior/interior7.webp",
            "alt": "Living Space Designs Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "83",
            "rating": "4.8",
            "tags": ["AI Chat Bot", "CRM", "Price Calculator", "BOQ"],
        },
        {
            "id": 12,
            "slug": "prime-interior-solutions",
            "name": "Prime Interior Solutions",
            "category": "interior-firm",
            "price": 11999,
            "price_display": "₹11,999",
            "price_tier": "Up to 20 Pages",
            "discount": 52,
            "image": "/images/templates/interior/interior8.webp",
            "alt": "Prime Interior Solutions Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "64",
            "rating": "4.7",
            "tags": ["AI Chat Bot", "CRM", "Price Calculator", "BOQ"],
        },
        {
            "id": 13,
            "slug": "axis-architects",
            "name": "Axis Architects",
            "category": "architect-firm",
            "price": 13999,
            "price_display": "₹13,999",
            "price_tier": "Up to 25 Pages",
            "discount": 55,
            "image": "/images/theme.webp",
            "alt": "Axis Architects Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "49",
            "rating": "4.7",
            "tags": ["Project Gallery", "CRM", "Lead Form", "SEO"],
        },
        {
            "id": 14,
            "slug": "urban-arc-studio",
            "name": "Urban Arc Studio",
            "category": "architect-firm",
            "price": 16999,
            "price_display": "₹16,999",
            "price_tier": "Up to 30 Pages",
            "discount": 59,
            "image": "/images/theme.webp",
            "alt": "Urban Arc Studio Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "62",
            "rating": "4.8",
            "tags": ["Project Gallery", "CRM", "Lead Form", "SEO"],
        },
        {
            "id": 15,
            "slug": "form-space-architects",
            "name": "Form & Space Architects",
            "category": "architect-firm",
            "price": 18999,
            "price_display": "₹18,999",
            "price_tier": "Up to 35 Pages",
            "discount": 62,
            "image": "/images/theme.webp",
            "alt": "Form and Space Architects Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "74",
            "rating": "4.9",
            "tags": ["Project Gallery", "CRM", "Lead Form", "SEO"],
        },
        {
            "id": 16,
            "slug": "studio-vertex",
            "name": "Studio Vertex",
            "category": "architect-firm",
            "price": 15999,
            "price_display": "₹15,999",
            "price_tier": "Up to 30 Pages",
            "discount": 57,
            "image": "/images/theme.webp",
            "alt": "Studio Vertex Architecture Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "55",
            "rating": "4.7",
            "tags": ["Project Gallery", "CRM", "Lead Form", "SEO"],
        },
        {
            "id": 17,
            "slug": "arc-and-interiors",
            "name": "Arc & Interiors Studio",
            "category": "interior-architect",
            "price": 14999,
            "price_display": "₹14,999",
            "price_tier": "Up to 25 Pages",
            "discount": 56,
            "image": "/images/theme.webp",
            "alt": "Arc and Interiors Studio Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "47",
            "rating": "4.7",
            "tags": ["Price Calculator", "CRM", "BOQ", "AI Chat Bot"],
        },
        {
            "id": 18,
            "slug": "buildspace-designs",
            "name": "BuildSpace Designs",
            "category": "interior-architect",
            "price": 16999,
            "price_display": "₹16,999",
            "price_tier": "Up to 30 Pages",
            "discount": 60,
            "image": "/images/theme.webp",
            "alt": "BuildSpace Designs Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "59",
            "rating": "4.8",
            "tags": ["Price Calculator", "CRM", "BOQ", "AI Chat Bot"],
        },
        {
            "id": 19,
            "slug": "studio-integrate",
            "name": "Studio Integrate",
            "category": "interior-architect",
            "price": 18999,
            "price_display": "₹18,999",
            "price_tier": "Up to 35 Pages",
            "discount": 63,
            "image": "/images/theme.webp",
            "alt": "Studio Integrate Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "68",
            "rating": "4.9",
            "tags": ["Price Calculator", "CRM", "BOQ", "AI Chat Bot"],
        },
        {
            "id": 20,
            "slug": "minimal-interior-portfolio",
            "name": "Minimal Interior Portfolio",
            "category": "interior-portfolio",
            "price": 8999,
            "price_display": "₹8,999",
            "price_tier": "Up to 15 Pages",
            "discount": 48,
            "image": "/images/theme.webp",
            "alt": "Minimal Interior Portfolio Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "32",
            "rating": "4.6",
            "tags": ["Portfolio", "Gallery", "WhatsApp", "Inquiry Form"],
        },
        {
            "id": 21,
            "slug": "creative-interior-showcase",
            "name": "Creative Interior Showcase",
            "category": "interior-portfolio",
            "price": 10999,
            "price_display": "₹10,999",
            "price_tier": "Up to 20 Pages",
            "discount": 54,
            "image": "/images/theme.webp",
            "alt": "Creative Interior Showcase Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "46",
            "rating": "4.7",
            "tags": ["Portfolio", "Gallery", "WhatsApp", "Inquiry Form"],
        },
        {
            "id": 22,
            "slug": "designer-portfolio-studio",
            "name": "Designer Portfolio Studio",
            "category": "interior-portfolio",
            "price": 11999,
            "price_display": "₹11,999",
            "price_tier": "Up to 20 Pages",
            "discount": 57,
            "image": "/images/theme.webp",
            "alt": "Designer Portfolio Studio Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "53",
            "rating": "4.8",
            "tags": ["Portfolio", "Gallery", "WhatsApp", "Inquiry Form"],
        },
        {
            "id": 23,
            "slug": "modern-architect-portfolio",
            "name": "Modern Architect Portfolio",
            "category": "architect-portfolio",
            "price": 12999,
            "price_display": "₹12,999",
            "price_tier": "Up to 20 Pages",
            "discount": 55,
            "image": "/images/theme.webp",
            "alt": "Modern Architect Portfolio Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "39",
            "rating": "4.7",
            "tags": ["Project Showcase", "Gallery", "CRM", "Contact Form"],
        },
        {
            "id": 24,
            "slug": "premium-architect-showcase",
            "name": "Premium Architect Showcase",
            "category": "architect-portfolio",
            "price": 16999,
            "price_display": "₹16,999",
            "price_tier": "Up to 30 Pages",
            "discount": 60,
            "image": "/images/theme.webp",
            "alt": "Premium Architect Showcase Website",
            "preview_url": "https://theme-dekho.github.io/development_page/",
            "badges": [],
            "sold": "57",
            "rating": "4.8",
            "tags": ["Project Showcase", "Gallery", "CRM", "Contact Form"],
        },
    ]

    database = SessionLocal()

    try:
        for product_data in products:
            existing_product = database.scalar(
                select(Product).where(
                    Product.slug == product_data["slug"]
                )
            )

            if existing_product:
                continue

            subcategory = database.scalar(
                select(Subcategory).where(
                    Subcategory.slug == product_data["category"]
                )
            )

            if not subcategory:
                raise RuntimeError(
                    f"Subcategory not found: {product_data['category']}"
                )

            database.add(
                Product(
                    id=product_data["id"],
                    subcategory_id=subcategory.id,
                    slug=product_data["slug"],
                    name=product_data["name"],
                    price=product_data["price"],
                    price_display=product_data["price_display"],
                    price_tier=product_data["price_tier"],
                    discount=product_data["discount"],
                    image=product_data["image"],
                    alt=product_data["alt"],
                    preview_url=product_data["preview_url"],
                    badges=product_data["badges"],
                    sold=product_data["sold"],
                    rating=product_data["rating"],
                    tags=product_data["tags"],
                    status="active",
                )
            )

        database.commit()

    finally:
        database.close()


def ensure_master_admin() -> None:

    username = os.getenv(
        "MASTER_ADMIN_USERNAME"
    )

    password = os.getenv(
        "MASTER_ADMIN_PASSWORD"
    )

    if not username or not password:
        raise RuntimeError(
            "MASTER_ADMIN_USERNAME and "
            "MASTER_ADMIN_PASSWORD must be "
            "configured in the environment."
        )

    database = SessionLocal()

    try:
        statement = select(AdminUser).where(
            AdminUser.role == "MASTER"
        )

        master = database.scalar(statement)

        if master is not None:
            return

        master = AdminUser(
            username=username.strip(),
            name="Master Administrator",
            password_hash=hash_password(
                password
            ),
            role="MASTER",
            status="active",
            created_by=None,
        )

        database.add(master)
        database.commit()

    finally:
        database.close()