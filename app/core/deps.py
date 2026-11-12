from fastapi import Request, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.models.user import User


def get_current_user(request: Request, db: Session = Depends(get_db)):
    # 쿠키에서 풀어낸 세션에서 user_id를 확인
    user_id = request.session.get("user_id")
    # user_id가 없음 -> 로그인 하지 않은 요청 처리
    if user_id is None:
        raise UnauthorizedError()

    # 쿠키는 있는데 DB 사용자가 없는 경우 -> 세션 비우고 에러
    # DB에 해당 유저의 쿼리를 하나 조회
    user = db.get(User, user_id)
    if user is None:
        request.session.clear()
        raise  UnauthorizedError()

    return user

