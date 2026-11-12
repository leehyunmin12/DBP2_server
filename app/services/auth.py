from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import EmailExistsError, InvalidCredentialsError
from app.core.security import hash_password, verify_password
from app.models.user import User


def signup(db: Session, email: str, password: str) -> User:
    # 해당 이메일의 User가 있는지를 DB에서 검색함
    exists = db.scalar(select(User).where(User.email == email))
    if exists:
        # 이미 있는 이메일이면 exception 처리
        raise EmailExistsError()

    # 아니면 User entity에 값 넣고 해당 객체를 DB 쿼리문으로 생성 및 쿼리 호출
    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    # 쿼리문 호출 후 최종적으로 생긴 row를 가져옴 (id와 created_at 컬럼 추가)
    db.refresh(user)
    return user


def login(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email))

    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()
    return user