from fastapi import Header, HTTPException
from typing import Optional
from app.services.auth_service import decode_token


def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    """Strict — raises 401 if no valid token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(authorization.split(" ", 1)[1])
        return int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_optional_user_id(authorization: Optional[str] = Header(None)) -> Optional[int]:
    """Lenient — returns None for guests, user_id for logged-in users."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        payload = decode_token(authorization.split(" ", 1)[1])
        return int(payload["sub"])
    except Exception:
        return None
