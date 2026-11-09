from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stock import Stock

# Stock 객체의 리스트를 반환해줌
def list_stocks(db: Session, query: str | None = None, market: str | None = None) -> list[Stock]:

    stmt = select(Stock)
    if query:
        # 만약 query가 있다면 해당 쿼리가 종목명에 포함되거나 symbol에 포함되는 행 조회 (대소문자 무시)
        stmt = stmt.where(Stock.name.ilike(f"%{query}%") | Stock.symbol.ilike(f"%{query}%"))
    if market:
        # 만약 시장이 존재하면 해당 시장을 조회 (대소문자 무시)
        stmt = stmt.where(Stock.market == market)
    # stocks 모델을 select(조회) 쿼리를 작성 후, DB에서 실행한 결과 전체를 가져옴, 결과를 list로 변환
    return list(db.scalars(stmt).all())