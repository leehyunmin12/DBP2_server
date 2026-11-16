import csv
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

from app.core.database import SessionLocal
from app.models import Stock

# 현재 폴더의 절대경로 위에서 .csv 파일 찾기
CSV_PATH = Path(__file__).resolve().parent.parent / "db" / "seed" / "stocks.csv"


def main() -> None:
    # csv 파일을 열고 
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        rows = [
            {"market": r["market"].strip(), "symbol": r["symbol"].strip(), "name": r["name"].strip()}
            for r in csv.DictReader(f)
        ]

    stmt = insert(Stock).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["market", "symbol"],
        set_={"name": stmt.excluded.name},
    )

    with SessionLocal() as db:
        db.execute(stmt)
        db.commit()
    print(f"{len(rows)}개 종목 반영 완료")


if __name__ == "__main__":
    main()