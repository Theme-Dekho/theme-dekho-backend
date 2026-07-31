from pydantic import BaseModel, Field, EmailStr, field_validator
import re
from typing import Any


class GenerateOTPRequest(BaseModel):
    phone: str = Field(...)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        value = value.strip()

        if not re.fullmatch(r"[6-9]\d{9}", value):
            raise ValueError("Invalid Indian Mobile Number")

        return value


# class VerifyOTPRequest(BaseModel):
#     phone: str
#     otp: str
class VerifyOTPRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str
    otp: str


class AnalyticsEventCreate(BaseModel):
    session_id: str = Field(
        min_length=10,
        max_length=64,
    )

    event_name: str = Field(
        min_length=1,
        max_length=100,
    )

    page_url: str | None = Field(
        default=None,
        max_length=500,
    )

    element_name: str | None = Field(
        default=None,
        max_length=150,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("session_id")
    @classmethod
    def validate_session_id(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Session ID cannot be empty.",
            )

        return cleaned_value

    @field_validator("event_name")
    @classmethod
    def validate_event_name(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip().lower()

        if not cleaned_value:
            raise ValueError(
                "Event name cannot be empty.",
            )

        return cleaned_value    