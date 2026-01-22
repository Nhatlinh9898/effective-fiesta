"""
FastAPI app entrypoint.
"""
import time
from typing import Dict

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .routes.health import router as health_router
from .routes.models import router as models_router
from .routes.generate import router as generate_router
from .routes.chat import router as chat_router
from .config import settings


app = FastAPI(title="Lightweight Local AI Server", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_rate_state: Dict[str, Dict[str, float]] = {}


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    bucket = _rate_state.get(ip)
    if not bucket or now > bucket["reset"]:
        bucket = {"count": 0.0, "reset": now + 60.0}
        _rate_state[ip] = bucket
    if bucket["count"] >= settings.rate_limit_per_minute:
        return Response(status_code=429, content="Rate limit exceeded")
    bucket["count"] += 1.0
    return await call_next(request)

app.include_router(health_router)
app.include_router(models_router)
app.include_router(generate_router)
app.include_router(chat_router)
