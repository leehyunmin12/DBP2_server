from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# .env의 database_url로 DB 엔진 만들기
engine = create_engine(settings.database_url, pool_pre_ping=True)
# 세션은 DB와 주고받는 한 번의 작업 단위이다, 이 세션들은 위에 엔진을 활용하여 DB와 통신한다.
# SessionLocal()을 호출할 때마다 새로운 새션을 만든다.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal() # 세션은 하나 만들어서 db에 저장
    try:
        # yield는 return과 비슷하지만 값을 내준 뒤 함수를 멈추고 나중에 다시 실행한다.
        # 값을 주고, router가 끝나면 다시 돌아와서 밑에 finally 부분으로 감.
        yield db
    finally:
        db.close()
