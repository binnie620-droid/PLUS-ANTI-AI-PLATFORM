# Investment Horizon & Catalyst Timeline Protocol

CASE D에는 적용하지 않는다. CASE A/B/C의 모든 최종 후보 기업에 대해 목표주가와
**별도로** 권장 투자기간을 반드시 제시한다. "장기투자"처럼 기간을 특정하지 않는 표현은
금지한다.

## 1. Horizon 결정 로직

Investment Horizon은 임의로 고르는 것이 아니라 **Catalyst가 실적/멀티플에 반영되는
시점**에 근거해서 정한다. 아래 표준 구간 중 하나를 고르고, 그 구간을 고른 이유를
1문단으로 서술한다.

| Horizon | 적합한 경우 |
|---|---|
| 6M | 이미 확정된 단기 이벤트(실적 발표, 확정 계약 매출인식 개시)만 남은 경우 |
| 12M | 신규 수주가 매출로 인식되기 시작하는 시점, 근시일 내 정책/규제 변화 |
| 18M | CAPEX 완공 및 가동, 신제품 출시가 실적에 반영되는 시점 |
| 24M | Margin Improvement가 구조적으로 확인되는 시점, 시장 재평가(re-rating)까지 필요한
      시간 |
| 3Y+ | 산업 자체의 성숙(예: SMR 상용화)까지 필요한 시간 — 단, 이 경우 왜 지금
      진입해야 하는지(독립검토 질문 9,10) 근거가 더 강해야 한다 |

이유 서술 예시 템플릿:
```
Investment Horizon: 12–18 months
이유: 1) 26년 1분기 확정 수주분이 27년부터 매출 인식 시작 2) 28년 CAPA 증설 완공
시점에 Margin이 구조적으로 개선 3) 그 시점 이후 시장이 밸류에이션을 재평가할
가능성이 높음
```

## 2. Catalyst Timeline 템플릿 (기업별 필수)

```
0–6M
  - [카테고리: Earnings/Order/Product Launch/CAPEX/Regulation/Industry Event/
    Market Share] 이벤트 설명 [FACT/ESTIMATE, 출처·예상시점]

6–12M
  - ...

12–24M
  - ...
```

각 이벤트는 다음 카테고리 중 하나 이상에 태깅한다: `Earnings` `Order` `Product Launch`
`CAPEX` `Regulation` `Industry Event` `Market Share Change`. 확정 이벤트는 `[FACT]`,
예상 이벤트는 `[ESTIMATE]`로 구분한다.

## 3. Horizon–Catalyst 일치 검증 (Quality Gate에서 재확인)

제시한 Investment Horizon 구간 안에 Catalyst Timeline 상 최소 1개 이상의 실질적
이벤트(단순 "실적 발표"가 아니라 Thesis에 영향을 주는 이벤트)가 있어야 한다. 없으면
Horizon을 다시 정한다 — Catalyst 없는 Horizon은 근거 없는 숫자다.
