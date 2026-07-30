import os
import secrets
import string
from dotenv import load_dotenv

load_dotenv()

OTP_LENGTH = int(os.getenv("OTP_LENGTH", 4))


def generate_otp():
    return "".join(
        secrets.choice(string.digits)
        for _ in range(OTP_LENGTH)
    )