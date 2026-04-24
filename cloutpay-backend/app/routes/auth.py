from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from typing import Optional
import re

from app.db import get_db
from app.services import auth_service
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Request schemas ───────────────────────────────────────────────────────────

class SendOTPRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not re.fullmatch(r"[6-9]\d{9}", v):
            raise ValueError("Enter a valid 10-digit Indian mobile number")
        return v


class VerifyOTPRequest(BaseModel):
    phone: str
    code: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not re.fullmatch(r"\d{6}", v.strip()):
            raise ValueError("OTP must be 6 digits")
        return v.strip()


class UpdateProfileRequest(BaseModel):
    display_name: str

    @field_validator("display_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        if len(v) > 30:
            raise ValueError("Name must be under 30 characters")
        return v


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/send-otp")
async def send_otp(body: SendOTPRequest, db: Session = Depends(get_db)):
    try:
        await auth_service.send_otp(body.phone, db)
        return {"message": "OTP sent successfully"}
    except ValueError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-otp")
def verify_otp(body: VerifyOTPRequest, db: Session = Depends(get_db)):
    try:
        result = auth_service.verify_otp(body.phone, body.code, db)
        return result  # { token, is_new_user, display_name }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update-profile")
def update_profile(
    body: UpdateProfileRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        display_name = auth_service.update_profile(user_id, body.display_name, db)
        return {"display_name": display_name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
