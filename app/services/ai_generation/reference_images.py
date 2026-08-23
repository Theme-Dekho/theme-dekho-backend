from pathlib import Path

from app.services.ai_generation.template_router import (
    TemplateType,
)


REFERENCE_IMAGE_DIR = (
    Path(__file__).resolve().parents[2]
    / "reference_images"
)


REFERENCE_IMAGE_MAP: dict[TemplateType, str] = {
    "interior": "interior.png",
    "healthcare": "healthcare.webp",
    "real_estate": "real-estate.png",
    "ecommerce": "ecommerce.webp",
}


def get_reference_image_path(
    template_type: TemplateType,
) -> Path:
    file_name = REFERENCE_IMAGE_MAP.get(
        template_type
    )

    if not file_name:
        raise ValueError(
            f"No reference image configured for: {template_type}"
        )

    image_path = (
        REFERENCE_IMAGE_DIR / file_name
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Reference image not found: {image_path}"
        )

    return image_path