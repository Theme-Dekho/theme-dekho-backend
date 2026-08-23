from pydantic import BaseModel, Field


class InteriorColors(BaseModel):
    background: str
    backgroundSoft: str
    accent: str
    secondary: str
    text: str


class InteriorHighlight(BaseModel):
    title: str
    label: str


class InteriorProject(BaseModel):
    title: str


class InteriorProcessStep(BaseModel):
    title: str
    description: str


class InteriorTestimonial(BaseModel):
    name: str
    text: str


class InteriorGeneratedContent(BaseModel):
    businessName: str
    tagline: str
    description: str

    phone: str | None = None
    email: str | None = None
    address: str | None = None

    colors: InteriorColors

    highlights: list[InteriorHighlight] = Field(
        default_factory=list
    )

    projects: list[InteriorProject] = Field(
        default_factory=list
    )

    process: list[InteriorProcessStep] = Field(
        default_factory=list
    )

    aboutTitle: str
    aboutDescription: str

    testimonials: list[InteriorTestimonial] = Field(
        default_factory=list
    )