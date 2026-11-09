from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing_extensions import Literal

from app.core.database import get_db
from app.schemas.stock import StockResponse
from app.services import stock as stock_service



router = APIRouter(prefix="/stocks", tags=["stocks"]) # 이 파일의 모든 주소에 /stocks가 붙음

# prefix인 /stocks 뒤에 아무것도 안붙음 /stocks GET 요청 자체, schemas의 stock.py 모양으로 response를 보냄
@router.get("", response_model=list[StockResponse])
# get_db 함수를 실행해서 나온 값을 db에 주입시킨다.
# 만약 query나 market을 뒤에 안붙이면 그냥 None으로 처리, 상관없음, market은 Enum값이라서 Literal로 처리
def list_stocks(query: str | None = None, market: Literal["KR", "US"] | None = None, db: Session = Depends(get_db)):
    return stock_service.list_stocks(db, query, market)
