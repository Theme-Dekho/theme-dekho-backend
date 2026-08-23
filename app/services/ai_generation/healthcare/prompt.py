def build_healthcare_prompt(generation) -> str:
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
You are a professional healthcare website copywriter.

Generate structured content for a fixed Healthcare website template.

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
- Keep the writing professional, trustworthy, clear, and concise.
- Use language suitable for healthcare, hospitals, clinics, medical tourism, dental clinics, IVF centers, diagnostics, or related businesses.
- Use supplied phone, email, and address exactly.
- Do not invent doctors, medical professionals, qualifications, certifications, accreditations, awards, ratings, success rates, treatment outcomes, prices, years of experience, patient counts, hospital bed counts, or medical claims.
- Generate exactly 3 highlights.
- Generate exactly 6 healthcare services.
- Doctors must be an empty list unless doctor information was explicitly supplied in the business description.
- Generate exactly 4 process steps.
- Generate one About section.
- Testimonials must be empty unless testimonial information was explicitly supplied by the user.
- Do not provide medical advice.
- Do not make guaranteed treatment or outcome claims.

COLOR RULES
Generate a professional healthcare color palette.

All colors must be valid HEX values.

Prefer clean, calm, trustworthy healthcare colors.

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
    "backgroundSoft": "#F4F8FA",
    "primary": "#176B87",
    "secondary": "#2E8A99",
    "accent": "#64CCC5",
    "text": "#102A32"
  }},

  "highlights": [
    {{
      "title": "string",
      "label": "string"
    }}
  ],

  "services": [
    {{
      "title": "string",
      "description": "string"
    }}
  ],

  "doctors": [],

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