from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Identity
    phone_number = Column(String(15), unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=True)

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

