import os
import random
import httpx
from datetime import datetime, timedelta

from jose import jwt
from sqlalchemy.orm import Session

from app.models.otp import OTP
from app.models.users import User

JWT_SECRET = os.getenv("JWT_SECRET", "changeme")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 30

OTP_EXPIRY_MINUTES = 5
OTP_MAX_ATTEMPTS = 5

ENV = os.getenv("ENV", "dev")


def _generate_code() -> str:
    return str(random.randint(100000, 999999))


async def send_otp(phone: str, db: Session) -> None:
    # Rate limit: max OTP_MAX_ATTEMPTS in last 10 minutes
    window = datetime.utcnow() - timedelta(minutes=10)
    recent = (
        db.query(OTP)
        .filter(OTP.phone_number == phone, OTP.created_at >= window)
        .count()
    )
    if recent >= OTP_MAX_ATTEMPTS:
        raise ValueError("Too many OTP requests. Please wait 10 minutes.")

    code = _generate_code()
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    otp = OTP(phone_number=phone, code=code, expires_at=expires_at)
    db.add(otp)
    db.flush()
    if ENV == "dev":
        print(f"[DEV OTP] {phone}: {code}")
        return

    await _send_via_fast2sms(phone, code)


async def _send_via_fast2sms(phone: str, code: str) -> None:
    api_key = os.getenv("FAST2SMS_API_KEY")
    if not api_key:
        raise RuntimeError("FAST2SMS_API_KEY not set")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.fast2sms.com/dev/bulkV2",
            headers={"authorization": api_key},
            json={
                "route": "q",
                "variables_values": code,
                "numbers": phone,
            },
        )
        data = response.json()
        print(f"Fast2SMS response: {data}")
        if data.get("status_code") != 200:
            raise RuntimeError(
                f"Fast2SMS failed: {data.get('message')} (code: {data.get('status_code')})"
            )


def verify_otp(phone: str, code: str, db: Session) -> dict:
    otp = (
        db.query(OTP)
        .filter(
            OTP.phone_number == phone,
            OTP.code == code,
            OTP.is_used == False,
            OTP.expires_at >= datetime.utcnow(),
        )
        .order_by(OTP.created_at.desc())
        .first()
    )

    if not otp:
        raise ValueError("Invalid or expired OTP")

    otp.is_used = True

    # Upsert user
    user = db.query(User).filter_by(phone_number=phone).first()
    is_new_user = user is None

    if is_new_user:
        user = User(phone_number=phone, is_verified=True, last_login=datetime.utcnow())
        db.add(user)
    else:
        user.is_verified = True
        user.last_login = datetime.utcnow()

    db.flush()

    return {
        "token": _create_token(user.id, phone),
        "is_new_user": is_new_user,
        "display_name": user.display_name,
    }


def update_profile(user_id: int, display_name: str, db: Session) -> str:
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise ValueError("User not found")
    user.display_name = display_name.strip()
    db.flush()
    return user.display_name


def _create_token(user_id: int, phone: str) -> str:
    payload = {
        "sub": str(user_id),
        "phone": phone,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
