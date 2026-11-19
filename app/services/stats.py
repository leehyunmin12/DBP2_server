from collections import defaultdict
from dataclasses import dataclass
from datetime import time
from decimal import Decimal

from matplotlib.pyplot import hsv

from app.models import Stock


@dataclass
class Realized:
    pnl: Decimal
    rate: Decimal
    unmatched_qty: Decimal = Decimal("0")


def calc_realized(trades) -> dict[int, Realized]:
    groups = defaultdict(list) # 없는 키를 처음 쓰면 빈 리스트를 자동으로 만들어 줌
    for t in trades:
        groups[(t.market, t.symbol)].append(t) # [{"KR", "005930"]: [거래1, 거래2, 거래3]

    # 계산 결과를 담을 빈 딕셔너리
    result: dict[int, Realized] = {}

    for group in groups.values(): # 종목 하나의 전체 거래씩 실행
        # 오래된 거래 순으로 정렬 처리
        group.sort(key=lambda t: (t.traded_on, t.traded_time or time.min, t.id))

        qty = Decimal("0")
        avg = Decimal("0")
        for t in group: # t는 한 거래내역 객체
            if t.side == "BUY": # 구매 내역
                total = avg * qty + t.price * t.qty # 지금까지 총 금액 + 이번에 구매 금액
                qty += t.qty # 보유 수량 +
                avg = total / qty # 새로운 평균 단가 구하기
            else: # 판매 내역
                sell_qty = min(t.qty, qty) # 만약 팔 수량이 보유 수량보다 많다면 최대한 많이 팔고 나머지는
                unmatched = t.qty - sell_qty # unmatched에 저장
                if sell_qty > 0: # 팔 주식이 있는 경우
                    pnl = (t.price - avg) * sell_qty # 손익은 (판 가격 - 평균단가) * 수량이다.
                    rate = (t.price - avg) / avg # 수익률은 평균단가 대비 비율
                else: # 팔 주식이 없는데 판 경우 전부 0으로 초기화
                    pnl, rate = Decimal("0"), Decimal("0")
                result[t.id] = Realized(pnl, rate, unmatched) # 거래 결과 저장
                qty -= sell_qty # 판매 개수 빼기
                if qty == 0:
                    avg = Decimal("0")

    return result


def _win_rate(win_count: int, counted: int) -> float:
    return win_count / counted if counted else 0.0 # 승률, 승리 수 / 거래 수


def build_stats(trades, realized, date_from, date_to, market) -> dict:
    # TODO 1. 대상 SELL 고르기
    sells = []

    for t in trades:
        if t.side != "SELL":
            continue
        r = realized.get(t.id)
        if r is None:
            continue
        if date_from and t.traded_on < date_from:
            continue
        if date_to and t.traded_on > date_to:
            continue
        if market and t.market != market:
            continue
        if t.qty - r.unmatched_qty <= 0:
            continue
        sells.append((t, r))



    # TODO 2. summary 계산
    pnls = [r.pnl for _, r in sells]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    summary = {
        "total_pnl": float(sum(pnls)),
        "sell_count": len(sells),
        "win_count": len(wins),
        "loss_count": len(losses),
        "win_rate": _win_rate(len(wins), len(sells)),
        "avg_profit": float(sum(wins) / len(wins)) if wins else 0.0,
        "avg_loss": float(sum(losses) / len(losses)) if losses else 0.0,
    }

    # TODO 3. by_stock : (market, symbol)별로 묶어서 손익 합계, 매도 횟수

    stock_map = defaultdict(lambda: {"pnl": Decimal("0"), "sell_count": 0, "name": ""})
    for t, r in sells:
        s = stock_map[(t.market, t.symbol)] # market과 symbol을 키로 가져감
        s["pnl"] += r.pnl
        s["sell_count"] += 1
        s["name"] = t.stock.name
    by_stock = [
        {"market": m, "symbol": sym, "name": v["name"],
            "pnl": float(v["pnl"]), "sell_count": v["sell_count"]}
            for (m, sym), v in stock_map.items()
        ]

    # TODO 4. by_emotion : 감정별로 묶어서 매도 횟수, 손익 합계, 승률

    emotion_map = defaultdict(lambda: {"pnl": Decimal("0"), "sell_count": 0, "win_count": 0})
    for t, r in sells:
        emotion = t.note.emotion if t.note and t.note.emotion else "NONE" # 감정은 t.note.emotion, 메모가 없거나 감정이 없으면 "NONE"
        e = emotion_map[emotion]
        e["pnl"] += r.pnl
        e["sell_count"] += 1
        if r.pnl > 0:
            e["win_count"] += 1

    by_emotion = [
        {
            "emotion": emo, "sell_count": v["sell_count"], "pnl": float(v["pnl"]),
            "win_rate": _win_rate(v["win_count"], v["sell_count"])
        }
        for emo, v in emotion_map.items()
    ]

    # TODO 5. has_unmatched : realized 중 unmatched_qty > 0 이 하나라도 있으면 True
    #   ※ 기간·시장 필터와 상관없이 전체 기준
    has_unmatched = any(r.unmatched_qty > 0 for r in realized.values())

    return {
        "summary": summary,
        "by_stock": by_stock,
        "by_emotion": by_emotion,
        "has_unmatched": has_unmatched,
    }