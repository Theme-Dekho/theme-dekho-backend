from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes import attribution
from app.routes import account
from app.routes.analytics import router as analytics_router
from app.routes.wishlist import router as wishlist_router
from app.routes.enquiries import router as enquiries_router
from app.routes import quote_request
from app.routes import contact
from app.routes import ai_website

app = FastAPI(
    title="OTP Verification API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "https://themedekho.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(attribution.router)
app.include_router(account.router)
app.include_router(analytics_router)
app.include_router(wishlist_router)
app.include_router(enquiries_router)
app.include_router(quote_request.router)
app.include_router(contact.router)
app.include_router(ai_website.router)