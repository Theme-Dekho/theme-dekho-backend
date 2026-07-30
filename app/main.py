# from app.redis_client import redis_client
# from fastapi import FastAPI
# from app.routes.auth import router as auth_router
# from app.database import Base, engine
# from app import models
# from app.routes import account
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI(
#     title="OTP Verification API",
#     version="1.0.0"
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://127.0.0.1:3000",
#         "http://localhost:3000",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Base.metadata.create_all(bind=engine)

# app.include_router(auth_router)
# app.include_router(account.router)


# @app.get("/check-otp/{phone}")
# async def check_otp(phone: str):

#     otp = redis_client.get(f"otp:{phone}")

#     return {
#         "phone": phone,
#         "otp": otp
#     }


# @app.get("/")
# async def root():
#     return {
#         "status": "success",
#         "message": "OTP API Running"
#     }

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes import account
from app.routes.analytics import router as analytics_router


app = FastAPI(
    title="OTP Verification API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "https://theme-dekho-project.vercel.app/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(account.router)
app.include_router(analytics_router)