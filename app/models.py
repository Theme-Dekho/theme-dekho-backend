from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import BigInteger, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from sqlalchemy import (
    Column,
    JSON,
    func
)

IST = ZoneInfo("Asia/Kolkata")

def now_ist() -> datetime:
    """
    Return the current Indian Standard Time as a naive datetime.

    MySQL DATETIME does not store timezone information, so tzinfo is removed
    after calculating the correct Asia/Kolkata time.
    """
    return datetime.now(IST).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    phone: Mapped[str] = mapped_column(
        String(15),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_phone_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        # default=datetime.now(IST),
        default=now_ist
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        # default=datetime.now(IST),
        default=now_ist,
        onupdate=now_ist
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

class ActivityEvent(Base):
    __tablename__ = "activity_events"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    session_id = Column(
        String(64),
        nullable=False,
        index=True,
    )

    user_id = Column(
        BigInteger,
        nullable=True,
        index=True,
    )

    ip_hash = Column(
    String(64),
    nullable=True,
    index=True,
    )

    event_name = Column(
        String(100),
        nullable=False,
        index=True,
    )

    page_url = Column(
        String(500),
        nullable=True,
    )

    element_name = Column(
        String(150),
        nullable=True,
    )

    event_metadata = Column(
        "metadata",
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=now_ist,
        index=True,
    )    