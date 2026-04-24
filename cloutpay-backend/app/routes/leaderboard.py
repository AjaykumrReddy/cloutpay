from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user_id
from app.models.payment import Payment, PaymentOrder
from app.models.users import User

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
                "payment_reference": p.razorpay_payment_id,
                "created_at": p.created_at.isoformat(),
            }
            for p in payments
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/leaderboard/me")
def get_my_summary(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        order_ids = [
            row.id
            for row in db.query(PaymentOrder.id)
            .filter_by(user_id=user_id, status="paid")
            .all()
        ]

        payments = (
            db.query(Payment)
            .filter(Payment.order_id.in_(order_ids))
            .order_by(Payment.created_at.desc())
            .all()
        )

        total_contributed = int(sum(payment.amount for payment in payments))
        payments_count = len(payments)
        last_payment_at = payments[0].created_at.isoformat() if payments else None

        current_rank = None
        amount_to_next_rank = None
        next_rank_name = None

        if user.display_name and total_contributed > 0:
            totals = [
                {"name": row.user_name, "amount": int(row.total)}
                for row in db.query(Payment.user_name, func.sum(Payment.amount).label("total"))
                .filter(Payment.user_name != "Anonymous")
                .group_by(Payment.user_name)
                .order_by(func.sum(Payment.amount).desc(), Payment.user_name.asc())
                .all()
            ]

            current_rank = next(
                (index + 1 for index, row in enumerate(totals) if row["name"] == user.display_name),
                None,
            )

            if current_rank and current_rank > 1:
                higher = totals[current_rank - 2]
                next_rank_name = higher["name"]
                amount_to_next_rank = max(higher["amount"] - total_contributed + 1, 0)

        return {
            "display_name": user.display_name,
            "total_contributed": total_contributed,
            "payments_count": payments_count,
            "current_rank": current_rank,
            "amount_to_next_rank": amount_to_next_rank,
            "next_rank_name": next_rank_name,
            "last_payment_at": last_payment_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
