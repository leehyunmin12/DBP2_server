from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

# TODO: POST /signup, POST /login, POST /logout (세션 쿠키 방식)
