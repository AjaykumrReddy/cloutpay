from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.db import Base


class HallOfFame(Base):
    __tablename__ = "hall_of_fame"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Integer, nullable=False)
    month = Column(String(7), unique=True, nullable=False)  # e.g. "2025-01"
    recorded_at = Column(DateTime, default=datetime.utcnow)
