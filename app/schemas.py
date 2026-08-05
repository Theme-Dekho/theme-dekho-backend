from pydantic import BaseModel, Field, EmailStr, field_validator
import re
from typing import Any
from datetime import datetime


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

class WishlistItemCreate(BaseModel):
    product_id: str = Field(
        min_length=1,
        max_length=100,
    )

    product_slug: str = Field(
        min_length=1,
        max_length=200,
    )

    product_name: str = Field(
        min_length=1,
        max_length=255,
    )

    product_label: str | None = Field(
        default=None,
        max_length=150,
    )

    product_image: str | None = Field(
        default=None,
        max_length=500,
    )


class WishlistItemResponse(BaseModel):
    id: int
    product_id: str
    product_slug: str
    product_name: str
    product_label: str | None
    product_image: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class WishlistResponse(BaseModel):
    items: list[WishlistItemResponse]
    count: int


class EnquiryCreate(BaseModel):
    product_id: str = Field(
        min_length=1,
        max_length=100,
    )

    product_slug: str = Field(
        min_length=1,
        max_length=200,
    )

    product_name: str = Field(
        min_length=1,
        max_length=255,
    )

    customer_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    phone: str = Field(
        min_length=10,
        max_length=15,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    selected_addons: list[str] = Field(
        default_factory=list,
    )

    message: str | None = Field(
        default=None,
        max_length=2000,
    )


class EnquiryResponse(BaseModel):
    id: int
    product_id: str
    product_slug: str
    product_name: str
    customer_name: str
    email: str
    phone: str
    city: str | None
    selected_addons: list[str] | None
    message: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class EnquiryListResponse(BaseModel):
    items: list[EnquiryResponse]
    count: int    


class QuoteRequestCreate(BaseModel):
    business_name: str = Field(
        min_length=2,
        max_length=150,
    )

    whatsapp_number: str = Field(
        min_length=10,
        max_length=15,
    )

    website_type: str = Field(
        min_length=2,
        max_length=100,
    )

    @field_validator("whatsapp_number")
    @classmethod
    def validate_whatsapp_number(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if not re.fullmatch(r"[6-9]\d{9}", cleaned_value):
            raise ValueError(
                "Invalid Indian WhatsApp number.",
            )

        return cleaned_value


class QuoteRequestResponse(BaseModel):
    id: int
    user_id: int | None
    business_name: str
    whatsapp_number: str
    website_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }    