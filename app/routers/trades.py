from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.trade import TradeResponse, TradeCreate, BulkRequest, BulkResponse
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
