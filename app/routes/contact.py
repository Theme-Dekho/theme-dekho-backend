from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ContactRequest
from app.services.crm_lead_service import send_lead_to_crm

router = APIRouter(prefix="/api", tags=["Contact"])

class ContactRequestCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    message: str
    source_url: str | None = None

@router.post("/contact-requests")
async def create_contact_request(
    payload: ContactRequestCreate,
    db: Session = Depends(get_db)
):
    try:
        db_contact = ContactRequest(
            name=payload.name.strip(),
            email=payload.email.strip(),
            phone=payload.phone.strip(),
            message=payload.message.strip(),
            source_url=payload.source_url,
            status="submitted"
        )
        
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)

        try:
            crm_response = send_lead_to_crm(
                name=db_contact.name,
                phone=db_contact.phone,
                email=db_contact.email,
                source="Theme Dekho - Contact Form",
                notes=(
                    f"Message: {db_contact.message}\n"
                    f"Source URL: {db_contact.source_url or 'Not provided'}"
                ),
            )
            print("CRM lead submission response:", crm_response)

        except Exception as error:
            print("CRM lead submission failed:", str(error))


    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save contact request: {str(e)}"
        )