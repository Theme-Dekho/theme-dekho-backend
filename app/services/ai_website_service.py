from datetime import timedelta
from app.models import AIWebsiteGeneration
from app.models import now_ist
from app.services.llm_service import (generate_website_content)


def mark_generation_completed(
    generation: AIWebsiteGeneration,
    generated_url: str,
    generated_content: dict,
    llm_provider: str,
    llm_model: str,
) -> None:
    generation.generation_status = "completed"

    generation.generated_url = generated_url

    generation.expires_at = (
        now_ist() + timedelta(days=20)
    )

    generation.generated_content = generated_content

    generation.llm_provider = llm_provider
    generation.llm_model = llm_model

    generation.error_message = None

def build_generation_prompt(
    generation: AIWebsiteGeneration,
) -> str:
    pages = ", ".join(
        generation.selected_pages or []
    )

    features = ", ".join(
        generation.selected_features or []
    )

    return f"""
You are an expert website designer and copywriter.

Create a professional website specification for the following business.

BUSINESS INFORMATION

Business Name:
{generation.business_name}

Industry:
{generation.industry}

Sub-Industry:
{generation.sub_industry}

Phone:
{generation.business_phone}

Email:
{generation.business_email or "Not provided"}

Address:
{generation.business_address or "Not provided"}

Business Description:
{generation.business_description or "Not provided"}

SELECTED WEBSITE PAGES

{pages}

SELECTED WEBSITE FEATURES

{features or "No additional features selected"}

REQUIREMENTS

1. Generate content only for the selected pages.
2. The website must match the business industry and sub-industry.
3. Write professional and conversion-focused content.
4. Do not invent certifications, awards, statistics, doctors, projects,
   testimonials, addresses, prices, or claims that were not provided.
5. Use the provided business phone and email for contact information.
6. Make the content suitable for desktop and mobile websites.
7. Keep headings concise and professional.
8. Include clear call-to-action text where appropriate.

Return structured website data that can later be rendered by our frontend.
""".strip()


def generate_ai_website(
    generation: AIWebsiteGeneration,
) -> dict:
    prompt = build_generation_prompt(
        generation
    )

    generated_website = generate_website_content(
        prompt
    )

    return generated_website.model_dump()