from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import get_db
from app.routers import auth, reports, sample, stocks, trades, users

API_PREFIX = "/api/v1"

app = FastAPI(title="매매 일지 + AI 복기 API", version="0.1.0")

# 세션 쿠키 (서명된 쿠키 세션). CORS가 가장 바깥에 오도록 나중에 추가한다.
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="lax",
    https_only=settings.session_https_only,
    max_age=60 * 60 * 24 * 7,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (auth, users, stocks, trades, reports, sample):
    app.include_router(module.router, prefix=API_PREFIX)


@app.get(f"{API_PREFIX}/health", tags=["health"])
def health():
    return {"status": "ok"}


@app.get(f"{API_PREFIX}/health/db", tags=["health"])
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected"}
