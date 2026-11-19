from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.stats import StatsResponse
from app.services import trade as trade_service
from app.services.stats import build_stats, calc_realized

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_stats(
    date_from: date | None = Query(None, alias="from"),
    date_to: date | None = Query(None, alias="to"),
    market: Literal["KR", "US"] | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trades = trade_service.list_all_trades(db, user.id)
    realized = calc_realized(trades)
    return build_stats(trades, realized, date_from, date_to, market)