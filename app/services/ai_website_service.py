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

# def build_generation_prompt(
#     generation: AIWebsiteGeneration,
# ) -> str:
#     pages = ", ".join(
#         generation.selected_pages or []
#     )

#     features = ", ".join(
#         generation.selected_features or []
#     )

#     return f"""
# You are an expert website designer and copywriter.

# Create a professional website specification for the following business.

# BUSINESS INFORMATION

# Business Name:
# {generation.business_name}

# Industry:
# {generation.industry}

# Sub-Industry:
# {generation.sub_industry}

# Phone:
# {generation.business_phone}

# Email:
# {generation.business_email or "Not provided"}

# Address:
# {generation.business_address or "Not provided"}

# Business Description:
# {generation.business_description or "Not provided"}

# SELECTED WEBSITE PAGES

# {pages}

# SELECTED WEBSITE FEATURES

# {features or "No additional features selected"}

# REQUIREMENTS

# 1. Generate content only for the selected pages.
# 2. The website must match the business industry and sub-industry.
# 3. Write professional and conversion-focused content.
# 4. Do not invent certifications, awards, statistics, doctors, projects,
#    testimonials, addresses, prices, or claims that were not provided.
# 5. Use the provided business phone and email for contact information.
# 6. Make the content suitable for desktop and mobile websites.
# 7. Keep headings concise and professional.
# 8. Include clear call-to-action text where appropriate.

# Return structured website data that can later be rendered by our frontend.
# """.strip()

def build_generation_prompt(generation) -> str:
    selected_pages = generation.selected_pages or []
    selected_features = generation.selected_features or []

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
You are a senior UI/UX designer, conversion-focused copywriter,
brand strategist, and professional website architect.

Your task is to create the complete content and design direction for
a polished, modern, production-quality business website.

The website must look like it was designed by a professional digital
agency, not generated from a generic AI template.

==================================================
BUSINESS INFORMATION
==================================================

Business Name:
{generation.business_name}

Industry:
{generation.industry}

Sub-Industry:
{generation.sub_industry}

Phone:
{generation.business_phone or "Not provided"}

Email:
{generation.business_email or "Not provided"}

Business Address:
{generation.business_address or "Not provided"}

Business Description:
{generation.business_description or "Not provided"}

Requested Pages:
{pages_text}

Requested Features:
{features_text}

==================================================
PRIMARY OBJECTIVE
==================================================

Create a professional, credible, premium-looking website that:

- immediately communicates what the business does
- builds trust within the first few seconds
- has strong visual hierarchy
- has clear conversion-focused calls to action
- feels specific to this business and industry
- avoids generic AI-generated wording
- is suitable for real customers
- works well on desktop, tablet, and mobile
- follows modern UI/UX standards
- feels visually consistent across every page

The result should resemble work produced by an experienced
web design and branding agency.

==================================================
DESIGN DIRECTION
==================================================

Choose a visual style appropriate for the specific industry and
sub-industry.

The website must use:

- a professional modern layout
- generous whitespace
- consistent spacing
- strong typography hierarchy
- restrained and intentional use of color
- clear section separation
- attractive cards where appropriate
- modern buttons
- premium-looking hero sections
- balanced content density
- clean navigation
- polished footer
- consistent border radius
- subtle visual depth
- industry-appropriate imagery direction
- professional icon usage
- strong alignment and grid structure

Avoid:

- random bright colors
- excessive gradients
- excessive rounded cards
- excessive shadows
- cluttered sections
- walls of text
- repeated sections
- childish visual styling
- generic startup-template appearance
- unnecessary emojis
- exaggerated marketing claims

==================================================
BRAND SYSTEM
==================================================

Create a coherent visual identity.

Choose:

1. Primary brand color
2. Secondary brand color
3. Accent color
4. Main background color
5. Alternate section background color
6. Main text color
7. Muted text color
8. Heading typography style
9. Body typography style
10. Button style
11. Card style

The colors must suit the business industry.

Examples:

Healthcare:
clean, trustworthy, calm, accessible.

Interior / Architecture:
premium, editorial, elegant, image-led.

Technology:
modern, precise, innovative.

Professional Services:
credible, minimal, structured.

Hospitality:
warm, aspirational, visual.

Do not blindly use blue for every business.

==================================================
GLOBAL WEBSITE STRUCTURE
==================================================

The website should have a professional header containing:

- logo / business name
- primary navigation
- prominent primary CTA

The primary CTA should be appropriate for the business.

Examples:

- Book Consultation
- Request a Quote
- Schedule Appointment
- Get Started
- Contact Us
- Call Now
- Book a Visit

Use the same CTA strategy consistently throughout the website.

The footer should contain:

- business name
- short brand description
- useful page links
- services links where appropriate
- contact details
- address if available
- copyright text

==================================================
HOMEPAGE
==================================================

The homepage must be the strongest page.

Create approximately 7–10 meaningful sections depending on the
industry.

A strong homepage structure may include:

1. Premium Hero Section
2. Trust / credibility indicators
3. About / business introduction
4. Core services
5. Why choose us
6. Process / how it works
7. Featured work, treatments, projects, products, or specialties
8. Benefits / differentiators
9. Testimonials or trust section when appropriate
10. FAQ
11. Strong final CTA
12. Footer

Do not force sections that do not make sense for the industry.

==================================================
HERO SECTION
==================================================

The hero section must contain:

- a strong industry-specific headline
- a clear supporting paragraph
- primary CTA
- optional secondary CTA
- strong visual direction
- immediate business positioning

The headline should communicate value, not just the business name.

Weak:
"Welcome to ABC Interiors"

Better:
"Thoughtfully Designed Interiors Built Around the Way You Live"

Weak:
"Welcome to XYZ Hospital"

Better:
"Advanced Medical Care With Compassion at Every Step"

Do not use generic phrases such as:

- Welcome to our website
- We provide the best services
- Your trusted partner
- One-stop solution
- We are committed to excellence

unless the wording is substantially more specific and meaningful.

==================================================
SERVICES
==================================================

Create realistic service offerings based on the industry and
sub-industry.

Each service should contain:

- clear service name
- concise description
- customer benefit
- appropriate positioning

Do not invent regulated certifications, awards, years of experience,
doctor qualifications, client counts, project counts, licenses, or
other factual claims unless explicitly provided.

==================================================
COPYWRITING
==================================================

Write confident professional copy.

The tone should be:

- clear
- credible
- natural
- concise
- persuasive
- industry appropriate
- human sounding

Avoid:

- repetitive sentences
- buzzword stuffing
- exaggerated claims
- generic filler
- robotic AI language
- excessively long paragraphs

Prefer short paragraphs of approximately 1–3 sentences.

Use strong headings and scannable content.

Every section should have a clear purpose.

==================================================
CONVERSION STRATEGY
==================================================

Guide visitors toward meaningful actions.

Use contextual CTAs throughout the website.

Examples:

For Interior Design:
- View Our Work
- Start Your Project
- Book a Design Consultation

For Healthcare:
- Book Appointment
- Speak With Our Team
- Find a Specialist

For Architecture:
- Discuss Your Project
- Explore Our Work
- Request Consultation

For Business Services:
- Request a Quote
- Schedule Consultation
- Talk to an Expert

Do not place CTAs randomly.

==================================================
TRUST AND CREDIBILITY
==================================================

Use credibility-building content appropriate for the industry.

Possible trust elements:

- transparent process
- service guarantees when genuinely supportable
- professional methodology
- privacy-oriented messaging
- project approach
- support availability
- FAQs
- client-focused benefits

Do not fabricate:

- customer numbers
- review counts
- star ratings
- certifications
- awards
- years in business
- famous clients
- medical credentials
- legal accreditation

If such information is unavailable, use qualitative trust messaging
instead.

==================================================
PAGE GENERATION
==================================================

Create every requested page:

{pages_text}

Each page must:

- have a distinct purpose
- contain its own hero or page header
- contain meaningful sections
- avoid repeating homepage content word-for-word
- maintain consistent branding
- contain relevant CTA opportunities
- use industry-specific content

Do not create thin placeholder pages.

==================================================
FEATURE INTEGRATION
==================================================

Requested website features:

{features_text}

Incorporate these features naturally into appropriate pages or
sections.

Examples:

Contact Form:
place it within a contact or conversion section.

Appointment Booking:
make appointment CTAs prominent throughout relevant healthcare pages.

Gallery:
design a visual project/gallery section.

Testimonials:
use a professional testimonial layout.

WhatsApp:
treat it as a secondary contact method rather than cluttering every
section.

Calculator:
introduce it with explanatory context and clear purpose.

==================================================
RESPONSIVE DESIGN
==================================================

The generated design direction must work on:

- desktop
- tablet
- mobile

On smaller screens:

- navigation should simplify cleanly
- layouts should stack logically
- buttons should remain easy to tap
- typography should remain readable
- sections should not feel overcrowded
- cards should adapt naturally

==================================================
ACCESSIBILITY
==================================================

Follow sensible accessibility principles:

- readable contrast
- clear hierarchy
- descriptive CTA labels
- logical content structure
- readable font sizes
- no important information conveyed only through color
- avoid overly low-contrast muted text

==================================================
SEO
==================================================

Create natural SEO-friendly copy.

Use:

- meaningful page titles
- clear headings
- industry-specific terminology
- location references only when supported by provided information
- descriptive service names
- natural keyword usage

Do not keyword-stuff.

==================================================
FINAL QUALITY CHECK
==================================================

Before producing the final result, internally verify:

- Does this website feel custom to this business?
- Does the homepage establish value immediately?
- Does every section have a reason to exist?
- Is the visual identity consistent?
- Are headings specific rather than generic?
- Are CTAs clear and intentional?
- Are requested pages included?
- Are requested features included?
- Is any unsupported factual claim being invented?
- Would this reasonably look like a professional agency-designed
  business website?

If any answer is no, improve it before returning the final result.

==================================================
OUTPUT REQUIREMENT
==================================================

Return only the structured website data required by the provided
response schema.

Do not return markdown.
Do not explain your reasoning.
Do not wrap the response in code fences.
Do not include commentary outside the required structured output.
"""


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