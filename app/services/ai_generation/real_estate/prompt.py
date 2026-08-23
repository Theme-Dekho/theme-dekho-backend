def build_real_estate_prompt(generation) -> str:
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
You are a professional real estate website copywriter.

Generate structured content for a fixed Real Estate website template.

BUSINESS
Business Name: {generation.business_name}
Industry: {generation.industry}
Sub-Industry: {generation.sub_industry}
Phone: {generation.business_phone or "Not provided"}
Email: {generation.business_email or "Not provided"}
Address: {generation.business_address or "Not provided"}
Description: {generation.business_description or "Not provided"}

REQUESTED PAGES
{pages_text}

REQUESTED FEATURES
{features_text}

CONTENT RULES
- Keep the writing professional, trustworthy, concise, and sales-focused without exaggeration.
- Use language suitable for real estate agencies, builders, property consultants, brokers, developers, residential projects, commercial property, or property portfolios.
- Use supplied phone, email, and address exactly.
- Do not invent property prices.
- Do not invent availability.
- Do not invent possession dates.
- Do not invent RERA numbers.
- Do not invent project approvals.
- Do not invent property dimensions, floor plans, amenities, locations, or legal status unless explicitly supplied by the user.
- Do not invent awards, ratings, years of experience, client counts, completed-project counts, or sales figures.
- Generate exactly 3 highlights.
- Properties must be an empty list unless actual property/project information was explicitly supplied in the business description.
- Generate exactly 6 services.
- Generate exactly 4 process steps.
- Generate one short About section.
- Testimonials must be empty unless testimonial information was explicitly supplied by the user.

COLOR RULES
Generate a professional Real Estate color palette.

All colors must be valid HEX values.

Prefer premium, trustworthy, modern real estate colors.

OUTPUT RULES
Return ONLY valid JSON.
Do not return markdown.
Do not return explanations.
Do not add extra fields.

Return exactly this structure:

{{
  "businessName": "string",
  "tagline": "string",
  "description": "string",

  "phone": "string or null",
  "email": "string or null",
  "address": "string or null",

  "colors": {{
    "background": "#FFFFFF",
    "backgroundSoft": "#F5F5F2",
    "primary": "#18392B",
    "secondary": "#6B7A70",
    "accent": "#C4A66A",
    "text": "#17211D"
  }},

  "highlights": [
    {{
      "title": "string",
      "label": "string"
    }}
  ],

  "properties": [],

  "services": [
    {{
      "title": "string",
      "description": "string"
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
""".strip()