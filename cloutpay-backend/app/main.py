from fastapi import FastAPI, WebSocket
from app.models import users, payment as payment_models  # noqa: F401 - required for FK resolution
from app.models import otp as otp_model  # noqa: F401 - required for table creation
from app.routes import payment, leaderboard, auth
from app.websocket import manager

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(payment.router)
app.include_router(leaderboard.router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        print("❌ WebSocket disconnected:", e)
        manager.disconnect(websocket)