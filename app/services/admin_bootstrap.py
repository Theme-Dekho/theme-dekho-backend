import os
from sqlalchemy import select
from app.database import SessionLocal
from app.models import AdminUser, Permission
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