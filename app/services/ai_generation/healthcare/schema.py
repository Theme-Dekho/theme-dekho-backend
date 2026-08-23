from pydantic import BaseModel, Field


class HealthcareColors(BaseModel):
    background: str
    backgroundSoft: str
    primary: str
    secondary: str
    accent: str
    text: str


class HealthcareService(BaseModel):
    title: str
    description: str


class HealthcareHighlight(BaseModel):
    title: str
    label: str


class HealthcareDoctor(BaseModel):
    name: str
    specialization: str


class HealthcareProcessStep(BaseModel):
    title: str
    description: str


class HealthcareTestimonial(BaseModel):
    name: str
    text: str


class HealthcareGeneratedContent(BaseModel):
    businessName: str
    tagline: str
    description: str

    phone: str | None = None
    email: str | None = None
    address: str | None = None

    colors: HealthcareColors

    highlights: list[HealthcareHighlight] = Field(
        default_factory=list
    )

    services: list[HealthcareService] = Field(
        default_factory=list
    )

    doctors: list[HealthcareDoctor] = Field(
        default_factory=list
    )

    process: list[HealthcareProcessStep] = Field(
        default_factory=list
    )

    aboutTitle: str
    aboutDescription: str

    testimonials: list[HealthcareTestimonial] = Field(
        default_factory=list
    )