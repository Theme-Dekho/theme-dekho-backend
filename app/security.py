import hashlib

def hash_otp(otp: str) -> str:
    """
    Returns SHA256 hash of OTP.
    """
    return hashlib.sha256(
        otp.encode()
    ).hexdigest()