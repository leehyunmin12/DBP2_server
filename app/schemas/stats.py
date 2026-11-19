from pydantic import BaseModel


class StatsSummary(BaseModel):
    total_pnl: float
    sell_count: int
    win_count: int
    loss_count: int
    win_rate: float      # 0.0 ~ 1.0
    avg_profit: float    # 이익 거래의 평균
    avg_loss: float      # 손실 거래의 평균 (음수)


class StockStat(BaseModel):
    market: str
    symbol: str
    name: str
    pnl: float
    sell_count: int


class EmotionStat(BaseModel):
    emotion: str         # 감정이 없으면 "NONE"
    sell_count: int
    pnl: float
    win_rate: float


class StatsResponse(BaseModel):
    summary: StatsSummary
    by_stock: list[StockStat]
    by_emotion: list[EmotionStat]
    has_unmatched: bool  # 보유보다 많이 판 거래가 있는지