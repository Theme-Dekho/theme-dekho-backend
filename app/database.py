# import os
# from collections.abc import Generator

# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# if not DATABASE_URL:
#     raise RuntimeError(
#         "DATABASE_URL is missing from the .env file."
#     )


# class Base(DeclarativeBase):
#     pass


# engine = create_engine(
#     DATABASE_URL,
#     pool_pre_ping=True,
#     pool_recycle=3600,
#     echo=False,
# )


# SessionLocal = sessionmaker(
#     bind=engine,
#     autoflush=False,
#     autocommit=False,
#     expire_on_commit=False,
# )


# def get_db() -> Generator[Session, None, None]:
#     database = SessionLocal()

#     try:
#         yield database
#     finally:
#         database.close()



import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is missing from the .env file."
    )


# BASE_DIR = Path(__file__).resolve().parent.parent
# CA_CERT_PATH = BASE_DIR / "ca.pem"
BASE_DIR = Path(__file__).resolve().parent.parent

CA_CERT_PATH = Path(
    os.getenv(
        "CA_CERT_PATH",
        str(BASE_DIR / "ca.pem"),
    )
)

if not CA_CERT_PATH.exists():
    raise RuntimeError(
        f"Aiven CA certificate not found: {CA_CERT_PATH}"
    )


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    connect_args={
        "ssl": {
            "ca": str(CA_CERT_PATH),
        }
    },
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    database = SessionLocal()

    try:
        yield database
    finally:
        database.close()