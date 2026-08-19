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
#     name: str = Field(min_length=2, max_length=100)
#     email: EmailStr
#     phone: str
#     otp: str
class RegisterVerifyOTPRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    phone: str

    otp: str = Field(
        min_length=4,
        max_length=6,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if not re.fullmatch(r"[6-9]\d{9}", cleaned_value):
            raise ValueError(
                "Invalid Indian Mobile Number",
            )

        return cleaned_value

    @field_validator("password")
    @classmethod
    def validate_password(
        cls,
        value: str,
    ) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain at least one uppercase letter.",
            )

        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain at least one lowercase letter.",
            )

        if not re.search(r"\d", value):
            raise ValueError(
                "Password must contain at least one number.",
            )

        return value
    

class ForgotPasswordRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        phone = value.strip()

        if not phone.isdigit():
            raise ValueError(
                "Mobile number must contain only digits."
            )

        if len(phone) != 10:
            raise ValueError(
                "Enter a valid 10-digit mobile number."
            )

        if phone[0] not in "6789":
            raise ValueError(
                "Enter a valid Indian mobile number."
            )

        return phone   
    

class VerifyResetOTPRequest(BaseModel):
    phone: str

    otp: str = Field(
        min_length=4,
        max_length=6,
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if not re.fullmatch(r"[6-9]\d{9}", cleaned_value):
            raise ValueError(
                "Invalid Indian Mobile Number",
            )

        return cleaned_value

    @field_validator("otp")
    @classmethod
    def validate_otp(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value.isdigit():
            raise ValueError(
                "OTP must contain only digits.",
            )

        return cleaned_value 


class ResetPasswordRequest(BaseModel):
    phone: str

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if not re.fullmatch(r"[6-9]\d{9}", cleaned_value):
            raise ValueError(
                "Invalid Indian Mobile Number",
            )

        return cleaned_value

    @field_validator("new_password")
    @classmethod
    def validate_new_password(
        cls,
        value: str,
    ) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain at least one uppercase letter.",
            )

        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain at least one lowercase letter.",
            )

        if not re.search(r"\d", value):
            raise ValueError(
                "Password must contain at least one number.",
            )

        return value
    

class LoginRequest(BaseModel):
    phone: str
    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if not re.fullmatch(r"[6-9]\d{9}", cleaned_value):
            raise ValueError(
                "Invalid Indian Mobile Number",
            )

        return cleaned_value    


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


class AIWebsiteGenerationCreate(BaseModel):
    source_page: str = Field(
        min_length=2,
        max_length=50,
    )

    industry: str = Field(
        min_length=2,
        max_length=100,
    )

    sub_industry: str = Field(
        min_length=2,
        max_length=150,
    )

    selected_pages: list[str] = Field(
        min_length=1,
    )

    selected_features: list[str] = Field(
        default_factory=list,
    )

    business_name: str = Field(
        min_length=2,
        max_length=150,
    )

    business_phone: str = Field(
        min_length=10,
        max_length=20,
    )

    business_email: EmailStr | None = None

    business_address: str | None = Field(
        default=None,
        max_length=255,
    )

    business_description: str | None = Field(
        default=None,
        max_length=5000,
    )

    # @field_validator("source_page")
    # @classmethod
    # def validate_source_page(
    #     cls,
    #     value: str,
    # ) -> str:
    #     cleaned_value = value.strip().lower()

    #     allowed_sources = {
    #         "ai_builder",
    #         "build_interior",
    #     }

    #     if cleaned_value not in allowed_sources:
    #         raise ValueError(
    #             "Invalid AI builder source page.",
    #         )

    #     return cleaned_value
    @field_validator("source_page")
    @classmethod
    def validate_source_page(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip().lower()

        if cleaned_value == "ai_builder":
            return cleaned_value

        if re.fullmatch(
            r"build_[a-z0-9_]+",
            cleaned_value,
        ):
            return cleaned_value

        raise ValueError(
            "Invalid AI builder source page.",
        )
    

    @field_validator("business_phone")
    @classmethod
    def validate_business_phone(
        cls,
        value: str,
    ) -> str:
        cleaned_value = re.sub(r"\D", "", value)

        if not re.fullmatch(r"[6-9]\d{9}", cleaned_value):
            raise ValueError(
                "Invalid Indian Mobile Number",
            )

        return cleaned_value

class AIWebsiteGenerationResponse(BaseModel):
    id: int
    user_id: int

    source_page: str

    industry: str
    sub_industry: str

    selected_pages: list[str]
    selected_features: list[str]

    business_name: str
    business_phone: str
    business_email: str | None
    business_address: str | None
    business_description: str | None

    generation_status: str

    generated_url: str | None
    expires_at: datetime | None

    llm_provider: str | None
    llm_model: str | None

    generated_content: dict[str, Any] | None

    error_message: str | None

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }

class AIWebsiteCTA(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=100,
    )

    style: str | None = Field(
        default=None,
        max_length=50,
    )

    action: str | None = Field(
        default=None,
        max_length=100,
    )


class AIWebsiteItem(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    icon: str | None = Field(
        default=None,
        max_length=100,
    )

    label: str | None = Field(
        default=None,
        max_length=100,
    )


class AIWebsiteSection(BaseModel):
    section_type: str = Field(
        min_length=1,
        max_length=100,
    )

    layout: str | None = Field(
        default=None,
        max_length=500,
    )

    visual_style: str | None = Field(
        default=None,
        max_length=150,
    )

    background_style: str | None = Field(
        default=None,
        max_length=100,
    )

    heading: str | None = Field(
        default=None,
        max_length=200,
    )

    eyebrow: str | None = Field(
        default=None,
        max_length=100,
    )

    subheading: str | None = Field(
        default=None,
        max_length=500,
    )

    content: str | None = Field(
        default=None,
        max_length=5000,
    )

    items: list[AIWebsiteItem] = Field(
        default_factory=list,
    )

    primary_cta: AIWebsiteCTA | None = None

    secondary_cta: AIWebsiteCTA | None = None

    image_direction: str | None = Field(
        default=None,
        max_length=1000,
    )

    alignment: str | None = Field(
        default=None,
        max_length=50,
    )

    columns: int | None = Field(
        default=None,
        ge=1,
        le=4,
    )


class AIWebsitePage(BaseModel):
    page_name: str = Field(
        min_length=1,
        max_length=100,
    )

    slug: str = Field(
        default="",
        max_length=150,
    )

    @field_validator("slug")
    @classmethod
    def normalize_slug(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip().lower()

        if not cleaned_value:
            return "home"

        cleaned_value = re.sub(
            r"[^a-z0-9]+",
            "-",
            cleaned_value,
        )

        return cleaned_value.strip("-") or "home"

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    meta_description: str | None = Field(
        default=None,
        max_length=300,
    )

    page_style: str | None = Field(
        default=None,
        max_length=150,
    )

    sections: list[AIWebsiteSection] = Field(
        default_factory=list,
    )


class AIWebsiteTheme(BaseModel):
    style: str = Field(
        min_length=1,
        max_length=500,
    )

    primary_color: str = Field(
        min_length=4,
        max_length=20,
    )

    secondary_color: str = Field(
        min_length=4,
        max_length=20,
    )

    accent_color: str | None = Field(
        default=None,
        max_length=20,
    )

    background_color: str | None = Field(
        default=None,
        max_length=20,
    )

    surface_color: str | None = Field(
        default=None,
        max_length=20,
    )

    text_color: str | None = Field(
        default=None,
        max_length=20,
    )

    muted_text_color: str | None = Field(
        default=None,
        max_length=20,
    )

    heading_font: str | None = Field(
        default=None,
        max_length=100,
    )

    body_font: str | None = Field(
        default=None,
        max_length=100,
    )

    button_style: str | None = Field(
        default=None,
        max_length=500,
    )

    card_style: str | None = Field(
        default=None,
        max_length=500,
    )

    border_radius: str | None = Field(
        default=None,
        max_length=50,
    )

    shadow_style: str | None = Field(
        default=None,
        max_length=500,
    )


class AIGeneratedWebsite(BaseModel):
    business_name: str

    tagline: str | None = None

    industry: str
    sub_industry: str

    brand_personality: str | None = Field(
        default=None,
        max_length=500,
    )

    theme: AIWebsiteTheme

    pages: list[AIWebsitePage]

    features: list[str] = Field(
        default_factory=list,
    )

    phone: str
    email: str | None = None
    address: str | None = None    

# class AIWebsiteSection(BaseModel):
#     section_type: str = Field(
#         min_length=1,
#         max_length=100,
#     )

#     heading: str | None = Field(
#         default=None,
#         max_length=200,
#     )

#     subheading: str | None = Field(
#         default=None,
#         max_length=500,
#     )

#     content: str | None = Field(
#         default=None,
#         max_length=5000,
#     )

#     cta_text: str | None = Field(
#         default=None,
#         max_length=100,
#     )


# class AIWebsitePage(BaseModel):
#     page_name: str = Field(
#         min_length=1,
#         max_length=100,
#     )

#     slug: str = Field(
#         min_length=1,
#         max_length=150,
#     )

#     title: str = Field(
#         min_length=1,
#         max_length=200,
#     )

#     meta_description: str | None = Field(
#         default=None,
#         max_length=300,
#     )

#     sections: list[AIWebsiteSection] = Field(
#         default_factory=list,
#     )


# class AIWebsiteTheme(BaseModel):
#     style: str = Field(
#         min_length=1,
#         max_length=100,
#     )

#     primary_color: str = Field(
#         min_length=4,
#         max_length=20,
#     )

#     secondary_color: str = Field(
#         min_length=4,
#         max_length=20,
#     )

#     accent_color: str | None = Field(
#         default=None,
#         max_length=20,
#     )

#     font_style: str | None = Field(
#         default=None,
#         max_length=100,
#     )


# class AIGeneratedWebsite(BaseModel):
#     business_name: str

#     tagline: str | None = None

#     industry: str
#     sub_industry: str

#     theme: AIWebsiteTheme

#     pages: list[AIWebsitePage]

#     features: list[str] = Field(
#         default_factory=list,
#     )

#     phone: str
#     email: str | None = None
#     address: str | None = None                