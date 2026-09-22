from fastapi import APIRouter, Depends, HTTPException
from app.models import AdminUser, Permission, AdminPermission
from app.dependencies import get_current_admin, require_master, require_root_or_master
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from pydantic import BaseModel
from app.security import hash_password


class CreateAdminUserRequest(BaseModel):
    username: str
    password: str
    name: str | None = None
    email: str | None = None
    role: str


class AssignPermissionsRequest(BaseModel):
    admin_id: int
    permission_ids: list[int]    


router = APIRouter(
    prefix="/api/admin/users",
    tags=["Admin Users"],
)


@router.get("/me")
async def admin_user_me(
    admin: AdminUser = Depends(get_current_admin),
):
    return {
        "status": "success",
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "name": admin.name,
            "email": admin.email,
            "role": admin.role,
            "status": admin.status,
        },
    }

@router.get("")
async def list_admin_users(
    admin: AdminUser = Depends(require_root_or_master),
    database: Session = Depends(get_db),
):
    statement = select(AdminUser).order_by(
        AdminUser.id.asc()
    )

    admins = database.scalars(statement).all()

    return {
        "status": "success",
        "count": len(admins),
        "admins": [
            {
                "id": item.id,
                "username": item.username,
                "name": item.name,
                "email": item.email,
                "role": item.role,
                "status": item.status,
                "created_by": item.created_by,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "last_login_at": item.last_login_at,
            }
            for item in admins
        ],
    }

@router.post("")
async def create_admin_user(
    data: CreateAdminUserRequest,
    admin: AdminUser = Depends(require_master),
    database: Session = Depends(get_db),
):
    role = data.role.strip().upper()

    if role not in {"ROOT", "USER"}:
        raise HTTPException(
            status_code=400,
            detail="Only ROOT or USER accounts can be created.",
        )

    username = data.username.strip()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username is required.",
        )

    existing_admin = database.scalar(
        select(AdminUser).where(
            AdminUser.username == username
        )
    )

    if existing_admin is not None:
        raise HTTPException(
            status_code=409,
            detail="Username already exists.",
        )

    email = data.email.strip() if data.email else None

    if email:
        existing_email = database.scalar(
            select(AdminUser).where(
                AdminUser.email == email
            )
        )

        if existing_email is not None:
            raise HTTPException(
                status_code=409,
                detail="Email already exists.",
            )

    new_admin = AdminUser(
        username=username,
        name=data.name.strip() if data.name else None,
        email=email,
        password_hash=hash_password(data.password),
        role=role,
        status="active",
        created_by=admin.id,
    )

    database.add(new_admin)
    database.commit()
    database.refresh(new_admin)

    return {
        "status": "success",
        "message": f"{role} account created successfully.",
        "admin": {
            "id": new_admin.id,
            "username": new_admin.username,
            "name": new_admin.name,
            "email": new_admin.email,
            "role": new_admin.role,
            "status": new_admin.status,
            "created_by": new_admin.created_by,
        },
    }


@router.post("/permissions")
async def assign_permissions(
    data: AssignPermissionsRequest,
    admin: AdminUser = Depends(require_master),
    database: Session = Depends(get_db),
):
    target_admin = database.get(AdminUser, data.admin_id)

    if target_admin is None:
        raise HTTPException(
            status_code=404,
            detail="Admin account not found.",
        )

    if target_admin.role != "USER":
        raise HTTPException(
            status_code=400,
            detail="Permissions can only be assigned to USER accounts.",
        )

    existing_permissions = database.scalars(
        select(AdminPermission).where(
            AdminPermission.admin_id == target_admin.id
        )
    ).all()

    for item in existing_permissions:
        database.delete(item)

    unique_permission_ids = list(set(data.permission_ids))

    for permission_id in unique_permission_ids:
        permission = database.get(Permission, permission_id)

        if permission is None:
            raise HTTPException(
                status_code=404,
                detail=f"Permission {permission_id} not found.",
            )

        database.add(
            AdminPermission(
                admin_id=target_admin.id,
                permission_id=permission.id,
            )
        )

    database.commit()

    return {
        "status": "success",
        "message": "Permissions assigned successfully.",
        "admin": {
            "id": target_admin.id,
            "username": target_admin.username,
            "role": target_admin.role,
        },
        "permission_ids": unique_permission_ids,
    }
