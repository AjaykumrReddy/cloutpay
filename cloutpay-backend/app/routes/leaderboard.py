from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user_id
from app.models.payment import Payment, PaymentOrder
from app.models.users import User

router = APIRouter()


def _month_start() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _build_leaderboard(db: Session, since: Optional[datetime] = None) -> list[dict]:
    q = db.query(Payment.user_name, func.sum(Payment.amount).label("total"))
    if since:
        q = q.filter(Payment.created_at >= since)

    named = (
        q.filter(Payment.user_name != "Anonymous")
        .group_by(Payment.user_name)
        .order_by(func.sum(Payment.amount).desc())
        .limit(10)
        .all()
    )

    leaderboard = [{"name": r.user_name, "amount": int(r.total)} for r in named]

    anon_q = db.query(func.sum(Payment.amount)).filter(Payment.user_name == "Anonymous")
    if since:
        anon_q = anon_q.filter(Payment.created_at >= since)
    anon_total = anon_q.scalar()

    if anon_total:
        leaderboard.append({"name": "Someone", "amount": int(anon_total)})
        leaderboard.sort(key=lambda x: x["amount"], reverse=True)
        leaderboard = leaderboard[:10]

    return leaderboard


@router.get("/leaderboard")
def get_leaderboard(
    period: Optional[str] = Query(None, pattern="^month$"),
    db: Session = Depends(get_db),
):
    since = _month_start() if period == "month" else None
    return _build_leaderboard(db, since)


@router.get("/payments/history")
def get_history(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
):
    try:
        PAGE_SIZE = 2
        offset = (page - 1) * PAGE_SIZE

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
            .offset(offset)
            .limit(PAGE_SIZE + 1)
            .all()
        )

        has_more = len(payments) > PAGE_SIZE
        payments = payments[:PAGE_SIZE]

        return {
            "items": [
                {
                    "id": p.id,
                    "amount": p.amount,
                    "user_name": p.user_name,
                    "payment_reference": p.razorpay_payment_id,
                    "created_at": p.created_at.isoformat(),
                }
                for p in payments
            ],
            "has_more": has_more,
            "page": page,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/leaderboard/me")
def get_my_summary(
    period: Optional[str] = Query(None, pattern="^month$"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        since = _month_start() if period == "month" else None

        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        order_ids = [
            row.id
            for row in db.query(PaymentOrder.id)
            .filter_by(user_id=user_id, status="paid")
            .all()
        ]

        payments_q = db.query(Payment).filter(Payment.order_id.in_(order_ids))
        if since:
            payments_q = payments_q.filter(Payment.created_at >= since)
        payments = payments_q.order_by(Payment.created_at.desc()).all()

        total_contributed = int(sum(p.amount for p in payments))
        payments_count = len(payments)
        last_payment_at = payments[0].created_at.isoformat() if payments else None
        biggest_payment = int(max((p.amount for p in payments), default=0))
        average_payment = int(total_contributed / payments_count) if payments_count else 0

        current_rank = None
        amount_to_next_rank = None
        next_rank_name = None

        if user.display_name and total_contributed > 0:
            totals_q = db.query(Payment.user_name, func.sum(Payment.amount).label("total"))
            if since:
                totals_q = totals_q.filter(Payment.created_at >= since)
            totals = [
                {"name": row.user_name, "amount": int(row.total)}
                for row in totals_q
                .filter(Payment.user_name != "Anonymous")
                .group_by(Payment.user_name)
                .order_by(func.sum(Payment.amount).desc(), Payment.user_name.asc())
                .all()
            ]

            current_rank = next(
                (i + 1 for i, row in enumerate(totals) if row["name"] == user.display_name),
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
            "biggest_payment": biggest_payment,
            "average_payment": average_payment,
            "current_rank": current_rank,
            "amount_to_next_rank": amount_to_next_rank,
            "next_rank_name": next_rank_name,
            "last_payment_at": last_payment_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
