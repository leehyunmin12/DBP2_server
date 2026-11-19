-- 매매 일지 + AI 복기 서비스 DB 스키마 (PostgreSQL, 3NF)

-- 1. ENUM 타입
CREATE TYPE market_type  AS ENUM ('KR', 'US'); -- 한국주식, 미국주식
CREATE TYPE trade_side   AS ENUM ('BUY', 'SELL'); -- 구매, 판매
CREATE TYPE trade_source AS ENUM ('MANUAL', 'CAPTURE', 'SAMPLE'); -- 사진 출처
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
  traded_time TIME,
  source      trade_source  NOT NULL,
  created_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),
  FOREIGN KEY (market, symbol) REFERENCES stocks (market, symbol)
);
CREATE INDEX idx_trades_user_date ON trades (user_id, traded_on);

-- 5. 매매 메모 (매매 1건당 최대 1개)
CREATE TABLE trade_notes (
  id         BIGSERIAL    PRIMARY KEY,
  trade_id   BIGINT       NOT NULL UNIQUE REFERENCES trades(id) ON DELETE CASCADE,
  reason     TEXT         NOT NULL,
  emotion    emotion_type,
  created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- 6. 시세 캐시 (종가, 시장 통화 기준)
CREATE TABLE market_prices (
  market market_type   NOT NULL,
  symbol VARCHAR(20)   NOT NULL,
  date   DATE          NOT NULL,
  close  NUMERIC(18,4) NOT NULL,
  PRIMARY KEY (market, symbol, date),
  FOREIGN KEY (market, symbol) REFERENCES stocks (market, symbol)
);

-- 7. 복기 리포트 (기간별 분석 결과 스냅샷)
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
