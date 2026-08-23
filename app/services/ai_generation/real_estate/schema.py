from pydantic import BaseModel, Field


class RealEstateColors(BaseModel):
    background: str
    backgroundSoft: str
    primary: str
    secondary: str
    accent: str
    text: str


class RealEstateHighlight(BaseModel):
    title: str
    label: str


class RealEstateProperty(BaseModel):
    title: str
    location: str
    propertyType: str


class RealEstateService(BaseModel):
    title: str
    description: str


class RealEstateProcessStep(BaseModel):
    title: str
    description: str


class RealEstateTestimonial(BaseModel):
    name: str
    text: str


class RealEstateGeneratedContent(BaseModel):
    businessName: str
    tagline: str
    description: str

    phone: str | None = None
    email: str | None = None
    address: str | None = None

    colors: RealEstateColors

    highlights: list[RealEstateHighlight] = Field(
        default_factory=list
    )

    properties: list[RealEstateProperty] = Field(
        default_factory=list
    )

    services: list[RealEstateService] = Field(
        default_factory=list
    )

    process: list[RealEstateProcessStep] = Field(
        default_factory=list
    )

    aboutTitle: str
    aboutDescription: str

    testimonials: list[RealEstateTestimonial] = Field(
        default_factory=list
    )