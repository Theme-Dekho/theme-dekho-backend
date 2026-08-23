def build_interior_prompt(generation) -> str:
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
You are a professional interior website copywriter.

Generate structured content for a fixed Interior & Architecture website template.

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
- Keep copy concise and premium.
- Use natural interior and architecture language.
- Use supplied phone, email, and address exactly.
- Do not invent awards, certifications, ratings, prices, years of experience, project counts, or client counts.
- Generate exactly 3 highlights.
- Generate exactly 3 project titles.
- Generate exactly 6 process steps.
- Generate one short About section.
- Testimonials must be empty unless testimonial information was supplied by the user.

COLOR RULES
Generate a professional Interior & Architecture color palette.

All colors must be valid HEX values.

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
""".strip()