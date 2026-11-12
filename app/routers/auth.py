
from fastapi import APIRouter, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status

from app.core.database import get_db
from app.schemas.user import UserResponse, SignupRequest, LoginRequest
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", responses_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: Session = Depends(get_db())):
    return auth_service.signup(db, body.email, body.password)

@router.post("/login", response_model=UserResponse)
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db())):
    user = auth_service.login(db, body.email, body.password)
    request.session.clear()
    request.session["user_id"] = user.id
    return user

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request):
    request.session.clear()