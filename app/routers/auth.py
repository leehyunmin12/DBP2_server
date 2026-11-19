from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.core.database import get_db
from app.schemas.user import UserResponse, SignupRequest, LoginRequest
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    return auth_service.signup(db, body.email, body.password)

# request는 들어온 요청의 모든 정보를 담은 객체(헤더, 쿠키, 주소, 세션 등)
@router.post("/login", response_model=UserResponse)
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = auth_service.login(db, body.email, body.password)
    # 이전 세션을 지우고 새롭게 user_id를 넣어줌
    request.session.clear()
    request.session["user_id"] = user.id
    return user

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request):
    request.session.clear()
    