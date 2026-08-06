import hashlib
from passlib.context import CryptContext


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_otp(otp: str) -> str:
    """
    Returns SHA256 hash of OTP.
    """
    return hashlib.sha256(
        otp.encode()
    ).hexdigest()



def hash_password(password: str) -> str:
    return password_context.hash(password)



def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    return password_context.verify(
        plain_password,
        password_hash,
    )