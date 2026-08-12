# Input Normalization Logic

Skill 1~3의 출력 형식은 세션마다, 팀원마다 조금씩 다를 수 있다(JSON, 표, 자유서술 등).
desk-head는 아래의 **canonical schema**로 무엇이든 정규화해서 이후 단계를 진행한다.

## Canonical Schema (내부적으로 항상 이 형태로 변환)

```yaml
industries:      # Skill 1, 6개 (A: 대체어려운 3개 + B: 미래효용증가 3개)
  - name: string
    category: "A_hard_to_replace" | "B_rising_utility"
    thesis: string            # 산업 구조/성장성/AI관계 핵심 논리
    tam: {value, unit, source, year} | null
    cagr: {value, source, period} | null
    risks: [string]

companies:       # Skill 2, 산업별 5개 (총 30개)
  - name, ticker, industry_ref
  - business_model, revenue_driver, competitive_position, market_share
  - financials: {revenue, margin, roic_roe, balance_sheet, cash_flow, capex}
  - valuation_asis, catalyst, risk, ai_linkage, price_expectation_embedded

verification:    # Skill 3
  passed_companies: [ticker]      # 0~3개
  pass_reasons: {ticker: string}
  rejected_companies: [ticker]
  reject_reasons: {ticker: string}
  key_risks: {ticker: [string]}
  rejection_memo: string | null   # 통과 0개일 때 반드시 존재해야 하는 반려지시서
```

## 필드 매핑 규칙 (동의어 허용)

입력 필드명이 정확히 일치하지 않아도 아래 동의어 군으로 매칭한다. 매칭이 실패하면
추측하지 말고 `[Data unavailable]`로 표시한 뒤 3단계 처리 절차(아래)를 따른다.

| Canonical 필드 | 허용 동의어 예시 |
|---|---|
| `ticker` | 종목코드, code, symbol, 티커 |
| `passed_companies` | 통과기업, survivors, final_candidates, 검증통과 |
| `rejection_memo` | 반려지시서, 반려보고서, rejection_report, disqualification_memo |
| `tam` | market_size, 시장규모, TAM |
| `catalyst` | trigger, 촉매, upcoming_events |

## 누락 정보 처리 순서 (절대 순서 고정)

```
Missing Information 발견
   → 임의로 채우지 않는다
   → 1) 추가 Research: 소스 우선순위(sourcing-and-anti-hallucination.md)에 따라
      직접 조사해서 채운다
   → 2) Verification: 조사한 값이 Fact/Estimate/Assumption 중 무엇인지 태깅하고,
      2개 이상 출처로 교차 확인 가능하면 확정
   → 3) 그래도 못 채우면: 리포트에 [Data unavailable] 또는 [Assumption required]로
      명시하고, 해당 항목이 결론에 미치는 영향을 한 줄로 설명한다
```

CASE D(0개 통과)에서 `rejection_memo`가 비어 있는 경우: Skill 1~3 원자료(개별 기업의
`reject_reasons`, `key_risks`)를 취합해 팀장이 직접 반려지시서를 재구성한다. 재구성했다는
사실을 리포트에 명시한다("Skill 3의 반려지시서가 제공되지 않아, 개별 기업 반려 근거를
종합하여 재구성함").

## 충돌 해결 규칙 — Skill 3 vs 팀장 독자 조사

팀장은 Skill 3를 그대로 승인하는 역할이 아니라 재검토자다. 독자 조사 결과가 Skill 3의
판단(통과/반려, 리스크 평가 등)과 다르면:

1. **팀장의 독립 조사 결과를 우선한다.**
2. 단, 반드시 리포트에 "Skill 3 판단과의 차이" 섹션을 넣어 **왜 뒤집었는지 근거를
   1문단 이상**으로 설명한다. 근거 없는 뒤집기는 금지.
3. 흔한 뒤집기 유형:
   - Skill 3 통과 기업을 팀장이 HOLD/NO INVESTMENT로 하향 → 대개 "이미 가격에 반영된
     기대" 또는 "Bear Case 감당 불가"가 근거
   - Skill 3 반려 기업을 팀장이 재검토해 다시 채택하는 것은 **원칙적으로 금지** —
     Skill 3의 검증 게이트를 팀장이 우회하면 파이프라인 전체의 신뢰도가 무너진다.
     반려 기업에 이견이 있으면 "다음 라운드 Skill 3 재검증 요청" 형태로만 남긴다.
