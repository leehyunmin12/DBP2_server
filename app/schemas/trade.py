from datetime import date, time, timedelta
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Market = Literal["KR", "US"]
Side = Literal["BUY", "SELL"]
Emotion = Literal["CONFIDENT", "ANXIOUS", "IMPULSIVE", "GREEDY", "FEARFUL", "NEUTRAL"]


def _check_not_future(d: date) -> date:
    # 서버 시간대가 한국보다 느릴 수 있어서 하루 여유를 둔다.
    if d > date.today() + timedelta(days=1):
        raise ValueError("오늘 이후 날짜의 거래는 입력할 수 없습니다.")
    return d


# ---------- 요청 ----------
class NoteInput(BaseModel):
    reason: str = Field(min_length=1, max_length=500)
    emotion: Emotion | None = None

class TradeCreate(BaseModel):
    market: Market
    symbol: str = Field(min_length=1, max_length=20)
    side: Side
    # 값이 0보다 커야함, 최대 크기 설정(Numeric(18, 4)와 동일
    qty: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    price: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    traded_on: date
    traded_time: time | None = None # 생략 가능
    note: NoteInput | None = None

    @field_validator("traded_on")
    @classmethod
    def check_traded_on(cls, v: date) -> date:
        return _check_not_future(v)


class BulkTradeItem(BaseModel):
    market: Market
    symbol: str = Field(min_length=1, max_length=20)
    qty: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    buy_price: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    sell_price: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    buy_date: date
    sell_date: date
    note: NoteInput | None = None

    @field_validator("buy_date", "sell_date")
    @classmethod
    def check_not_future(cls, v: date) -> date:
        return _check_not_future(v)

    # 각 필드의 타입 검증이 모두 끝난 후, 여러 필드를 비교하는 검증
    @model_validator(mode="after")
    def check_dates(self):
        if self.sell_date < self.buy_date:
            raise ValueError("매도일은 매수일 이후여야 합니다.")
        return self


class BulkRequest(BaseModel):
    items: list[BulkTradeItem] = Field(min_length=1, max_length=100)


# ---------- 응답 ----------
class NoteResponse(BaseModel):
    # DB 객체의 속성에서 값을 읽어와야 하기 때문
    model_config = ConfigDict(from_attributes=True)

    reason: str
    emotion: str | None


class TradeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    market: str
    symbol: str
    name: str
    side: str
    qty: float
    price: float
    traded_on: date
    traded_time: time | None
    source: str
    note: NoteResponse | None
    pnl: float | None = None
    rate: float | None = None
    unmatched_qty: float = 0

class BulkResponse(BaseModel):
    saved: int

class TradeListResponse(BaseModel):
    total: int
    items: list[TradeResponse]

class NoteInput(BaseModel):
    reason: str = Field(min_length=1, max_length=500),
    emotion: Emotion | None = None