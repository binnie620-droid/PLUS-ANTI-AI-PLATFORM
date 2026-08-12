# Case Branching Detail — A / B / C

CASE D(0개 통과)는 이 파일을 사용하지 않는다 → `report-templates.md`의 CASE D 섹션만
사용한다.

## CASE C — 1개 기업 통과

**Skill 3 통과 = 자동 BUY가 절대 아니다.** `independent-review.md`의 10문항을 전부
재검토한 뒤 아래 4개 중 하나로 독립 판정한다:

| 판정 | 조건 |
|---|---|
| BUY | Investment Thesis 성립 + 현재가 대비 충분한 Upside + Bear Case 감당 가능 |
| HOLD | Thesis는 유효하나 현재 가격이 기대를 상당 부분 반영 (Upside 제한적) |
| SELL | Thesis 자체가 약하거나 Bear Case 감당 불가 수준 (Skill 3 통과 판단을 뒤집는
       경우 — `input-normalization.md`의 충돌 해결 규칙에 따라 근거 명시 필수) |
| 투자보류 (Hold-for-Catalyst) | Thesis는 유효하나 지금 사야 할 긴급성이 없음
       (질문 9,10) — "6개월~1년 뒤 재검토" 형태로 결론 |

단일 기업이므로 Multi-Company Comparison은 생략하지만, **"더 좋은 대체 투자처가 없는가"
(질문 8)**는 반드시 다른 Skill 2 후보 기업(Skill 3에서 탈락한 5개 중 나머지, 또는 다른
산업의 후보)과 비교한 1문단을 넣는다 — 단일 종목이라도 진공 속에서 판단하지 않는다.

## CASE B — 2개 기업 통과

두 기업의 Investment Thesis를 각각 독립적으로 완성한 뒤(Case C와 동일한 깊이), **반드시
상대 비교**를 수행한다. 비교표는 CASE A와 동일한 형식(아래) 사용, 행은 유지하고 열만 2개.

최종적으로 **Top Pick / Second Pick**을 결정한다. 두 기업 모두 BUY가 아닐 수 있다(예:
Top Pick = BUY, Second Pick = HOLD, 또는 둘 다 HOLD).

## CASE A — 3개 기업 통과

### 보고서는 "3개 기업분석을 이어붙인 것"이 아니라 아래 순서의 단일 논리 흐름이어야 한다

```
AI 구조적 변화
   → 산업 선정 논리 (Skill 1의 6개 산업 중 왜 이 산업이 최종까지 남았는가)
   → 후보 기업 비교 (Skill 2의 산업별 5개 중 왜 이 3개가 Skill 3을 통과했는가, 요약)
   → 3개 기업 개별 투자논리 (각각 독립적인 Investment Thesis + Valuation + Horizon +
     Scenario — case-branching이 아니라 valuation-protocol.md/scenario-and-risk.md
     기준으로 개별 완성)
   → 기업 간 투자매력도 비교 (아래 표)
   → Portfolio 관점 (3개를 동시에 들고 있다면 어떤 상관관계/분산 이슈가 있는가 —
     동일 Catalyst에 의존하는 기업들인지, 겹치는 리스크가 있는지)
   → 최종 투자 판단 (1·2·3위 + 개별 BUY/HOLD/SELL/NO INVESTMENT)
```

### Multi-Company Comparison 표 (CASE A/B 공통 템플릿)

| 항목 | Company A | Company B | Company C |
|---|---|---|---|
| AI Structural Exposure | | | |
| Industry Growth | | | |
| Earnings Growth | | | |
| Earnings Visibility | | | |
| Competitive Moat | | | |
| ROIC | | | |
| Valuation (적용 Method/Multiple) | | | |
| Upside | | | |
| Catalyst (가장 가까운 것) | | | |
| Downside Risk (Bear Case) | | | |
| Risk/Reward | | | |
| Investment Horizon | | | |

### 우선순위 결정 규칙

1·2·3위는 채점표가 아니라 **위 비교표를 근거로 한 서술적 판단**이다. 순위를 정할 때
최소 아래를 고려한다: Risk/Reward(Upside 대비 Bear Downside), Earnings Visibility(수주잔고
등 가시성), Catalyst 근접성(Horizon이 짧을수록, 즉 곧 확인될수록 우선), Valuation 여유도.

**3개 모두 투자할 필요는 없다.** 예:
```
Company A → BUY (1위)
Company B → HOLD (2위, Thesis 유효하나 가격 부담)
Company C → NO INVESTMENT (3위, Bear Case 감당 불가로 개별 재검토에서 탈락)
```
이 경우도 정상적인 결과이며, "Skill 3을 통과했으니 3개 다 사야 한다"는 압박에 굴복하지
않는다.

### Portfolio 관점 — 이 섹션이 CASE A/B를 "리포트 3개 붙이기"와 구분하는 지점

3개(또는 2개) 기업이 동일한 Structural Change(예: 같은 AI 인프라 수요)에서 파생된 경우,
**Catalyst가 서로 얼마나 겹치는지**를 명시한다. 예를 들어 셋 다 같은 정책 발표에
의존한다면, 그 정책이 지연될 경우 셋이 동시에 타격받는 분산 실패 구조라는 점을
Risk 섹션에 명시한다.
