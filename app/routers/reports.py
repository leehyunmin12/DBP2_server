from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.report import ReportCreate, ReportResponse
from app.services import report as report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    body: ReportCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return report_service.create_report(db, user.id, body)


@router.get("", response_model=list[ReportResponse])
def list_reports(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return report_service.list_reports(db, user.id)


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return report_service.get_report(db, user.id, report_id)


@router.post("/{report_id}/summary", response_model=ReportResponse)
def retry_summary(
    report_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return report_service.retry_summary(db, user.id, report_id)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report_service.delete_report(db, user.id, report_id)