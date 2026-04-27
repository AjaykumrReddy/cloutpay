from datetime import datetime, timezone
from typing import Optional
from calendar import monthrange

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user_id
from app.models.payment import Payment, PaymentOrder
from app.models.users import User
from app.models.hall_of_fame import HallOfFame

router = APIRouter(tags=["badges"])


# ── Badge definitions ─────────────────────────────────────────────────────────

BADGES = [
    {
        "id": "first_blood",
        "emoji": "🔥",
        "label": "First Blood",
        "desc": "Made your first contribution",
    },
    {
        "id": "1k_club",
        "emoji": "💎",
        "label": "Rs 1K Club",
        "desc": "Contributed Rs 1,000 or more in total",
    },
    {
        "id": "10k_club",
        "emoji": "👑",
        "label": "Rs 10K Club",
        "desc": "Contributed Rs 10,000 or more in total",
    },
    {
        "id": "top_dog",
        "emoji": "🥇",
        "label": "Top Dog",
        "desc": "Currently ranked #1 on the leaderboard",
    },
    {
        "id": "consistent",
        "emoji": "🎯",
        "label": "Consistent",
        "desc": "Contributed in 3 or more different months",
    },
    {
        "id": "high_roller",
        "emoji": "⚡",
        "label": "High Roller",
        "desc": "Made a single payment of Rs 500 or more",
    },
]


def _compute_badges(
    payments: list,
    total: int,
    current_rank: Optional[int],
    biggest_payment: int,
) -> list[dict]:
    earned = set()

    if payments:
        earned.add("first_blood")

    if total >= 1000:
        earned.add("1k_club")

    if total >= 10000:
        earned.add("10k_club")

    if current_rank == 1:
        earned.add("top_dog")

    months = {p.created_at.strftime("%Y-%m") for p in payments}
    if len(months) >= 3:
        earned.add("consistent")

    if biggest_payment >= 500:
        earned.add("high_roller")

    return [
        {**b, "earned": b["id"] in earned}
        for b in BADGES
    ]


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/badges/me")
def get_my_badges(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    order_ids = [
        r.id for r in db.query(PaymentOrder.id).filter_by(user_id=user_id, status="paid").all()
    ]

    payments = (
        db.query(Payment)
        .filter(Payment.order_id.in_(order_ids))
        .all()
    )

    total = sum(p.amount for p in payments)
    biggest = max((p.amount for p in payments), default=0)

    # Get current rank
    current_rank = None
    if user.display_name and total > 0:
        totals = [
            row.user_name
            for row in db.query(Payment.user_name, func.sum(Payment.amount).label("t"))
            .filter(Payment.user_name != "Anonymous")
            .group_by(Payment.user_name)
            .order_by(func.sum(Payment.amount).desc())
            .all()
        ]
        current_rank = next(
            (i + 1 for i, name in enumerate(totals) if name == user.display_name), None
        )

    return _compute_badges(payments, int(total), current_rank, int(biggest))


@router.get("/hall-of-fame")
def get_hall_of_fame(db: Session = Depends(get_db)):
    entries = (
        db.query(HallOfFame, User.display_name)
        .join(User, User.id == HallOfFame.user_id)
        .order_by(HallOfFame.month.desc())
        .limit(12)
        .all()
    )
    return [
        {
            "display_name": display_name,
            "total_amount": e.total_amount,
            "month": e.month,
        }
        for e, display_name in entries
    ]


@router.post("/hall-of-fame/record")
def record_hall_of_fame(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    now = datetime.now(timezone.utc)
    if now.month == 1:
        year, month = now.year - 1, 12
    else:
        year, month = now.year, now.month - 1

    month_str = f"{year}-{month:02d}"
    month_start = datetime(year, month, 1, tzinfo=timezone.utc)
    month_end = datetime(year, month, monthrange(year, month)[1], 23, 59, 59, tzinfo=timezone.utc)

    existing = db.query(HallOfFame).filter_by(month=month_str).first()
    if existing:
        user = db.query(User).filter_by(id=existing.user_id).first()
        return {"message": f"Already recorded for {month_str}", "entry": {
            "display_name": user.display_name if user else "Unknown",
            "total_amount": existing.total_amount,
            "month": existing.month,
        }}

    result = (
        db.query(Payment.user_name, func.sum(Payment.amount).label("total"))
        .filter(
            Payment.user_name != "Anonymous",
            Payment.created_at >= month_start,
            Payment.created_at <= month_end,
        )
        .group_by(Payment.user_name)
        .order_by(func.sum(Payment.amount).desc())
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail=f"No payments found for {month_str}")

    # Find the user_id for the winning display_name
    winner = db.query(User).filter_by(display_name=result.user_name).first()
    if not winner:
        raise HTTPException(status_code=404, detail="Winner user not found")

    entry = HallOfFame(
        user_id=winner.id,
        total_amount=int(result.total),
        month=month_str,
    )
    db.add(entry)
    db.flush()

    return {
        "message": f"Recorded {result.user_name} as champion for {month_str}",
        "entry": {
            "display_name": winner.display_name,
            "total_amount": entry.total_amount,
            "month": entry.month,
        }
    }
