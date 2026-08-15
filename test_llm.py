from app.services.llm_service import generate_website_content


prompt = """
Create a simple website specification for an interior design business.

Business Name: Demo Interiors
Industry: Interior & Architecture
Sub-Industry: Interior Firm
Phone: 9876543210
Email: demo@example.com
Address: New Delhi

Pages:
Home, About Us, Services, Contact

Features:
WhatsApp Chat, Contact Form
"""


result = generate_website_content(prompt)

print(
    result.model_dump_json(
        indent=2,
    )
)