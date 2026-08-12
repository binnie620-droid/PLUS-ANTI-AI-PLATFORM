# Source / Citation Rules & Anti-Hallucination Rules

## 1. 출처 우선순위 (숫자를 찾을 때 이 순서로 탐색)

1. 기업 IR / Annual Report / 사업보고서 / 공시 (1차 자료, 최우선)
2. 정부·규제기관 (에너지부, 규제위원회, 전력수급계획 등)
3. 국제기관 (IEA, IAEA, IPCC 등)
4. 산업협회
5. 신뢰도 높은 리서치기관 (BCG, Wood Mackenzie 등)
6. 증권사 Research
7. 주요 Financial Media

**가능하면 항상 1차 자료를 우선한다.** 아래 항목은 출처 없는 숫자를 절대 쓰지 않는다:
Market Size, CAGR, Market Share, Revenue, Margin, CAPEX, Backlog, Consensus, Multiple,
Target Price 관련 Input 전부.

## 2. Fact / Estimate / Assumption 태깅 (모든 리포트, 모든 CASE 공통)

핵심 숫자마다 다음 중 하나를 인라인으로 표시한다:

- `[FACT]` — 1차 자료에 직접 명시된 값 (출처 각주 필수)
- `[ESTIMATE]` — Fact를 근거로 desk-head가 계산한 값 (계산식 명시 필수)
- `[ASSUMPTION]` — 근거 자료 없이 desk-head가 가정한 값 (가정 이유 + 민감도 영향 필수)

## 3. 데이터 없을 때

숫자를 만들어내지 않는다. 대신:
- `[Data unavailable]` — 조사했으나 확인 불가
- `[Assumption required — 근거: ...]` — 가정으로 대체했고 그 근거를 붙임

두 표시 모두 그 숫자가 최종 결론(Target Price, Decision 등)에 미치는 영향을 1문장으로
서술한다. 영향이 크면(예: Target Price가 ±10%p 이상 흔들림) Quality Gate 통과를 보류하고
추가 Research를 시도한다.

## 4. Anti-Hallucination — 절대 금지 목록

다음을 만들어내는 것은 예외 없이 금지된다:
- 숫자 (매출, 마진, 시장점유율, CAGR 등)
- 존재하지 않는 보고서·공시·계약
- 시장점유율
- 컨센서스 (실제 확인 안 된 애널리스트 평균)
- 기업 Guidance
- Valuation Multiple (근거 없이 "적정 P/E는 15배" 식으로 던지는 것)
- 출처 (실제로 확인하지 않은 자료를 인용한 것처럼 쓰는 것)

확인할 수 없는 내용은 반드시 §3의 표시 방식으로 명확히 드러낸다. "일반적으로",
"~로 알려져 있다" 같은 표현 뒤에 근거 없는 숫자를 숨기지 않는다.

## 5. CASE D 전용 추가 규칙

CASE D(0개 통과)에서는 개별 기업 숫자(매출추정/목표주가 등)를 **원천적으로 산출하지
않는다** — 이는 Fact/Estimate/Assumption 태깅 대상조차 아니다. 산업 차원 숫자(TAM, CAGR
등)는 여전히 §1~§3 규칙을 그대로 따른다.
