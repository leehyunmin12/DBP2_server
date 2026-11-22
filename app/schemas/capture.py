from datetime import date
from typing import Literal
from pydantic import BaseModel
from decimal import Decimal
from pydantic import Field
from app.schemas.trade import TradeCreate

class CaptureCandidate(BaseModel):
    name: str                          # AI가 읽은 종목명
    side: Literal["BUY", "SELL"]
    qty: Decimal
    price: Decimal
    traded_on: date | None = None
    # 서버가 stocks에서 찾아서 채움 (못 찾으면 None)
    symbol: str | None = None
    market: Literal["KR", "US"] | None = None


class CaptureResponse(BaseModel):
    candidates: list[CaptureCandidate]

class RawRow(BaseModel):
    side: Literal["BUY", "SELL"]
    qty: float
    price: float
    date_text: str | None      # 화면에 보이는 그대로 "6.19", 없으면 None


class RawCapture(BaseModel):
    stock_name: str
    rows: list[RawRow]

class CaptureConfirm(BaseModel):
    items: list[TradeCreate] = Field(min_length=1, max_length=100)