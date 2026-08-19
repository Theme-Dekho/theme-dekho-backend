from fastapi import ( APIRouter, Depends, HTTPException)
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import ( User, AIWebsiteGeneration, now_ist)
from app.schemas import ( AIWebsiteGenerationCreate, AIWebsiteGenerationResponse)
from app.services.ai_website_service import (generate_ai_website, mark_generation_completed)
from app.config import (LLM_PROVIDER, LLM_MODEL)
from sqlalchemy.exc import IntegrityError


router = APIRouter(
    prefix="/api/ai-websites",
    tags=["AI Website"],
)

CAMPAIGN_INDUSTRY_MAP = {
    "build_interior": "Interior & Architecture",
    "build_healthcare": "Healthcare",
    "build_ecommerce": "E-Commerce & Retail",
    "build_realestate": "Real Estate",
    "build_travel": "Travel & Tourism",
}

@router.post(
    "",
    response_model=AIWebsiteGenerationResponse,
    status_code=201,
)
def create_ai_website_generation(
    payload: AIWebsiteGenerationCreate,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    existing_generation = (
        database.query(AIWebsiteGeneration)
        .filter(
            AIWebsiteGeneration.user_id == current_user.id,
        )
        .with_for_update()
        .first()
    )

    if (
        existing_generation
        and existing_generation.generation_status
        in {
            "pending",
            "generating",
            "completed",
            "expired",
        }
    ):
        raise HTTPException(
            status_code=409,
            detail="You have already used your free AI website generation.",
        )


    industry = CAMPAIGN_INDUSTRY_MAP.get(
        payload.source_page,
        payload.industry.strip(),
    )


    if existing_generation:
        generation = existing_generation

        generation.source_page = payload.source_page
        generation.industry = industry
        generation.sub_industry = payload.sub_industry.strip()

        generation.selected_pages = payload.selected_pages
        generation.selected_features = payload.selected_features

        generation.business_name = payload.business_name.strip()
        generation.business_phone = payload.business_phone

        generation.business_email = (
            str(payload.business_email)
            if payload.business_email
            else None
        )

        generation.business_address = (
            payload.business_address.strip()
            if payload.business_address
            else None
        )

        generation.business_description = (
            payload.business_description.strip()
            if payload.business_description
            else None
        )

        generation.generation_status = "pending"
        generation.generated_url = None
        generation.generated_content = None
        generation.expires_at = None
        generation.llm_provider = None
        generation.llm_model = None
        generation.error_message = None

    else:
        generation = AIWebsiteGeneration(
            user_id=current_user.id,
            source_page=payload.source_page,
            industry=industry,
            sub_industry=payload.sub_industry.strip(),
            selected_pages=payload.selected_pages,
            selected_features=payload.selected_features,
            business_name=payload.business_name.strip(),
            business_phone=payload.business_phone,
            business_email=(
                str(payload.business_email)
                if payload.business_email
                else None
            ),
            business_address=(
                payload.business_address.strip()
                if payload.business_address
                else None
            ),
            business_description=(
                payload.business_description.strip()
                if payload.business_description
                else None
            ),
            generation_status="pending",
        )

        database.add(generation)

    try:
        database.commit()

    except IntegrityError:
        database.rollback()

        raise HTTPException(
            status_code=409,
            detail="You have already used your free AI website generation.",
        )

    database.refresh(generation)


    try:
        generation.generation_status = "generating"

        database.commit()
        database.refresh(generation)

        generated_content = generate_ai_website(
            generation
        )

        mark_generation_completed(
            generation=generation,
            generated_url=f"/generated/{generation.id}",
            generated_content=generated_content,
            llm_provider=LLM_PROVIDER,
            llm_model=LLM_MODEL,
        )

        database.commit()
        database.refresh(generation)

    except Exception as exc:
        generation.generation_status = "failed"
        generation.error_message = str(exc)

        database.commit()

        raise HTTPException(
            status_code=500,
            detail="AI website generation failed.",
        )

    return generation


@router.get(
    "/me",
    response_model=AIWebsiteGenerationResponse,
)
def get_my_ai_website_generation(
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    generation = (
        database.query(AIWebsiteGeneration)
        .filter(
            AIWebsiteGeneration.user_id == current_user.id,
        )
        .first()
    )

    if not generation:
        raise HTTPException(
            status_code=404,
            detail="AI website generation not found.",
        )

    if (
        generation.expires_at
        and generation.expires_at < now_ist()
    ):
        if generation.generation_status != "expired":
            generation.generation_status = "expired"
            database.commit()

        raise HTTPException(
            status_code=410,
            detail="Generated website has expired.",
        )

    return generation


@router.get(
    "/{generation_id}",
    response_model=AIWebsiteGenerationResponse,
)
def get_ai_website_generation(
    generation_id: int,
    database: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    generation = (
        database.query(AIWebsiteGeneration)
        .filter(
            AIWebsiteGeneration.id == generation_id,
            AIWebsiteGeneration.user_id == current_user.id,
        )
        .first()
    )

    if not generation:
        raise HTTPException(
            status_code=404,
            detail="AI website generation not found.",
        )

    if (
        generation.expires_at
        and generation.expires_at < now_ist()
    ):
        generation.generation_status = "expired"

        database.commit()

        raise HTTPException(
            status_code=410,
            detail="Generated website has expired.",
        )

    return generation