from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models.payment import Payment
from app.services.payment_service import PaymentService
from app.websocket import manager

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/create-order")
def create_order(data: dict, db: Session = Depends(get_db)):
    try:
        service = PaymentService(db)
        result = service.create_order(user_id=None, amount=data["amount"])
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-payment")
async def verify_payment(data: dict, db: Session = Depends(get_db)):
    try:
        service = PaymentService(db)
        payment = service.verify_payment(data)

        await manager.broadcast({
            "type": "NEW_ACTIVITY",
            "payload": {"text": f"{payment.user_name} supported ₹{payment.amount} 🔥"}
        })

        # Broadcast updated leaderboard
        results = (
            db.query(Payment.user_name, func.sum(Payment.amount).label("total"))
            .group_by(Payment.user_name)
            .order_by(func.sum(Payment.amount).desc())
            .limit(10)
            .all()
        )
        await manager.broadcast({
            "type": "UPDATE_LEADERBOARD",
            "payload": [{"name": r.user_name, "amount": int(r.total)} for r in results]
        })

        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))