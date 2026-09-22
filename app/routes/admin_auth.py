import os
from app.models import AdminUser, now_ist
from app.dependencies import (
    get_current_admin,
    require_master,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    AdminLoginRequest,
    AdminAuthResponse,
)
from app.security import verify_password
from app.dependencies import get_current_admin
# from app.dependencies import (
#     get_current_admin,
#     require_master,
# )
from app.services.admin_session_service import (
    create_admin_session,
    delete_admin_session,
)


router = APIRouter(
    prefix="/api/admin/auth",
    tags=["Admin Authentication"],
)


SESSION_EXPIRE_DAYS = int(
    os.getenv(
        "ADMIN_SESSION_EXPIRE_DAYS",
        "1",
    )
)

SESSION_COOKIE_MAX_AGE = (
    SESSION_EXPIRE_DAYS * 24 * 60 * 60
)

COOKIE_SECURE = (
    os.getenv(
        "COOKIE_SECURE",
        "false",
    )
    .strip()
    .lower()
    == "true"
)

COOKIE_SAMESITE = os.getenv(
    "COOKIE_SAMESITE",
    "lax",
).strip().lower()


@router.post("/login")
async def admin_login(
    data: AdminLoginRequest,
    response: Response,
    database: Session = Depends(get_db),
):

    statement = select(AdminUser).where(
        AdminUser.username == data.username.strip()
    )

    admin = database.scalar(statement)

    if admin is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    if admin.status != "active":
        raise HTTPException(
            status_code=403,
            detail="Admin account is inactive.",
        )

    if not verify_password(
        data.password,
        admin.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    admin.last_login_at = now_ist()

    database.commit()
    database.refresh(admin)

    session_id = create_admin_session(
        admin_id=admin.id,
        username=admin.username,
        role=admin.role,
    )

    response.set_cookie(
        key="admin_session_id",
        value=session_id,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )

    return {
        "status": "success",
        "message": "Admin logged in successfully.",
        "authenticated": True,
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "name": admin.name,
            "email": admin.email,
            "role": admin.role,
            "status": admin.status,
        },
    }


@router.get("/me")
async def admin_me(
    admin: AdminUser = Depends(
        get_current_admin
    ),
):

    return {
        "status": "success",
        "authenticated": True,
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "name": admin.name,
            "email": admin.email,
            "role": admin.role,
            "status": admin.status,
        },
    }


@router.post("/logout")
async def admin_logout(
    request: Request,
    response: Response,
):

    session_id = request.cookies.get(
        "admin_session_id"
    )

    if session_id:
        delete_admin_session(
            session_id
        )

    response.delete_cookie(
        key="admin_session_id",
        path="/",
    )

    return {
        "status": "success",
        "message": "Admin logged out successfully.",
    }


# Temporary Data
# @router.get("/test-master")
# async def test_master_access(
#     admin: AdminUser = Depends(require_master),
# ):
#     return {
#         "status": "success",
#         "message": "Master access granted.",
#         "admin": {
#             "id": admin.id,
#             "username": admin.username,
#             "role": admin.role,
#         },
#     }