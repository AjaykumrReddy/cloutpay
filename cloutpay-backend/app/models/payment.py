from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Boolean
from datetime import datetime
from app.db import Base


class PaymentOrder(Base):
    __tablename__ = "payment_orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    razorpay_order_id = Column(String, unique=True, index=True)
    amount = Column(Integer)
    currency = Column(String, default="INR")

    status = Column(String, default="created")  # created, paid, failed

    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("payment_orders.id"))

    razorpay_payment_id = Column(String, unique=True, index=True)
    amount = Column(Integer)

    user_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)