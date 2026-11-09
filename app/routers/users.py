from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

# TODO: GET /me (새로고침 때 로그인 상태 확인에도 사용)
