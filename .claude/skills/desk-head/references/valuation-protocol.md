# Valuation & Target Price Protocol

CASE D(0개 통과)에는 이 문서를 적용하지 않는다 — 개별 기업 Valuation을 하지 않기 때문이다.
CASE A/B/C에서 최종 후보로 남은 **모든** 기업에 대해 반드시 목표주가(Target Price)를
제시한다.

## 1. Method 선택

기업 특성에 맞는 방법을 고른다. 자의적 선택을 막기 위한 가이드:

| 기업 특성 | 권장 1차 Method | 권장 Cross-check Method |
|---|---|---|
| 안정적 장기 CF, Capex 집약 인프라/설비 | DCF | EV/EBITDA (peer) |
| 지주/자회사 보유 구조 | DCF + SOTP(자회사 지분가치 가산) | P/B, Peer 합산 시총 비교 |
| 고성장, 이익 아직 불안정 | EV/Sales 또는 PEG | DCF (민감도 넓게) |
| 금융/자산 중심 | P/B, ROE 기반 | DDM |
| 성숙 산업, 안정적 이익 | P/E (peer 대비) | EV/EBITDA |

**최소 2개 Method로 Cross-check한다.** 두 값이 크게 벌어지면(예: ±20%p 이상) 그 이유를
설명하고, 최종 목표주가는 단순평균이 아니라 어느 Method에 더 가중치를 두는지와 그 이유를
명시한다.

## 2. DCF Protocol (해당 시)

### WACC — 반드시 아래 순서로 처음부터 계산한다 (임의의 WACC 숫자 금지)

```
1) 타인자본비용(Cost of Debt)
   = 신용등급 기반 동일등급 회사채 금리 [FACT/ESTIMATE, 출처 명시]
   세후 CoD = CoD × (1 − 한계세율)

2) 자기자본비용(Cost of Equity) — CAPM
   CoE = Rf + β × ERP + Size Premium
   - Rf: 무위험이자율 (자국 10년물 국채금리) [FACT, 출처·기준일 명시]
   - ERP: Equity Risk Premium [FACT, 출처 명시 — 예: 공인회계사회 가이던스,
     Damodaran 등]
   - β: Peer Group의 Unlevered Beta 평균을 구한 뒤, Target 기업의 자본구조로
     Relever. Peer의 사업 노출도가 Target과 다르면(예: 방산/특수사업 겸영)
     할인/할증 근거를 서술하고 조정 β를 사용 — 조정 없이 그대로 쓰지 말 것
   - Size Premium: 시가총액 규모에 따른 프리미엄 [FACT, 출처 명시]

3) WACC = 세후CoD × (D/(D+E)) + CoE × (E/(D+E))
```

WACC 값 자체보다 **이 계산 과정이 리포트에 재현 가능한 표로 나와야 한다** (두산 보고서의
WACC 계산표·Peer Beta 표 형태를 최소 기준으로 삼는다).

### FCFF & Terminal Value

- 명시적 추정기간은 `research-and-forecast-protocol.md`와 동일하게 **15~20개년**을
  기본으로 한다(장기 구조적 성장 산업 기준). 단기 실적 가시성만 있는 기업은 최소 5년까지
  축소할 수 있으나, 축소한 이유를 명시한다. FCFF = NOPAT + D&A − ΔNWC − CAPEX
- Terminal Value = FCFF(n+1) / (WACC − g), g는 산업의 장기 구조적 성장 특성과 물가상승률
  근거로 정당화 (임의로 2~3%를 넣지 말 것 — 왜 그 g인지 1문장 이상)
- 영업가치 = PV(FCFF) + PV(TV)

### SOTP 가산 (지주/자회사 구조가 있는 경우)

```
적정 시가총액 = 영업가치
              + Σ(상장 자회사 지분가치: 자회사 시총 × 지분율)
              + 기타 비영업자산
              − 이자부부채
적정주가 = 적정 시가총액 / 총 주식수
```

## 3. Target Price 계산식 — 반드시 명시적으로 표시

리포트에는 아래 형태로 **계산식 자체**가 드러나야 한다 (숫자만 던지고 끝내지 않는다):

```
예) Target Price = Forward EPS × Target P/E
예) Target Price = (영업가치 + 자회사지분가치 + 기타자산 − 이자부부채) / 주식수
```

### Target Multiple 정당화 (임의 입력 절대 금지)

Target Multiple(P/E, EV/EBITDA 등)을 쓸 경우, 아래 중 최소 2개 이상의 근거로 정당화한다:

- Historical Multiple (자사 과거 평균 대비 프리미엄/디스카운트 이유)
- Peer Multiple (비교기업 선정 기준을 명시 — 사업유사성, 성장률, 지역 등)
- Growth Premium (성장률 차이만큼의 조정)
- ROE / ROIC (자본효율성 비교)
- Earnings Visibility (수주잔고, 장기계약 비중 등 가시성)
- Risk Profile (재무구조, 사업 집중도 등)

## 4. 필수 표시 항목 (모든 최종 후보 기업, 예외 없음)

| 항목 | 설명 |
|---|---|
| Current Price | 기준일자 현재가 [FACT] |
| Target Price | 산출 목표주가 [ESTIMATE, 계산식 첨부] |
| Upside / Downside (%) | (TP/현재가 − 1) |
| Applied Multiple | 사용한 Target Multiple과 그 정당화 근거 |
| Reference Earnings | Multiple을 곱한 기준 실적(Forward EPS 등)과 그 연도 |
| Valuation Date | 기준일자 |
| Target Price Horizon | Investment Horizon과 동일 근거 (→ `horizon-and-catalyst.md`) |

## 5. 민감도 분석 (필수)

DCF를 썼다면 WACC × g 2차원 민감도 테이블을 제시한다(두산 보고서 방식). Multiple 기반이면
Target Multiple × Reference Earnings 민감도 테이블로 대체한다. 목적은 "목표주가가 얼마나
가정에 취약한지"를 숨기지 않는 것이다.
