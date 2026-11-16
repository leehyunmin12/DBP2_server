from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.trade import (
    BulkRequest, BulkResponse, TradeCreate, TradeListResponse, TradeResponse,
)
from app.services import trade as trade_service

router = APIRouter(prefix="/trades", tags=["trades"])

@router.post("", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
def create_trade(
        body: TradeCreate,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    return trade_service.create_trade(db, user.id, body)

@router.post("/bulk", response_model=BulkResponse, status_code=status.HTTP_201_CREATED)
def create_bulk(
    body: BulkRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved = trade_service.create_bulk(db, user.id, body.items)
    return BulkResponse(saved=saved)


@router.get("", response_model=TradeListResponse)
def list_trades(
    date_from: date | None = Query(None, alias="from"),
    date_to: date | None = Query(None, alias="to"),
    market: Literal["KR", "US"] | None = None,
    symbol: str | None = None,
    side: Literal["BUY", "SELL"] | None = None,
    limit: int = Query(20, ge=1, le=100), # 기본값이 20, 1이상 100이하
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total, rows = trade_service.list_trades(
        db,
        user.id,
        date_from=date_from,
        date_to=date_to,
        market=market,
        symbol=symbol,
        side=side,
        limit=limit,
        offset=offset,
    )
    return {"total": total, "items": rows}
