from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models.payment import Payment,PaymentOrder

router = APIRouter()


@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    results = (
        db.query(
            Payment.user_name,
            func.sum(Payment.amount).label("total")
        )
        .group_by(Payment.user_name)
        .order_by(func.sum(Payment.amount).desc())
        .limit(10)
        .all()
    )

    return [
        {"name": r.user_name, "amount": int(r.total)}
        for r in results
    ]