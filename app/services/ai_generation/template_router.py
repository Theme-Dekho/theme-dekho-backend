from typing import Literal


TemplateType = Literal[
    "interior",
    "healthcare",
    "ecommerce",
    "real_estate",
]


INDUSTRY_TEMPLATE_MAP: dict[str, TemplateType] = {
    "Interior & Architecture": "interior",
    "Medical & Healthcare": "healthcare",
    "Ecommerce": "ecommerce",
    "Real Estate": "real_estate",
}


def get_template_type(industry: str) -> TemplateType:
    normalized_industry = industry.strip()

    template_type = INDUSTRY_TEMPLATE_MAP.get(
        normalized_industry
    )

    if not template_type:
        raise ValueError(
            f"Unsupported industry: {industry}"
        )

    return template_type