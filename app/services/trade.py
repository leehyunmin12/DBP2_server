from sqlalchemy.orm import Session

from app.core.exceptions import StockNotFoundError
from app.models.stock import Stock
from app.models.trade import Trade, TradeNote
from app.schemas.trade import BulkTradeItem, TradeCreate

def _check_stock(db: Session, market: str, symbol: str) -> None:
    # 입력한 시장과 symbol이 Stock DB에 있는 지 조회
    if db.get(Stock, (market, symbol)) is None:
        raise StockNotFoundError()

def create_trade(db: Session, user_id: int, data: TradeCreate, source: str = "MANUAL") -> Trade:
    _check_stock(db, data.market, data.symbol)

    trade = Trade(
        user_id=user_id,
        market=data.market,
        symbol=data.symbol,
        side=data.side,
        qty=data.qty,
        price=data.price,
        traded_on=data.traded_on,
        traded_time=data.traded_time,
        source=source,
    )
    if data.note:
        trade.note = TradeNote(reason=data.note.reason, emotion=data.note.emotion)

    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade

def create_bulk(db: Session, user_id: int, items: list[BulkTradeItem], source: str = "MANUAL") -> int:
    # items 리스트를 돌면서 market과 symbol 컬럼 확인
    for market, symbol in {(i.market, i.symbol) for i in items}:
        _check_stock(db, market, symbol)

    # 하나의 입력을 두 개의 행으로 나눔
    for item in items:
        buy = Trade(
            user_id=user_id, market=item.market, symbol=item.symbol, side="BUY",
            qty=item.qty, price=item.buy_price, traded_on=item.buy_date, source=source,
        )
        sell = Trade(
            user_id=user_id, market=item.market, symbol=item.symbol, side="SELL",
            qty=item.qty, price=item.sell_price, traded_on=item.sell_date, source=source,
        )
        if item.note:
            sell.note = TradeNote(reason=item.note.reason, emotion=item.note.emotion)
        db.add_all([buy, sell])

    db.commit()
    return len(items)