from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.users import User


def update_streak(db: Session, user_id: int) -> dict:
    """Call this after every successful payment for a logged-in user."""
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return {}

    today = date.today()
    last = user.last_payment_date  # date or None

    if last is None:
        # First ever payment
        user.current_streak = 1
    elif last == today:
        # Already paid today — no change to streak
        pass
    elif last == today - timedelta(days=1):
        # Paid yesterday — extend streak
        user.current_streak = (user.current_streak or 0) + 1
    else:
        # Missed one or more days — reset
        user.current_streak = 1

    user.last_payment_date = today
    user.longest_streak = max(user.longest_streak or 0, user.current_streak)

    return {
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak,
    }


def get_streak_label(streak: int) -> str:
    if streak >= 30:
        return "👑 30+ day streak"
    if streak >= 14:
        return "⚡ 14+ day streak"
    if streak >= 7:
        return "🔥 7 day streak"
    if streak >= 3:
        return "🎯 3 day streak"
    if streak >= 1:
        return f"🔥 {streak} day streak"
    return ""
