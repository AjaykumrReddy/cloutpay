from datetime import datetime
import secrets

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index

from app.db import Base


def _generate_share_token() -> str:
    return secrets.token_urlsafe(8)  # 11-char URL-safe string


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Identity
    phone_number = Column(String(15), unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=True)
    share_token = Column(String(16), unique=True, index=True, nullable=True, default=_generate_share_token)

    # Auth flags
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_anonymous = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_login = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_phone_created", "phone_number", "created_at"),
    )

