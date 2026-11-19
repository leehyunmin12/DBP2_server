import time
from datetime import date

from app.core.database import SessionLocal
from app.services import trade as trade_service
from app.services.ai import generate_summary
from app.services.report_prompt import build_prompt, pick_highlights
from app.services.stats import build_stats, calc_realized, select_sells

USER_ID = 1  # 본인 계정 id
a, b = date(2026, 8, 1), date(2026, 11, 19)

with SessionLocal() as db:
    trades = trade_service.list_all_trades(db, USER_ID)
    rl = calc_realized(trades)
    stats = build_stats(trades, rl, a, b, "KR")
    hl = pick_highlights(select_sells(trades, rl, a, b, "KR"))
    system, user = build_prompt("KR", a, b, stats, hl)

start = time.time()
text = generate_summary(system, user)
print(f"걸린 시간: {time.time() - start:.1f}초\n")
print(text)