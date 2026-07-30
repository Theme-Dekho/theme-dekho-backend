import os
from fastapi import HTTPException
from app.otp import generate_otp
from app.redis_client import redis_client
from app.security import hash_otp

OTP_EXPIRY = int(os.getenv("OTP_EXPIRY", 300))

class OTPService:

    @staticmethod
    def generate(phone: str):

        cooldown_key = f"cooldown:{phone}"

        if redis_client.exists(cooldown_key):
            raise HTTPException(
                status_code=429,
                detail="Please wait before requesting another OTP."
            )

        otp = generate_otp()
        hashed_otp = hash_otp(otp)

        redis_client.setex(
            f"otp:{phone}",
            OTP_EXPIRY,
            hashed_otp
        )

        redis_client.setex(
            cooldown_key,
            30,
            "locked"
        )

        return otp

    @staticmethod
    def verify(phone: str, otp: str):
        # We'll move the verification logic here.
        pass