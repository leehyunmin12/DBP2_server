from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NoSellInPeriodError, ReportNotFoundError, AIUnavailableError
from app.models.report import Report
from app.schemas.report import ReportCreate
from app.services import trade as trade_service
from app.services.ai import AIError, generate_summary
from app.services.report_prompt import build_prompt, pick_highlights
from app.services.stats import build_stats, calc_realized, select_sells


def _serialize_highlights(highlights: list[dict]) -> list[dict]:
    # TODO date -> 문자열(isoformat), pnl/rate(Decimal) -> float 로 바꿔서 돌려주기
    #      (JSON에 저장하려면 필요)

    result = []

    for highlight in highlights:
        result.append({
            **highlight,
            "date": highlight["date"].isoformat(),
            "pnl": float(highlight["pnl"]),
            "rate": float(highlight["rate"]),
        })

    return result


def _make_summary(market, date_from, date_to, stats: dict) -> str:
    # TODO build_prompt -> generate_summary 호출
    # AIError가 나면 None을 돌려준다 (리포트는 그대로 저장되게)
    system, user = build_prompt(market, date_from, date_to, stats, stats["highlights"])
    return generate_summary(system, user)


def _build_report_stats(trades, realized, market, date_from, date_to) -> dict:
    # 리포트 통계는 저장하지 않고, 보여줄 때마다 거래에서 계산한다 (3NF: 파생 데이터 중복 저장 제거)
    stats = build_stats(trades, realized, date_from, date_to, market)
    sells = select_sells(trades, realized, date_from, date_to, market)
    stats["highlights"] = _serialize_highlights(pick_highlights(sells))
    return stats


def _with_stats(db: Session, user_id: int, reports: list[Report]) -> list[Report]:
    # 거래는 한 번만 읽고, 리포트마다 통계를 계산해 report.stats 에 붙인다
    trades = trade_service.list_all_trades(db, user_id)
    realized = calc_realized(trades)
    for report in reports:
        report.stats = _build_report_stats(
            trades, realized, report.market, report.period_start, report.period_end
        )
    return reports


def create_report(db: Session, user_id: int, data: ReportCreate) -> Report:
    # TODO 1. 내 거래 전부 가져와서 calc_realized
    trades = trade_service.list_all_trades(db, user_id)
    realized = calc_realized(trades)

    # TODO 2. select_sells로 대상 SELL 고르기. 하나도 없으면 NoSellInPeriodError
    sells = select_sells(trades, realized, data.date_from, data.date_to, data.market)
    if not sells:
        raise NoSellInPeriodError()

    # TODO 3. 통계 + 대표 거래 계산 (DB에는 저장하지 않고 AI 요약 입력으로만 쓴다)
    stats = _build_report_stats(trades, realized, data.market, data.date_from, data.date_to)

    # TODO 4. _make_summary로 요약 만들기 (실패하면 None)
    try:
        summary = _make_summary(data.market, data.date_from, data.date_to, stats)
    except AIError:
        summary = None

    # TODO 5. Report 만들어서 add, commit, refresh 후 반환
    report = Report(
        user_id = user_id,
        market = data.market,
        period_start = data.date_from,
        period_end = data.date_to,
        summary = summary,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    report.stats = stats
    return report


def _get_my_report(db: Session, user_id: int, report_id: int) -> Report:
    report = db.scalar(
        select(Report).where(Report.id == report_id, Report.user_id == user_id)
    )
    if report is None:
        raise ReportNotFoundError()
    return report

def get_report(db: Session, user_id: int, report_id: int) -> Report:
    report = _get_my_report(db, user_id, report_id)
    _with_stats(db, user_id, [report])
    return report


def list_reports(db: Session, user_id: int) -> list[Report]:
    reports = list(db.scalars(
        select(Report)
        .where(Report.user_id == user_id)
        .order_by(Report.created_at.desc(), Report.id.desc())
    ).all())
    return _with_stats(db, user_id, reports)


def delete_report(db: Session, user_id: int, report_id: int) -> None:
    report = get_report(db, user_id, report_id)
    db.delete(report)
    db.commit()

def retry_summary(db: Session, user_id: int, report_id: int) -> Report:
    report = get_report(db, user_id, report_id)

    try:
        summary = _make_summary(
            report.market,
            report.period_start,
            report.period_end,
            report.stats,
        )
    except AIError as e:
        raise AIUnavailableError() from e

    report.summary = summary
    db.commit()
    db.refresh(report)
    return report