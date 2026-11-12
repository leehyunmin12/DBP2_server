from sqlalchemy import Enum

# Enum 타입 정리

MarketType = Enum("KR", "US", name="market_type", create_type=False)
TradeSide = Enum("BUY", "SELL", name="trade_side", create_type=False)
TradeSource = Enum("MANUAL", "CAPTURE", "SAMPLE", name="trade_source", create_type=False)
EmotionType = Enum(
    "CONFIDENT", "ANXIOUS", "IMPULSIVE", "GREEDY", "FEARFUL", "NEUTRAL",
    name="emotion_type", create_type=False,
)