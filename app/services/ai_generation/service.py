from app.services.ai_generation.template_router import (
    get_template_type,
)
from app.services.ai_generation.llm_client import (
    generate_structured_content,
)
from app.services.ai_generation.reference_images import (
    get_reference_image_path,
)


# Interior
from app.services.ai_generation.interior.prompt import (
    build_interior_prompt,
)

from app.services.ai_generation.interior.schema import (
    InteriorGeneratedContent,
)

# Healthcare
from app.services.ai_generation.healthcare.prompt import (
    build_healthcare_prompt,
)

from app.services.ai_generation.healthcare.schema import (
    HealthcareGeneratedContent,
)

# Real Estate
from app.services.ai_generation.real_estate.prompt import (
    build_real_estate_prompt,
)

from app.services.ai_generation.real_estate.schema import (
    RealEstateGeneratedContent,
)

def generate_website_content(generation):
    template_type = get_template_type(
        generation.industry
    )

    reference_image_path = (
        get_reference_image_path(
            template_type
        )
    )

    print(
        "TEMPLATE:",
        template_type,
        "| REFERENCE IMAGE:",
        reference_image_path,
    )

    if template_type == "interior":
        prompt = build_interior_prompt(
            generation
        )

        generated_content = generate_structured_content(
            prompt=prompt,
            response_model=InteriorGeneratedContent,
            reference_image_path=reference_image_path,
        )

        return {
            "template_type": template_type,
            "content": generated_content.model_dump(),
        }


    if template_type == "healthcare":
        prompt = build_healthcare_prompt(
            generation
        )

        generated_content = generate_structured_content(
            prompt=prompt,
            response_model=HealthcareGeneratedContent,
            reference_image_path=reference_image_path,
        )

        return {
            "template_type": template_type,
            "content": generated_content.model_dump(),
        }


    if template_type == "real_estate":
        prompt = build_real_estate_prompt(
            generation
        )

        generated_content = generate_structured_content(
            prompt=prompt,
            response_model=RealEstateGeneratedContent,
            reference_image_path=reference_image_path,
        )

        return {
            "template_type": template_type,
            "content": generated_content.model_dump(),
        }


    raise ValueError(
        f"Generation is not implemented for template: {template_type}"
    )