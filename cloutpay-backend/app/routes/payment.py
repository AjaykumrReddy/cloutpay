from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_optional_user_id
from app.limiter import limiter
from app.models.payment import Payment
from app.models.users import User
from app.services.cashfree_service import verify_cashfree_webhook
from app.services.payment_service import PaymentService
from app.websocket import manager

router = APIRouter(prefix="/payments", tags=["payments"])


class CreateOrderRequest(BaseModel):
    amount: int

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Minimum amount is Rs 1")
        return value


class VerifyPaymentRequest(BaseModel):
    cf_order_id: str
    user_name: Optional[str] = None
    anonymous: Optional[bool] = False

    @field_validator("cf_order_id")
    @classmethod
    def validate_order_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("cf_order_id is required")
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
        # Get phone from user if logged in
        customer_phone = "9999999999"
        if user_id:
            user = db.query(User).filter_by(id=user_id).first()
            if user and user.phone_number:
                customer_phone = user.phone_number

        service = PaymentService(db)
        result = service.create_order(
            user_id=user_id,
            amount=body.amount,
            customer_phone=customer_phone,
        )
        db.commit()
        return result
    except Exception as e:
        db.rollback()
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
        payment, is_new_payment = service.verify_payment(
            cf_order_id=body.cf_order_id,
            user_id=user_id,
            user_name_override=body.user_name,
            anonymous=body.anonymous or False,
        )
        db.commit()

        if not is_new_payment:
            return {"status": "success", "duplicate": True}

        # Broadcast live activity
        await manager.broadcast({
            "type": "NEW_ACTIVITY",
            "payload": {"text": f"{payment.user_name} paid Rs {payment.amount}"}
        })

        # Rebuild leaderboard
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
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def cashfree_webhook(request: Request, db: Session = Depends(get_db)):
    """Cashfree webhook for server-side payment confirmation."""
    try:
        raw_body = await request.body()
        timestamp = request.headers.get("x-webhook-timestamp", "")
        signature = request.headers.get("x-webhook-signature", "")

        if timestamp and signature:
            if not verify_cashfree_webhook(raw_body, timestamp, signature):
                raise HTTPException(status_code=400, detail="Invalid webhook signature")

        import json
        data = json.loads(raw_body)
        event_type = data.get("type", "")

        if event_type == "PAYMENT_SUCCESS_WEBHOOK":
            order_data = data.get("data", {}).get("order", {})
            cf_order_id = order_data.get("order_id", "")
            if cf_order_id:
                service = PaymentService(db)
                payment, is_new = service.verify_payment(
                    cf_order_id=cf_order_id,
                    user_id=None,
                )
                db.commit()
                if is_new:
                    await manager.broadcast({
                        "type": "NEW_ACTIVITY",
                        "payload": {"text": f"{payment.user_name} paid Rs {payment.amount}"}
                    })

        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history")
@limiter.limit("30/minute")
def get_history(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_optional_user_id),
):
    if not user_id:
        raise HTTPException(status_code=401, detail="Login required")

    from app.models.payment import PaymentOrder
    page_size = 20
    offset = (page - 1) * page_size

    payments = (
        db.query(Payment)
        .join(PaymentOrder, Payment.order_id == PaymentOrder.id)
        .filter(PaymentOrder.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .offset(offset)
        .limit(page_size + 1)
        .all()
    )

    has_more = len(payments) > page_size
    items = payments[:page_size]

    return {
        "items": [
            {
                "id": p.id,
                "amount": p.amount,
                "user_name": p.user_name,
                "payment_reference": p.payment_reference or p.cf_payment_id,
                "created_at": p.created_at.isoformat(),
            }
            for p in items
        ],
        "has_more": has_more,
        "page": page,
    }
