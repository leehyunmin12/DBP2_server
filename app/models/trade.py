from datetime import date
from decimal import Decimal

from sqlalchemy import (
    BigInteger, Date, ForeignKey, ForeignKeyConstraint,
    Numeric, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.stock import Stock
from app.models.base import Base
from app.models.enums import EmotionType, MarketType, TradeSide, TradeSource

class Trade(Base):
    __tablename__ = "trades"
    # 복합 FK
    __table_args__ = (
        ForeignKeyConstraint(["market", "symbol"], ["stocks.market", "stocks.symbol"]),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    market: Mapped[str] = mapped_column(MarketType)
    symbol: Mapped[str] = mapped_column(String(20))
    side: Mapped[str] = mapped_column(TradeSide)
    qty: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    price: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    traded_on: Mapped[date] = mapped_column(Date)
    source: Mapped[str] = mapped_column(TradeSource)

    # relationship()은 테이블을 합쳐 놓는 것이 아니라 나중에 joinedload를 할 때 바로 가능하도록 하는 지도이다.
    # 그냥 Trade는 trades만 select하고 Trade.note를 호출해야 trades와 trad_notes를 select하는 것이다.

    # 종목 정보를 Stock 객체로 가져온다
    # trade.stock.name, trade.stock.symbol로 사용 가능
    stock: Mapped["Stock"] = relationship() # Trade.stock 형식으로 사용 가능
    note: Mapped["TradeNote | None"] = relationship(
        back_populates="trade", uselist=False, cascade="all, delete-orphan" # trade 속성과 연결, 매퍼 설정(configure mappers)
    )  # Trade.note로 사용 가능
    
    @property
    def name(self) -> str:
        return self.stock.name


class TradeNote(Base):
    __tablename__ = "trade_notes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    trade_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("trades.id", ondelete="CASCADE"), unique=True
    )
    reason: Mapped[str] = mapped_column(Text)
    emotion: Mapped[str | None] = mapped_column(EmotionType)

    trade: Mapped["Trade"] = relationship(back_populates="note") # note 속성과 연결