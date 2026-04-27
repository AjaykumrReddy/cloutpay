import os

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.limiter import limiter
from app.models import otp as otp_model  # noqa: F401
from app.models import payment as payment_models  # noqa: F401
from app.models import users  # noqa: F401
from app.models import hall_of_fame  # noqa: F401
from app.routes import auth, leaderboard, payment, share, badges
from app.websocket import manager

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=os.getenv(
        "CORS_ORIGIN_REGEX",
        r"https://.*\.ngrok-free\.app|http://localhost(:\d+)?"
    ),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(payment.router)
app.include_router(leaderboard.router)
app.include_router(share.router)
app.include_router(badges.router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)
