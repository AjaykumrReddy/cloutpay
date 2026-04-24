from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user_id
from app.models.payment import Payment, PaymentOrder

router = APIRouter()


@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    named = (
        db.query(Payment.user_name, func.sum(Payment.amount).label("total"))
        .filter(Payment.user_name != "Anonymous")
        .group_by(Payment.user_name)
        .order_by(func.sum(Payment.amount).desc())
        .limit(10)
        .all()
    )

    leaderboard = [{"name": r.user_name, "amount": int(r.total)} for r in named]

    anon_total = (
        db.query(func.sum(Payment.amount))
        .filter(Payment.user_name == "Anonymous")
        .scalar()
    )
    if anon_total:
        leaderboard.append({"name": "Someone", "amount": int(anon_total)})
        leaderboard.sort(key=lambda x: x["amount"], reverse=True)
        leaderboard = leaderboard[:10]

    return leaderboard


@router.get("/payments/history")
def get_history(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        order_ids = [
            o.id for o in
            db.query(PaymentOrder.id)
            .filter_by(user_id=user_id, status="paid")
            .all()
        ]

        payments = (
            db.query(Payment)
            .filter(Payment.order_id.in_(order_ids))
            .order_by(Payment.created_at.desc())
            .limit(50)
            .all()
        )

        return [
            {
                "id": p.id,
                "amount": p.amount,
                "user_name": p.user_name,
                "created_at": p.created_at.isoformat(),
            }
            for p in payments
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
