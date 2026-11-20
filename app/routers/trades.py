from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.trade import (
    BulkRequest, BulkResponse, TradeCreate, TradeListResponse, TradeResponse, NoteInput,
)
from app.services import trade as trade_service
from fastapi import File, UploadFile
from app.core.exceptions import AIUnavailableError, InvalidImageError
from app.schemas.capture import CaptureResponse
from app.services import capture as capture_service
from app.services.ai import AIError

router = APIRouter(prefix="/trades", tags=["trades"])

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024

@router.post("/capture", response_model=CaptureResponse)
def capture_trades(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise InvalidImageError()

    image = file.file.read()
    if len(image) > MAX_IMAGE_BYTES:
        raise InvalidImageError()

    try:
        candidates = capture_service.recognize(db, image, file.content_type)
    except AIError as e:
        raise AIUnavailableError() from e

    return CaptureResponse(candidates=candidates)


# response_model : 답변 스키마, status_code : 반환 값
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


# 거래 목록 가져오기
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

# router 주소를 /:id로 받아서 id를 바로 인자값으로 받음
@router.get("/{trade_id}", response_model=TradeResponse)
def get_trade(
    trade_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return trade_service.get_trade(db, user.id, trade_id)


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trade(
    trade_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trade_service.delete_trade(db, user.id, trade_id)

@router.put("/{trade_id}/note", response_model=TradeResponse)
def upsert_note(
    body: NoteInput,
    trade_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return trade_service.upsert_note(db, body, user.id, trade_id)

@router.delete("/{trade_id}/note", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
        trade_id: int,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    trade_service.delete_note(db, user.id, trade_id)
