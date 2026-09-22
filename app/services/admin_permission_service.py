from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AdminUser, Permission, AdminPermission


def has_permission(
    admin: AdminUser,
    permission_key: str,
    database: Session,
) -> bool:
    if admin.role == "MASTER":
        return True

    statement = (
        select(AdminPermission)
        .join(
            Permission,
            AdminPermission.permission_id == Permission.id,
        )
        .where(
            AdminPermission.admin_id == admin.id,
            Permission.permission_key == permission_key,
        )
    )

    return database.scalar(statement) is not None


def require_permission(
    admin: AdminUser,
    permission_key: str,
    database: Session,
) -> None:
    if not has_permission(
        admin,
        permission_key,
        database,
    ):
        raise HTTPException(
            status_code=403,
            detail=f"Permission required: {permission_key}",
        )