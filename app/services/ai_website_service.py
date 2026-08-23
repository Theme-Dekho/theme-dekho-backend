from datetime import timedelta
from app.models import AIWebsiteGeneration
from app.models import now_ist
from app.services.llm_service import (generate_website_content)
from app.services.ai_template_config import AI_TEMPLATE_CONFIG


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


# def build_generation_prompt(generation) -> str:
    selected_pages = generation.selected_pages or []
    selected_features = generation.selected_features or []
    # template_instruction = AI_TEMPLATE_CONFIG.get(generation.sub_industry, "")
    template_instruction = AI_TEMPLATE_CONFIG.get(
            generation.sub_industry.strip(),
            """
        Use the default professional website style appropriate
        for the selected industry and sub-industry.
        """,
        )

    pages_text = (
        ", ".join(selected_pages)
        if selected_pages
        else "Home, About, Services, Contact"
    )

    features_text = (
        ", ".join(selected_features)
        if selected_features
        else "Contact Form"
    )

    return f"""
     You are a professional UI/UX designer and website copywriter.

        Create a compact, premium website for:

        BUSINESS
        Name: {generation.business_name}
        Industry: {generation.industry}
        Sub-Industry: {generation.sub_industry}
        Phone: {generation.business_phone or "Not provided"}
        Email: {generation.business_email or "Not provided"}
        Address: {generation.business_address or "Not provided"}
        Description: {generation.business_description or "Not provided"}

        Requested Pages:
        {pages_text}

        Requested Features:
        {features_text}

        Category Direction:
        {template_instruction}

        REFERENCE IMAGE
        Use the attached image only as visual inspiration for layout, hero composition, spacing, typography, CTA placement, and visual density.

        Do not copy its text, branding, logo, images, or exact design.

        IMAGES
        Choose images that are directly relevant to both the Industry and Sub-Industry.

        Image selection must:

        * clearly represent {generation.industry}
        * specifically match {generation.sub_industry}
        * support the purpose of each section
        * look professional, premium, and realistic
        * avoid unrelated generic stock imagery

        For example, a Dental Clinic should use dental treatment, clinic, dentist, or patient-care imagery rather than generic healthcare images.

        DESIGN
        Use a clean, modern, premium style with:

        * light background
        * minimal header
        * strong two-column hero
        * 5–10 word headline
        * 20–40 word supporting text
        * relevant large imagery
        * one primary CTA
        * optional secondary CTA
        * generous whitespace
        * restrained colors
        * professional typography

        Keep the homepage to 1–2 sections:

        1. Hero
        2. Services / Key Offerings
        3. Portfolio / Work Preview, if relevant
        4. Contact / CTA

        CONTENT RULES

        * Generate only requested pages.
        * Limit services to 3–4.
        * Keep copy concise.
        * Use supplied contact details exactly.
        * Do not invent awards, certifications, experience, clients, statistics, ratings, prices, or project counts.
        * Avoid testimonials, large FAQs, long process sections, excessive cards, repeated CTAs, filler content, and generic marketing phrases.

        OUTPUT
        Return ONLY valid JSON with exactly these top-level keys:

        business_name
        tagline
        industry
        sub_industry
        brand_personality
        theme
        pages
        features
        phone
        email
        address

        brand_personality must be a string.

        theme:
        {{
        "style": "string",
        "primary_color": "string",
        "secondary_color": "string"
        }}

        Each page:
        {{
        "page_name": "string",
        "slug": "string",
        "title": "string",
        "meta_description": "string",
        "page_style": "string",
        "sections": []
        }}

        Each section must contain:
        "section_type": "string"

        Never use "section_id".

        Every object inside "items" must contain:
        "title": "string"

        features must be an array of strings.

        Return JSON only. No markdown or explanations.
        """

def build_generation_prompt(generation) -> str:
    selected_pages = generation.selected_pages or []
    selected_features = generation.selected_features or []

    pages_text = (
        ", ".join(selected_pages)
        if selected_pages
        else "Home"
    )

    features_text = (
        ", ".join(selected_features)
        if selected_features
        else "Contact Form"
    )

    return f"""
You are a professional interior website copywriter and UI design assistant.

Generate structured content for a ready-made Interior Firm / Company website template.

BUSINESS
Business Name: {generation.business_name}
Industry: {generation.industry}
Sub-Industry: {generation.sub_industry}
Phone: {generation.business_phone or "Not provided"}
Email: {generation.business_email or "Not provided"}
Address: {generation.business_address or "Not provided"}
Description: {generation.business_description or "Not provided"}

Requested Pages:
{pages_text}

Requested Features:
{features_text}

REFERENCE IMAGE
Use the attached image only as visual inspiration for color mood and overall design feel.

Do not copy:
- text
- logo
- images
- exact branding

CONTENT RULES
- Keep content concise and premium.
- Use natural interior-design language.
- Do not invent awards, ratings, certifications, years of experience,
  client counts, project counts or prices.
- Use supplied phone, email and address exactly.
- Generate exactly 3 highlights.
- Generate exactly 3 project titles.
- Generate exactly 6 process steps.
- Generate one short About section.
- Testimonials may be empty if no real testimonial information exists.

COLOR RULES
Choose a professional color palette suitable for the business.

Return:
- background
- backgroundSoft
- accent
- secondary
- text

Use valid HEX colors only.

OUTPUT FORMAT

Return ONLY valid JSON with exactly this structure:

{{
  "businessName": "string",
  "tagline": "string",
  "description": "string",
  "phone": "string or null",
  "email": "string or null",
  "address": "string or null",

  "colors": {{
    "background": "#FFFFFF",
    "backgroundSoft": "#F5F5F5",
    "accent": "#A8895D",
    "secondary": "#6D5A48",
    "text": "#171717"
  }},

  "highlights": [
    {{
      "title": "string",
      "label": "string"
    }}
  ],

  "projects": [
    {{
      "title": "string"
    }}
  ],

  "process": [
    {{
      "title": "string",
      "description": "string"
    }}
  ],

  "aboutTitle": "string",
  "aboutDescription": "string",

  "testimonials": []
}}

Return JSON only.
No markdown.
No explanations.
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