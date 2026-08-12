# Output Schema

사람이 읽는 리포트 본문과 별도로, 매 실행 결과 맨 끝에 아래 구조화 블록을 **항상**
붙인다. 목적: 다른 팀원의 코드/도구가 결과를 기계적으로 파싱할 수 있게 하고, 이후
포트폴리오 재검토나 대시보드화에 재사용 가능하게 하는 것.

```json
{
  "case": "A | B | C | D",
  "as_of": "YYYY-MM-DD",
  "companies": [
    {
      "name": "string",
      "ticker": "string",
      "decision": "BUY | HOLD | SELL | NO_INVESTMENT",
      "priority_rank": 1,
      "current_price": 0,
      "target_price": 0,
      "target_price_formula": "string (e.g. Forward EPS x Target P/E)",
      "valuation_methods_used": ["DCF", "EV/EBITDA"],
      "upside_pct": 0.0,
      "investment_horizon": "6M | 12M | 18M | 24M | 3Y+",
      "bull_case_tp": 0,
      "base_case_tp": 0,
      "bear_case_tp": 0,
      "thesis_breaking_trigger": "string",
      "overturned_skill3_verdict": false,
      "overturn_reason": "string | null"
    }
  ],
  "industry_context": {
    "industries_referenced": ["string"],
    "no_investment_reason": "string | null"
  },
  "final_decision_sentence": "string (SKILL.md 포맷 그대로)",
  "quality_gate_passed": true,
  "quality_gate_notes": ["항목별 미비점이 있었다면 무엇을 보완했는지"]
}
```

## CASE별 채움 규칙

- **CASE D**: `companies`는 반드시 빈 배열 `[]`. `industry_context.no_investment_reason`
  필수. 개별 기업 관련 필드(target_price 등)는 존재해선 안 된다.
- **CASE C**: `companies` 배열에 정확히 1개 원소, `priority_rank`는 생략 가능(null).
- **CASE B**: 2개 원소, `priority_rank` 1(Top Pick)/2(Second Pick).
- **CASE A**: 3개 원소, `priority_rank` 1/2/3. 3개 모두 `decision`이 BUY일 필요 없음.
- `overturned_skill3_verdict: true`인 경우 `overturn_reason`은 null이 될 수 없다
  (`input-normalization.md`의 충돌 해결 규칙).
