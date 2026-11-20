from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stock import Stock
from app.schemas.capture import CaptureCandidate, RawCapture, RawRow
from app.services.ai import generate_from_image

SYSTEM_INSTRUCTION = """..."""   # try_capture.py의 규칙 글을 그대로 옮기기


def _parse_md(text: str | None, year: int) -> date | None:
    """'6.19' -> date(year, 6, 19). 값이 없거나 이상하면 None"""
    ...


def _fill_dates(rows: list[RawRow]) -> list[str | None]:
    """빈 날짜를 '아래 줄의 날짜'로 채운 날짜 문자열 목록을 돌려준다"""
    ...


def _find_stock(db: Session, name: str) -> Stock | None:
    ...


def recognize(db: Session, image: bytes, mime_type: str) -> list[CaptureCandidate]:
    ...