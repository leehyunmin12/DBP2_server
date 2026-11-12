# sqlalchemy는 ORM이다.
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

# Base를 상속받는 이유 -> sqlalchemy가 DB와 연결된 모델인 걸 알게 하기 위해서.
class Stock(Base):
    # stocks 테이블과 연결된다는 선언
    __tablename__ = "stocks"

    # 왼쪽은 파이썬 기준, 오른쪽은 DB 기준
    market: Mapped[str] = mapped_column(Enum("KR", "US", name="market_type", create_type=False), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))