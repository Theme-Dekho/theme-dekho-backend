import logging
import os
from datetime import datetime, timezone

import requests
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
from app.models import User
from app.otp import generate_otp
from app.redis_client import redis_client
from app.schemas import GenerateOTPRequest, RegisterVerifyOTPRequest, LoginRequest, ForgotPasswordRequest
from app.security import hash_otp,   hash_password, verify_password
from app.services.session_service import (
    create_session,
    delete_session,
    get_session,
)
from app.services.whatsapp_service import (
    send_otp as send_whatsapp_otp,
)


logger = logging.getLogger(__name__)

MAX_OTP_ATTEMPTS = int(
    os.getenv("MAX_OTP_ATTEMPTS", "5")
)

OTP_LOCK_TIME = int(
    os.getenv("OTP_LOCK_TIME", "900")
)

OTP_EXPIRY = int(
    os.getenv("OTP_EXPIRY", "300")
)

OTP_COOLDOWN = int(
    os.getenv("OTP_COOLDOWN", "30")
)

SESSION_EXPIRE_DAYS = int(
    os.getenv("SESSION_EXPIRE_DAYS", "30")
)

SESSION_COOKIE_MAX_AGE = (
    SESSION_EXPIRE_DAYS * 24 * 60 * 60
)

COOKIE_SECURE = (
    os.getenv("COOKIE_SECURE", "false")
    .strip()
    .lower()
    == "true"
)

COOKIE_SAMESITE = os.getenv(
    "COOKIE_SAMESITE",
    "lax",
).strip().lower()


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


# ---------------------------------------------------------
# Generate OTP
# ---------------------------------------------------------

@router.post("/generate-otp")
async def generate_otp_api(
    data: GenerateOTPRequest,
):
    cooldown_key = f"cooldown:{data.phone}"
    otp_key = f"otp:{data.phone}"

    if redis_client.exists(cooldown_key):
        raise HTTPException(
            status_code=429,
            detail=(
                "Please wait before requesting another OTP."
            ),
        )

    otp = generate_otp()
    hashed_otp = hash_otp(otp)

    redis_client.setex(
        otp_key,
        OTP_EXPIRY,
        hashed_otp,
    )

    redis_client.setex(
        cooldown_key,
        OTP_COOLDOWN,
        "locked",
    )

    try:
        send_whatsapp_otp(
            data.phone,
            otp,
        )

    except requests.exceptions.HTTPError as error:
        redis_client.delete(otp_key)
        redis_client.delete(cooldown_key)

        provider_message = (
            "Failed to send OTP via WhatsApp"
        )

        if error.response is not None:
            try:
                response_data = error.response.json()

                provider_message = (
                    response_data
                    .get("error", {})
                    .get(
                        "message",
                        provider_message,
                    )
                )

            except ValueError:
                provider_message = (
                    error.response.text
                    or provider_message
                )

        logger.error(
            "WhatsApp OTP send failed for %s: %s",
            data.phone,
            (
                error.response.text
                if error.response is not None
                else str(error)
            ),
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Failed to send OTP via WhatsApp: "
                f"{provider_message}"
            ),
        ) from error

    except Exception as error:
        redis_client.delete(otp_key)
        redis_client.delete(cooldown_key)

        logger.exception(
            "WhatsApp OTP send failed for %s",
            data.phone,
        )

        raise HTTPException(
            status_code=502,
            detail="Failed to send OTP via WhatsApp",
        ) from error

    return {
        "status": "success",
        "message": "OTP sent via WhatsApp",
        "phone": data.phone,
        "retry_after": OTP_COOLDOWN,
    }


# ---------------------------------------------------------
# Verify OTP, save user and create session
# ---------------------------------------------------------

@router.post("/verify-otp")
async def verify_otp(
    data: RegisterVerifyOTPRequest,
    response: Response,
    database: Session = Depends(get_db),
):
    print(
        "VERIFY PAYLOAD:",
        data.name,
        data.email,
        data.phone,
    )
    
    otp_key = f"otp:{data.phone}"
    attempt_key = f"attempt:{data.phone}"
    lock_key = f"lock:{data.phone}"
    cooldown_key = f"cooldown:{data.phone}"

    # Check if phone is locked
    if redis_client.exists(lock_key):
        raise HTTPException(
            status_code=429,
            detail=(
                "Too many failed attempts. "
                "Try again later."
            ),
        )

    stored_otp = redis_client.get(otp_key)

    if stored_otp is None:
        raise HTTPException(
            status_code=404,
            detail="OTP expired or not found",
        )

    submitted_otp_hash = hash_otp(data.otp)

    # OTP matches
    if stored_otp == submitted_otp_hash:
        try:
            user_statement = select(User).where(
                User.phone == data.phone
            )

            user = database.scalar(
                user_statement
            )

            current_time = datetime.now(
                timezone.utc
            )

            # if user is None:
            #     user = User(
            #         phone=data.phone,
            #         name=data.name.strip(),
            #         email=data.email.strip().lower(),
            #         is_phone_verified=True,
            #         status="active",
            #         last_login_at=current_time,
            #     )

            #     database.add(user)

            # else:
            #     if user.status != "active":
            #         raise HTTPException(
            #             status_code=403,
            #             detail="This account is blocked.",
            #         )

            #     user.name = data.name.strip()
            #     user.email = data.email.strip().lower()
            #     user.is_phone_verified = True
            #     user.last_login_at = current_time
            if user is None:
                user = User(
                    phone=data.phone,
                    name=data.name.strip(),
                    email=data.email.strip().lower(),
                    password_hash=hash_password(
                        data.password,
                    ),
                    is_phone_verified=True,
                    status="active",
                    last_login_at=current_time,
                )

                database.add(user)

            else:
                if user.status != "active":
                    raise HTTPException(
                        status_code=403,
                        detail="This account is blocked.",
                    )

                # A password already exists, so this phone number
                # has already completed registration.
                if user.password_hash:
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "This phone number is already registered. "
                            "Please log in using your password."
                        ),
                    )

                # Support users created before password login was added.
                user.name = data.name.strip()
                user.email = data.email.strip().lower()
                user.password_hash = hash_password(
                    data.password,
                )
                user.is_phone_verified = True
                user.last_login_at = current_time

            database.commit()
            database.refresh(user)

            print(
                "SAVED USER:",
                user.id,
                user.name,
                user.email,
                user.phone,
            )

            # Create active session in Redis
            session_id = create_session(
                user_id=user.id,
                phone=user.phone,
            )

            logger.info(
            "Session created for user_id=%s phone=%s",
            user.id,
            user.phone,
            )

            print("Raw session ID generated:", bool(session_id))

        except HTTPException:
            database.rollback()
            raise

        except Exception as error:
            database.rollback()

            logger.exception(
                "Failed to create user/session for %s",
                data.phone,
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "OTP was verified, but login "
                    "session could not be created."
                ),
            ) from error

        # Delete OTP-related Redis records only after
        # user and session creation succeeds.
        redis_client.delete(otp_key)
        redis_client.delete(attempt_key)
        redis_client.delete(cooldown_key)

        print("Setting session cookie")
        print("COOKIE_SECURE:", COOKIE_SECURE)
        print("COOKIE_SAMESITE:", COOKIE_SAMESITE)
        print("COOKIE_MAX_AGE:", SESSION_COOKIE_MAX_AGE)

        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=SESSION_COOKIE_MAX_AGE,
            httponly=True,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            path="/",
        )

        return {
            "status": "success",
            "message": "OTP Verified Successfully",
            "authenticated": True,
            # "user": {
            #     "id": user.id,
            #     "phone": user.phone,
            #     "name": user.name,
            # },
            "user": {
                "id": user.id,
                "phone": user.phone,
                "name": user.name,
                "email": user.email,
            },
        }

    # OTP is incorrect
    attempts = redis_client.incr(
        attempt_key
    )

    # Set expiry on first failed attempt
    if attempts == 1:
        redis_client.expire(
            attempt_key,
            OTP_EXPIRY,
        )

    remaining = (
        MAX_OTP_ATTEMPTS - attempts
    )

    if attempts >= MAX_OTP_ATTEMPTS:
        redis_client.delete(otp_key)
        redis_client.delete(attempt_key)

        redis_client.setex(
            lock_key,
            OTP_LOCK_TIME,
            "locked",
        )

        raise HTTPException(
            status_code=429,
            detail=(
                "Maximum attempts exceeded. "
                "Phone number temporarily locked."
            ),
        )

    raise HTTPException(
        status_code=400,
        detail=(
            f"Invalid OTP. {remaining} "
            "attempts remaining."
        ),
    )



# ---------------------------------------------------------
# Login authenticated user
# ---------------------------------------------------------

@router.post("/login")
async def login_with_password(
    data: LoginRequest,
    response: Response,
    database: Session = Depends(get_db),
):
    user_statement = select(User).where(
        User.phone == data.phone
    )

    user = database.scalar(user_statement)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid phone number or password.",
        )

    if user.status != "active":
        raise HTTPException(
            status_code=403,
            detail="This account is blocked.",
        )

    if not user.password_hash:
        raise HTTPException(
            status_code=409,
            detail=(
                "Password login is not configured for this account. "
                "Please register using OTP first."
            ),
        )

    if not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid phone number or password.",
        )

    current_time = datetime.now(timezone.utc)
    user.last_login_at = current_time

    database.commit()
    database.refresh(user)

    session_id = create_session(
        user_id=user.id,
        phone=user.phone,
    )

    response.set_cookie(
        key="session_id",
        value=session_id,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )

    return {
        "status": "success",
        "message": "Logged in successfully.",
        "authenticated": True,
        "user": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name,
            "email": user.email,
        },
    }

# ---------------------------------------------------------
# Forgot password - check registered phone
# ---------------------------------------------------------

@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    database: Session = Depends(get_db),
    ):
    user_statement = select(User).where(
        User.phone == data.phone
    )

    user = database.scalar(user_statement)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="No account found with this mobile number.",
        )

    if user.status != "active":
        raise HTTPException(
            status_code=403,
            detail="This account is blocked.",
        )

    return {
        "status": "success",
        "message": "Account found. Ready to send password reset OTP.",
        "phone": data.phone,
    }    


# ---------------------------------------------------------
# Restore authenticated user
# ---------------------------------------------------------

@router.get("/me")
async def get_current_user(
    request: Request,
    database: Session = Depends(get_db),
):
    session_id = request.cookies.get(
        "session_id"
    )

    print("/me cookie received:", bool(session_id))

    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated.",
        )

    session_data = get_session(
        session_id
    )

    print("/me session found in Redis:", session_data is not None)

    if session_data is None:
        raise HTTPException(
            status_code=401,
            detail="Session expired or invalid.",
        )

    user_id = session_data.get("user_id")

    if user_id is None:
        delete_session(session_id)

        raise HTTPException(
            status_code=401,
            detail="Invalid session data.",
        )

    user = database.get(
        User,
        int(user_id),
    )

    if user is None:
        delete_session(session_id)

        raise HTTPException(
            status_code=401,
            detail="User does not exist.",
        )

    if user.status != "active":
        delete_session(session_id)

        raise HTTPException(
            status_code=403,
            detail="This account is blocked.",
        )

    return {
        "status": "success",
        "authenticated": True,
        # "user": {
        #     "id": user.id,
        #     "phone": user.phone,
        #     "name": user.name,
        # },
        "user": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name,
            "email": user.email,
        },
    }


# ---------------------------------------------------------
# Logout
# ---------------------------------------------------------

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
):
    session_id = request.cookies.get(
        "session_id"
    )

    if session_id:
        delete_session(session_id)

    response.delete_cookie(
        key="session_id",
        path="/",
        secure=COOKIE_SECURE,
        httponly=True,
        samesite=COOKIE_SAMESITE,
    )

    return {
        "status": "success",
        "message": "Logged out successfully.",
    }