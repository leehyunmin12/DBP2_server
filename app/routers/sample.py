from fastapi import APIRouter

router = APIRouter(prefix="/sample", tags=["sample"])

# TODO: POST /load (샘플 데이터 넣기), DELETE (샘플 삭제)
