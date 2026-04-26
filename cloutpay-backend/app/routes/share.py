import io
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.payment import Payment, PaymentOrder
from app.models.users import User

router = APIRouter(prefix="/share", tags=["share"])

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def _get_user_stats(share_token: str, db: Session) -> Optional[dict]:
    user = db.query(User).filter_by(share_token=share_token).first()
    if not user or not user.display_name:
        return None

    order_ids = [
        r.id for r in db.query(PaymentOrder.id).filter_by(user_id=user.id, status="paid").all()
    ]

    total = (
        db.query(func.sum(Payment.amount))
        .filter(Payment.order_id.in_(order_ids))
        .scalar()
    ) or 0

    totals = [
        row.user_name
        for row in db.query(Payment.user_name, func.sum(Payment.amount).label("t"))
        .filter(Payment.user_name != "Anonymous")
        .group_by(Payment.user_name)
        .order_by(func.sum(Payment.amount).desc())
        .all()
    ]

    rank = next((i + 1 for i, name in enumerate(totals) if name == user.display_name), None)

    return {"display_name": user.display_name, "total": int(total), "rank": rank}


@router.get("/{share_token}/stats")
def share_stats(share_token: str, db: Session = Depends(get_db)):
    stats = _get_user_stats(share_token, db)
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(content=stats, headers={"Cache-Control": "no-store"})


@router.get("/{share_token}/card.png")
def share_card_image(share_token: str, db: Session = Depends(get_db)):
    stats = _get_user_stats(share_token, db)
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")

    W, H = 1200, 630
    img = Image.new("RGB", (W, H), color="#080808")
    draw = ImageDraw.Draw(img)

    for i in range(H):
        alpha = int(30 * (1 - i / H))
        draw.line([(0, i), (W, i)], fill=(255, 77, 77, alpha))

    for cx, cy, r, color in [
        (200, 150, 280, (255, 77, 77, 40)),
        (1000, 500, 220, (255, 204, 0, 30)),
    ]:
        for radius in range(r, 0, -4):
            opacity = int(color[3] * (radius / r))
            draw.ellipse(
                [cx - radius, cy - radius, cx + radius, cy + radius],
                fill=(color[0], color[1], color[2], opacity),
            )

    try:
        font_large = ImageFont.truetype("arial.ttf", 120)
        font_medium = ImageFont.truetype("arial.ttf", 56)
        font_small = ImageFont.truetype("arial.ttf", 38)
        font_brand = ImageFont.truetype("arial.ttf", 32)
    except Exception:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
        font_brand = font_large

    draw.text((W // 2, 60), "CLOUTPAY", font=font_brand, fill="#ff9a9a", anchor="mm")
    rank_str = f"#{stats['rank']}" if stats["rank"] else "🔥"
    draw.text((W // 2, 240), rank_str, font=font_large, fill="#ffffff", anchor="mm")
    draw.text((W // 2, 370), stats["display_name"], font=font_medium, fill="#f0f0f0", anchor="mm")
    draw.text((W // 2, 460), f"Rs {stats['total']:,} contributed", font=font_small, fill="#ffdf71", anchor="mm")
    draw.text((W // 2, 560), "cloutpay.in · Turn Money Into Status", font=font_brand, fill="#555555", anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png", headers={"Cache-Control": "no-store"})


@router.get("/{share_token}", response_class=HTMLResponse)
def share_page(share_token: str, db: Session = Depends(get_db)):
    stats = _get_user_stats(share_token, db)
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")

    rank_text = f"Rank #{stats['rank']} on CloutPay" if stats["rank"] else "On the CloutPay board"
    total_text = f"Rs {stats['total']:,} contributed"
    card_url = f"{FRONTEND_URL.rstrip('/')}/api/share/{share_token}/card.png"
    page_url = f"{FRONTEND_URL.rstrip('/')}"

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{stats['display_name']} · CloutPay</title>
  <meta property="og:title" content="{stats['display_name']} is {rank_text}" />
  <meta property="og:description" content="{total_text}. Can you beat them?" />
  <meta property="og:image" content="{card_url}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:url" content="{page_url}" />
  <meta property="og:type" content="website" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{stats['display_name']} is {rank_text}" />
  <meta name="twitter:description" content="{total_text}. Can you beat them?" />
  <meta name="twitter:image" content="{card_url}" />
  <meta http-equiv="refresh" content="0;url={page_url}" />
</head>
<body>
  <p>Redirecting to CloutPay...</p>
</body>
</html>"""
    return HTMLResponse(content=html)
