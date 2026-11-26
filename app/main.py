from fastapi import Request

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AppError
from app.routers import auth, reports, stocks, trades, users, stats
app = FastAPI(title="매매 일지 + AI 복기 API", version="0.1.0")

# 세션 쿠키 (서명된 쿠키 세션). CORS가 가장 바깥에 오도록 나중에 추가한다.
# 세션 쿠키 관련 설정 (다른 사이트 접속 제한, 유효기간 등)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="lax",
    https_only=settings.session_https_only,
    max_age=60 * 60 * 24 * 7,
)

# CORS 설정  (다른 웹사이트에서 보내는 요청을 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 각 파일의 라우터를 앱에 연결시킴 (prefix 설정으로 주소 앞 고정)
for module in (auth, users, stocks, trades, reports, stats):
    app.include_router(module.router)

# health API, 서버가 살아있는 지 확인
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

# DB 연결 확인
@app.get("/health/db", tags=["health"])
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected"}

# service에서 Error를 올리면 router를 지나 여기 app_error_handler에서 잡음
# Error 났을 때 반환 내용 정의
@app.exception_handler(AppError)
def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error" : {"code": exc.code, "message": exc.message}},
    )