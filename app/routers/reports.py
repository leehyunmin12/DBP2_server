from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["reports"])

# TODO: POST (기간으로 생성), GET, GET /{id}, POST /{id}/summary (AI 요약 재시도), DELETE
