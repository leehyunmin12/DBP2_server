-- 복기노트 DB 샘플 (PostgreSQL 16): 구조 + 샘플 데이터
-- 매매 일지 + AI 복기 서비스 DB 스키마 (PostgreSQL, 3NF)

-- 1. ENUM 타입
CREATE TYPE market_type  AS ENUM ('KR', 'US'); -- 한국주식, 미국주식
CREATE TYPE trade_side   AS ENUM ('BUY', 'SELL'); -- 구매, 판매
CREATE TYPE trade_source AS ENUM ('MANUAL', 'CAPTURE'); -- 입력 방법 (직접 입력, 캡처 인식)
CREATE TYPE emotion_type AS ENUM ('CONFIDENT', 'ANXIOUS', 'IMPULSIVE', 'GREEDY', 'FEARFUL', 'NEUTRAL');  -- 구매할 때의 감정

-- 2. 사용자
CREATE TABLE users (
  id            BIGSERIAL    PRIMARY KEY,
  email         VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- 3. 종목 (종목명은 여기에만 저장)
CREATE TABLE stocks (
  market market_type  NOT NULL, -- 시장 종류
  symbol VARCHAR(20)  NOT NULL, -- 종목 구분 코드 (AAPL, 005930)
  name   VARCHAR(100) NOT NULL, -- 종목명
  PRIMARY KEY (market, symbol)
);

-- 4. 매매 기록 (가격은 시장 통화 기준: KR=원, US=달러)
CREATE TABLE trades (
  id          BIGSERIAL     PRIMARY KEY,
  user_id     BIGINT        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  market      market_type   NOT NULL,
  symbol      VARCHAR(20)   NOT NULL,
  side        trade_side    NOT NULL,
  qty         NUMERIC(18,4) NOT NULL CHECK (qty > 0), -- 개수
  price       NUMERIC(18,4) NOT NULL CHECK (price > 0), -- 가격
  traded_on   DATE          NOT NULL,
  source      trade_source  NOT NULL,
  FOREIGN KEY (market, symbol) REFERENCES stocks (market, symbol)
);
CREATE INDEX idx_trades_user_date ON trades (user_id, traded_on);

-- 5. 매매 메모 (매매 1건당 최대 1개)
CREATE TABLE trade_notes (
  id         BIGSERIAL    PRIMARY KEY,
  trade_id   BIGINT       NOT NULL UNIQUE REFERENCES trades(id) ON DELETE CASCADE,
  reason     TEXT         NOT NULL,
  emotion    emotion_type
);

-- 6. 복기 리포트 (기간별 분석 결과 스냅샷)
--    summary는 AI 요약이 실패하면 NULL (통계만 먼저 보여 주고 나중에 생성)
CREATE TABLE reports (
  id           BIGSERIAL    PRIMARY KEY,
  user_id      BIGINT       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  market       market_type  NOT NULL,
  period_start DATE         NOT NULL,
  period_end   DATE         NOT NULL,
  stats_json   JSONB        NOT NULL,
  summary      TEXT,
  created_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
  CHECK (period_end >= period_start)
);

-- ===================== 샘플 데이터 =====================
-- 이 파일 하나로 구조와 샘플 데이터가 모두 만들어진다. (빈 DB에 실행)
-- 로그인 계정: demo@example.com / demo1234

-- 종목 (db/seed/stocks.csv와 같은 내용)
INSERT INTO stocks (market, symbol, name) VALUES
  ('KR', '000100', '유한양행'),
  ('KR', '000270', '기아'),
  ('KR', '000660', 'SK하이닉스'),
  ('KR', '000720', '현대건설'),
  ('KR', '000810', '삼성화재'),
  ('KR', '003490', '대한항공'),
  ('KR', '003550', 'LG'),
  ('KR', '003670', '포스코퓨처엠'),
  ('KR', '005380', '현대차'),
  ('KR', '005490', 'POSCO홀딩스'),
  ('KR', '005930', '삼성전자'),
  ('KR', '005935', '삼성전자우'),
  ('KR', '006400', '삼성SDI'),
  ('KR', '006800', '미래에셋증권'),
  ('KR', '009150', '삼성전기'),
  ('KR', '009540', 'HD한국조선해양'),
  ('KR', '009830', '한화솔루션'),
  ('KR', '010130', '고려아연'),
  ('KR', '010140', '삼성중공업'),
  ('KR', '010950', 'S-Oil'),
  ('KR', '011200', 'HMM'),
  ('KR', '012330', '현대모비스'),
  ('KR', '012450', '한화에어로스페이스'),
  ('KR', '015760', '한국전력'),
  ('KR', '016360', '삼성증권'),
  ('KR', '017670', 'SK텔레콤'),
  ('KR', '018260', '삼성에스디에스'),
  ('KR', '022100', '포스코DX'),
  ('KR', '024110', '기업은행'),
  ('KR', '028260', '삼성물산'),
  ('KR', '028300', 'HLB'),
  ('KR', '030200', 'KT'),
  ('KR', '032830', '삼성생명'),
  ('KR', '033780', 'KT&G'),
  ('KR', '034020', '두산에너빌리티'),
  ('KR', '034730', 'SK'),
  ('KR', '035420', 'NAVER'),
  ('KR', '035720', '카카오'),
  ('KR', '035900', 'JYP Ent.'),
  ('KR', '036570', '엔씨소프트'),
  ('KR', '039030', '이오테크닉스'),
  ('KR', '041510', '에스엠'),
  ('KR', '042660', '한화오션'),
  ('KR', '042700', '한미반도체'),
  ('KR', '047050', '포스코인터내셔널'),
  ('KR', '047810', '한국항공우주'),
  ('KR', '051900', 'LG생활건강'),
  ('KR', '051910', 'LG화학'),
  ('KR', '055550', '신한지주'),
  ('KR', '058470', '리노공업'),
  ('KR', '064350', '현대로템'),
  ('KR', '066570', 'LG전자'),
  ('KR', '068270', '셀트리온'),
  ('KR', '079550', 'LIG넥스원'),
  ('KR', '086520', '에코프로'),
  ('KR', '086790', '하나금융지주'),
  ('KR', '090430', '아모레퍼시픽'),
  ('KR', '096770', 'SK이노베이션'),
  ('KR', '105560', 'KB금융'),
  ('KR', '196170', '알테오젠'),
  ('KR', '207940', '삼성바이오로직스'),
  ('KR', '247540', '에코프로비엠'),
  ('KR', '251270', '넷마블'),
  ('KR', '259960', '크래프톤'),
  ('KR', '263750', '펄어비스'),
  ('KR', '267260', 'HD현대일렉트릭'),
  ('KR', '277810', '레인보우로보틱스'),
  ('KR', '293490', '카카오게임즈'),
  ('KR', '316140', '우리금융지주'),
  ('KR', '323410', '카카오뱅크'),
  ('KR', '329180', 'HD현대중공업'),
  ('KR', '352820', '하이브'),
  ('KR', '373220', 'LG에너지솔루션'),
  ('KR', '377300', '카카오페이'),
  ('KR', '403870', 'HPSP'),
  ('KR', '454910', '두산로보틱스'),
  ('US', 'AAPL', '애플'),
  ('US', 'ADBE', '어도비'),
  ('US', 'AMD', 'AMD'),
  ('US', 'AMZN', '아마존'),
  ('US', 'ARM', '암 홀딩스'),
  ('US', 'ASML', 'ASML'),
  ('US', 'AVGO', '브로드컴'),
  ('US', 'BA', '보잉'),
  ('US', 'BAC', '뱅크오브아메리카'),
  ('US', 'BRK-B', '버크셔 해서웨이 B'),
  ('US', 'COIN', '코인베이스'),
  ('US', 'COST', '코스트코'),
  ('US', 'CRM', '세일즈포스'),
  ('US', 'CSCO', '시스코'),
  ('US', 'CVX', '셰브런'),
  ('US', 'DIS', '월트 디즈니'),
  ('US', 'GOOGL', '알파벳 A'),
  ('US', 'GS', '골드만삭스'),
  ('US', 'HD', '홈디포'),
  ('US', 'INTC', '인텔'),
  ('US', 'JNJ', '존슨앤드존슨'),
  ('US', 'JPM', 'JP모건 체이스'),
  ('US', 'KO', '코카콜라'),
  ('US', 'LLY', '일라이 릴리'),
  ('US', 'MA', '마스터카드'),
  ('US', 'MCD', '맥도날드'),
  ('US', 'META', '메타 플랫폼스'),
  ('US', 'MSFT', '마이크로소프트'),
  ('US', 'MU', '마이크론'),
  ('US', 'NFLX', '넷플릭스'),
  ('US', 'NKE', '나이키'),
  ('US', 'NVDA', '엔비디아'),
  ('US', 'ORCL', '오라클'),
  ('US', 'PEP', '펩시코'),
  ('US', 'PFE', '화이자'),
  ('US', 'PG', '프록터 앤드 갬블'),
  ('US', 'PLTR', '팔란티어'),
  ('US', 'PYPL', '페이팔'),
  ('US', 'QCOM', '퀄컴'),
  ('US', 'QQQ', '인베스코 QQQ ETF'),
  ('US', 'RIVN', '리비안'),
  ('US', 'SBUX', '스타벅스'),
  ('US', 'SCHD', '슈왑 미국 배당주 ETF'),
  ('US', 'SMCI', '슈퍼 마이크로 컴퓨터'),
  ('US', 'SOFI', '소파이'),
  ('US', 'SOXL', '디렉시온 반도체 불 3배 ETF'),
  ('US', 'SPY', 'SPDR S&P500 ETF'),
  ('US', 'TQQQ', '프로셰어즈 울트라프로 QQQ'),
  ('US', 'TSLA', '테슬라'),
  ('US', 'TSM', 'TSMC'),
  ('US', 'UBER', '우버'),
  ('US', 'UNH', '유나이티드헬스'),
  ('US', 'V', '비자'),
  ('US', 'VOO', '뱅가드 S&P500 ETF'),
  ('US', 'WFC', '웰스파고'),
  ('US', 'WMT', '월마트'),
  ('US', 'XOM', '엑슨모빌');

-- 사용자
INSERT INTO users (id, email, password_hash, created_at) VALUES
  (1, 'demo@example.com', '$2b$12$pE/I3Q15H2me5f8Ks40VQOFEFrFMTe3/m1GsHAPwGk5sdQVwzK5jK', '2026-11-22 13:50:42+00');

-- 매매 기록 (source: MANUAL=직접 입력, CAPTURE=캡처 인식)
INSERT INTO trades (id, user_id, market, symbol, side, qty, price, traded_on, source) VALUES
  (1, 1, 'KR', '005930', 'BUY', 10.0000, 68000.0000, '2026-08-04', 'MANUAL'),
  (2, 1, 'KR', '005930', 'SELL', 10.0000, 72500.0000, '2026-08-20', 'MANUAL'),
  (3, 1, 'KR', '000660', 'BUY', 5.0000, 180000.0000, '2026-08-12', 'MANUAL'),
  (4, 1, 'KR', '000660', 'SELL', 5.0000, 195000.0000, '2026-09-05', 'MANUAL'),
  (5, 1, 'KR', '005380', 'BUY', 4.0000, 240000.0000, '2026-09-01', 'MANUAL'),
  (6, 1, 'KR', '005380', 'SELL', 4.0000, 250000.0000, '2026-10-22', 'MANUAL'),
  (7, 1, 'KR', '035420', 'BUY', 6.0000, 210000.0000, '2026-09-15', 'MANUAL'),
  (8, 1, 'KR', '035420', 'SELL', 6.0000, 195000.0000, '2026-10-28', 'MANUAL'),
  (9, 1, 'KR', '035720', 'BUY', 20.0000, 50000.0000, '2026-09-22', 'MANUAL'),
  (10, 1, 'KR', '035720', 'SELL', 20.0000, 45500.0000, '2026-10-30', 'MANUAL'),
  (11, 1, 'KR', '034020', 'BUY', 3.0000, 98200.0000, '2026-10-06', 'CAPTURE'),
  (12, 1, 'KR', '034020', 'BUY', 1.0000, 93400.0000, '2026-10-06', 'CAPTURE'),
  (13, 1, 'KR', '034020', 'SELL', 4.0000, 103500.0000, '2026-11-10', 'CAPTURE'),
  (14, 1, 'KR', '005930', 'BUY', 3.0000, 75000.0000, '2026-11-12', 'MANUAL'),
  (15, 1, 'US', 'AAPL', 'BUY', 3.0000, 189.5000, '2026-09-20', 'MANUAL'),
  (16, 1, 'US', 'AAPL', 'SELL', 3.0000, 201.2500, '2026-10-02', 'MANUAL'),
  (17, 1, 'US', 'TSLA', 'BUY', 2.0000, 245.0000, '2026-10-08', 'MANUAL'),
  (18, 1, 'US', 'TSLA', 'SELL', 2.0000, 221.5000, '2026-11-03', 'MANUAL');

-- 매매 메모 (매매 1건당 최대 1개)
INSERT INTO trade_notes (id, trade_id, reason, emotion) VALUES
  (1, 1, '실적 발표 전에 분할 매수', 'CONFIDENT'),
  (2, 2, '목표가에 도달해 매도', 'CONFIDENT'),
  (3, 3, '급등하는 걸 보고 따라 매수', 'GREEDY'),
  (4, 4, '더 오를 것 같아 욕심내다 늦게 매도', 'GREEDY'),
  (5, 5, '분할 매수 계획대로 진입', 'NEUTRAL'),
  (6, 7, '커뮤니티 글 보고 충동적으로 매수', 'IMPULSIVE'),
  (7, 8, '손실이 커져 급하게 손절', 'IMPULSIVE'),
  (8, 9, '떨어져서 물타기', 'ANXIOUS'),
  (9, 10, '더 떨어질까 무서워 매도', 'FEARFUL'),
  (10, 14, '눌림목에서 추가 매수', 'NEUTRAL'),
  (11, 16, '지인 추천 받고 급해서 매도', 'IMPULSIVE'),
  (12, 17, '상승 분위기에 올라탐', 'GREEDY'),
  (13, 18, '손실이 커질까 불안해서 매도', 'ANXIOUS');

-- 복기 리포트 (id=2는 AI 요약이 없는 경우: summary NULL)
INSERT INTO reports (id, user_id, market, period_start, period_end, stats_json, summary, created_at) VALUES
  (1, 1, 'KR', '2026-08-01', '2026-11-22', '{"summary": {"avg_loss": -90000.0, "win_rate": 0.6666666666666666, "total_pnl": 6000.0, "win_count": 4, "avg_profit": 46500.0, "loss_count": 2, "sell_count": 6}, "by_stock": [{"pnl": 45000.0, "name": "삼성전자", "market": "KR", "symbol": "005930", "sell_count": 1}, {"pnl": 75000.0, "name": "SK하이닉스", "market": "KR", "symbol": "000660", "sell_count": 1}, {"pnl": 40000.0, "name": "현대차", "market": "KR", "symbol": "005380", "sell_count": 1}, {"pnl": -90000.0, "name": "NAVER", "market": "KR", "symbol": "035420", "sell_count": 1}, {"pnl": -90000.0, "name": "카카오", "market": "KR", "symbol": "035720", "sell_count": 1}, {"pnl": 26000.0, "name": "두산에너빌리티", "market": "KR", "symbol": "034020", "sell_count": 1}], "by_emotion": [{"pnl": 45000.0, "emotion": "CONFIDENT", "win_rate": 1.0, "sell_count": 1}, {"pnl": 75000.0, "emotion": "GREEDY", "win_rate": 1.0, "sell_count": 1}, {"pnl": 66000.0, "emotion": "NONE", "win_rate": 1.0, "sell_count": 2}, {"pnl": -90000.0, "emotion": "IMPULSIVE", "win_rate": 0.0, "sell_count": 1}, {"pnl": -90000.0, "emotion": "FEARFUL", "win_rate": 0.0, "sell_count": 1}], "highlights": [{"pnl": -90000.0, "date": "2026-10-28", "name": "NAVER", "rate": -0.07142857142857142, "reason": "손실이 커져 급하게 손절", "emotion": "IMPULSIVE"}, {"pnl": -90000.0, "date": "2026-10-30", "name": "카카오", "rate": -0.09, "reason": "더 떨어질까 무서워 매도", "emotion": "FEARFUL"}, {"pnl": 75000.0, "date": "2026-09-05", "name": "SK하이닉스", "rate": 0.08333333333333333, "reason": "더 오를 것 같아 욕심내다 늦게 매도", "emotion": "GREEDY"}, {"pnl": 45000.0, "date": "2026-08-20", "name": "삼성전자", "rate": 0.0661764705882353, "reason": "목표가에 도달해 매도", "emotion": "CONFIDENT"}, {"pnl": 40000.0, "date": "2026-10-22", "name": "현대차", "rate": 0.041666666666666664, "reason": null, "emotion": "NONE"}], "buy_summary": {"buy_count": 8, "buy_amount": 5413000.0, "by_emotion": [{"emotion": "NEUTRAL", "buy_count": 2}, {"emotion": "CONFIDENT", "buy_count": 1}, {"emotion": "GREEDY", "buy_count": 1}, {"emotion": "IMPULSIVE", "buy_count": 1}, {"emotion": "ANXIOUS", "buy_count": 1}, {"emotion": "NONE", "buy_count": 2}]}, "has_unmatched": false}', '## 한 줄 총평
총 실현손익은 +6,000원이며, 승률은 67%(매도 6건 중 이익 4건, 손실 2건)입니다.

## 잘한 점
- 목표가에 도달해 매도 (삼성전자, +45,000원)
- 분할 매수 계획대로 진입해 이익을 낸 거래 (현대차, +40,000원)

## 아쉬운 점
- 매도 건수가 6건이라 표본이 적어 아래 내용은 참고용입니다.
- 커뮤니티 글을 보고 충동적으로 매수했다가 손실 (NAVER, -90,000원) → 매수 전에 근거를 한 줄 적어 보세요.
- 불안과 공포 상태에서 매도한 거래가 손실로 이어졌습니다 (카카오, -90,000원) → 손절 기준을 미리 적어 두면 감정에 덜 흔들릴 수 있습니다.
- 이익이었지만 욕심 때문에 늦게 판 거래도 습관 점검이 필요합니다 (SK하이닉스).

## 다음에 점검할 것
- 매수 근거를 메모에 남겼는가?
- 손실이 났을 때 정해 둔 기준으로 판단했는가?
- 이익이 났을 때 목표가를 미리 정해 두었는가?
', '2026-11-22 13:50:43+00'),
  (2, 1, 'US', '2026-09-01', '2026-11-22', '{"summary": {"avg_loss": -47.0, "win_rate": 0.5, "total_pnl": -11.75, "win_count": 1, "avg_profit": 35.25, "loss_count": 1, "sell_count": 2}, "by_stock": [{"pnl": 35.25, "name": "애플", "market": "US", "symbol": "AAPL", "sell_count": 1}, {"pnl": -47.0, "name": "테슬라", "market": "US", "symbol": "TSLA", "sell_count": 1}], "by_emotion": [{"pnl": 35.25, "emotion": "IMPULSIVE", "win_rate": 1.0, "sell_count": 1}, {"pnl": -47.0, "emotion": "ANXIOUS", "win_rate": 0.0, "sell_count": 1}], "highlights": [{"pnl": -47.0, "date": "2026-11-03", "name": "테슬라", "rate": -0.09591836734693877, "reason": "손실이 커질까 불안해서 매도", "emotion": "ANXIOUS"}, {"pnl": 35.25, "date": "2026-10-02", "name": "애플", "rate": 0.06200527704485488, "reason": "지인 추천 받고 급해서 매도", "emotion": "IMPULSIVE"}], "buy_summary": {"buy_count": 2, "buy_amount": 1058.5, "by_emotion": [{"emotion": "NONE", "buy_count": 1}, {"emotion": "GREEDY", "buy_count": 1}]}, "has_unmatched": false}', NULL, '2026-11-22 13:50:43+00');

-- id 자동 증가 값을 맞춰 둔다
SELECT setval('users_id_seq',       (SELECT MAX(id) FROM users));
SELECT setval('trades_id_seq',      (SELECT MAX(id) FROM trades));
SELECT setval('trade_notes_id_seq', (SELECT MAX(id) FROM trade_notes));
SELECT setval('reports_id_seq',     (SELECT MAX(id) FROM reports));
