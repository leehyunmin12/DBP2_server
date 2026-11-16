from sqlalchemy.orm import Session

from app.core.exceptions import StockNotFoundError, TradeNotFoundError, NoteNotFoundError
from app.models.stock import Stock
from app.models.trade import Trade, TradeNote
from app.schemas.trade import BulkTradeItem, TradeCreate, NoteInput
from datetime import date
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

# 해당 종목을 DB에서 조회
def _check_stock(db: Session, market: str, symbol: str) -> None:
    # 입력한 시장과 symbol이 Stock DB에 있는 지 조회
    if db.get(Stock, (market, symbol)) is None:
        raise StockNotFoundError()

# 종목 1개 추가하기
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

# 여러 개의 종목 한번에 추가하기
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

# 거래 내역 리스트로 조회 api
# * 표시는 해당 표시 뒤부터는 모든 인자가 이름을 붙여서 넘겨야 한다는 뜻 (ex : ?market='KR')
def list_trades(
        db: Session,
        user_id: int,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        market: str | None = None,
        symbol: str | None = None,
        side: str | None = None,
        limit: int = 20,
        offset: int = 0,
) -> tuple[int, list[Trade]]:
    # stmt에 처음엔 본인인지를 확인하고 그 이후부터는 인자값이 있으면 해당 인자값을 조건으로 추가하는 방식
    stmt = select(Trade).where(Trade.user_id == user_id)

    if date_from:
        stmt = stmt.where(Trade.traded_on >= date_from)
    if date_to:
        stmt = stmt.where(Trade.traded_on <= date_to)
    if market:
        stmt = stmt.where(Trade.market == market)
    if symbol:
        stmt = stmt.where(Trade.symbol == symbol)
    if side:
        stmt = stmt.where(Trade.side == side)

    # 서브쿼리를 사용해서 count(*)를 센다
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    # offset : 건너뛸 개수
    rows = db.scalars(
        stmt.options(joinedload(Trade.stock), joinedload(Trade.note))
        .order_by(Trade.traded_on.desc(), Trade.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    return total, list(rows)

# id와 trade_id가 같고, 본인의 거래내역을 가져와라(종목과 메모도 함께)
def _get_my_trade(db: Session, user_id: int, trade_id: int) -> Trade:
    trade = db.scalar(
        select(Trade)
        .where(Trade.id == trade_id, Trade.user_id == user_id)
        .options(joinedload(Trade.stock), joinedload(Trade.note))
    )
    if trade is None:
        raise TradeNotFoundError()
    return trade

# 거래 내역 상세 조회 api
def get_trade(db: Session, user_id: int, trade_id: int) -> Trade:
    return _get_my_trade(db, user_id, trade_id)

# 거래 내역 삭제 api
def delete_trade(db: Session, user_id: int, trade_id: int) -> None:
    trade = _get_my_trade(db, user_id, trade_id)
    db.delete(trade)
    db.commit()

def upsert_note(db: Session, data: NoteInput, user_id: int, trade_id: int) -> Trade:
    trade = _get_my_trade(db, user_id, trade_id)

    if trade.note:
        trade.note.reason = data.reason
        trade.note.emotion = data.emotion
    else:
        trade.note = TradeNote(reason=data.reason, emotion=data.emotion)

    db.commit()
    db.refresh(trade)
    return trade

def delete_note(db: Session, user_id: int, trade_id: int) -> None:
    trade = _get_my_trade(db, user_id, trade_id)

    if trade.note is None:
        raise NoteNotFoundError()

    trade.note = None
    db.commit()
