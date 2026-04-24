from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.db import get_db
from app.models.payment import Payment
from app.services.payment_service import PaymentService
from app.dependencies import get_optional_user_id
from app.websocket import manager
from app.limiter import limiter

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/create-order")
@limiter.limit("20/minute")
def create_order(
    request: Request,
    data: dict,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_optional_user_id),
):
    try:
        service = PaymentService(db)
        result = service.create_order(user_id=user_id, amount=data["amount"])
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-payment")
@limiter.limit("20/minute")
async def verify_payment(
    request: Request,
    data: dict,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_optional_user_id),
):
    try:
        service = PaymentService(db)
        payment = service.verify_payment(data, user_id=user_id)

        await manager.broadcast({
            "type": "NEW_ACTIVITY",
            "payload": {"text": f"{payment.user_name} supported ₹{payment.amount} 🔥"}
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
            leaderboard.append({"name": "Someone 🕵️", "amount": int(anon_total)})
            leaderboard.sort(key=lambda x: x["amount"], reverse=True)
            leaderboard = leaderboard[:10]

        await manager.broadcast({
            "type": "UPDATE_LEADERBOARD",
            "payload": leaderboard
        })

        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
