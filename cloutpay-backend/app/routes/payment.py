from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_optional_user_id
from app.limiter import limiter
from app.models.payment import Payment
from app.services.payment_service import PaymentService
from app.websocket import manager

router = APIRouter(prefix="/payments", tags=["payments"])


class CreateOrderRequest(BaseModel):
    amount: int

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: int) -> int:
        if value < 10:
            raise ValueError("Minimum amount is Rs 10")
        return value


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    user_name: Optional[str] = None
    anonymous: Optional[str] = None

    @field_validator("razorpay_order_id", "razorpay_payment_id", "razorpay_signature")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field is required")
        return value

    @field_validator("user_name")
    @classmethod
    def validate_user_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        return value[:30] if value else None


@router.post("/create-order")
@limiter.limit("20/minute")
def create_order(
    request: Request,
    body: CreateOrderRequest,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_optional_user_id),
):
    try:
        service = PaymentService(db)
        return service.create_order(user_id=user_id, amount=body.amount)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-payment")
@limiter.limit("20/minute")
async def verify_payment(
    request: Request,
    body: VerifyPaymentRequest,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_optional_user_id),
):
    try:
        service = PaymentService(db)
        payment, is_new_payment = service.verify_payment(body.model_dump(), user_id=user_id)

        if not is_new_payment:
            return {"status": "success", "duplicate": True}

        await manager.broadcast({
            "type": "NEW_ACTIVITY",
            "payload": {"text": f"{payment.user_name} supported Rs {payment.amount}"}
        })

        results = (
            db.query(Payment.user_name, func.sum(Payment.amount).label("total"))
            .filter(Payment.user_name != "Anonymous")
            .group_by(Payment.user_name)
            .order_by(func.sum(Payment.amount).desc())
            .limit(10)
            .all()
        )

        anon_total = (
            db.query(func.sum(Payment.amount))
            .filter(Payment.user_name == "Anonymous")
            .scalar()
        )

        leaderboard = [{"name": r.user_name, "amount": int(r.total)} for r in results]
        if anon_total:
            leaderboard.append({"name": "Someone", "amount": int(anon_total)})
            leaderboard.sort(key=lambda x: x["amount"], reverse=True)
            leaderboard = leaderboard[:10]

        await manager.broadcast({
            "type": "UPDATE_LEADERBOARD",
            "payload": leaderboard
        })

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
