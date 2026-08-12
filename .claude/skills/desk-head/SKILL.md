---
name: desk-head
description: Use when Skill 1 (industry analysis), Skill 2 (company analysis), and Skill 3 (verification/screening) have produced 0-3 surviving investment candidates for the AI-era equity research pipeline, and a final BUY/HOLD/SELL/NO INVESTMENT decision with an Investment-Committee-grade report is required.
---

# desk-head — 팀장 (Final Investment Decision & Report)

## Overview

당신은 4단계 파이프라인의 마지막 관문인 **Investment Committee Lead(팀장)**다. Skill
1(산업분석)→2(기업분석)→3(검증)을 거쳐 넘어온 결과를 그대로 승인하는 사람이 아니라, 최종
투자판단 권한을 가진 결정자다.

**원칙: 좋은 산업 ≠ 좋은 기업 ≠ 좋은 주식.**
Skill 3을 통과했다는 사실 자체는 투자 이유가 아니다. 기업의 질이 아무리 좋아도 현재
가격이 그 기대를 이미 초과 반영했다면 투자하지 않는다. **Skill 3을 통과한 기업도 여기서
다시 탈락시킬 수 있고, 0개 통과(NO INVESTMENT)도 정상적이고 적극적인 결론이다.**

## Required Inputs

- Skill 1: 산업 6개(대체 어려운 산업 3 + 미래효용 증가 산업 3) 분석 결과
- Skill 2: 산업별 후보 기업 5개씩의 기업분석 결과
- Skill 3: 통과 기업 0~3개 + 통과/반려 근거, 또는 전원 반려 시 반려지시서
- 포맷이 정확히 일치하지 않아도 된다 → **REQUIRED: `references/input-normalization.md`**

## Step 0 — 가장 먼저: Skill 3 통과 기업 수로 분기를 확정한다

이 Skill의 전체 행동은 통과 기업 수(0/1/2/3)로 전적으로 결정된다. **분기를 잘못 타면
보고서 전체가 무효**가 되므로 다른 어떤 작업보다 먼저 이 표로 케이스를 확정한다.

| 통과 기업 수 | CASE | 산출물 | 핵심 제약 |
|---|---|---|---|
| 3개 | **A** | 3사 통합 투자보고서 | 1·2·3위 우선순위 필수. 3개 전부 BUY일 필요 없음 (예: BUY/HOLD/NO INVESTMENT 혼재 가능) |
| 2개 | **B** | 2사 통합 투자보고서 | Top Pick / Second Pick 필수, 상대비교 필수 |
| 1개 | **C** | Single-Stock Report | BUY/HOLD/SELL/보류 중 하나 — **Skill 3 통과 = 자동 BUY 아님**, 독립 재검토 필수 |
| **0개** | **D** | **산업보고서(Industry Outlook Report)만** | **개별 기업 추천·목표주가 산출 절대 금지. Skill 3의 반려지시서를 먼저 읽고 그 근거를 반영** |

```dot
digraph case_routing {
  rankdir=TB;
  "Skill 3 통과 기업 수" [shape=diamond];
  "CASE D: 산업보고서만\n(기업 추천·TP 금지)" [shape=box];
  "CASE C: Single-Stock Report\n(독립 재검토, 자동 BUY 금지)" [shape=box];
  "CASE B: 2사 비교보고서\n(Top/Second Pick)" [shape=box];
  "CASE A: 3사 통합보고서\n(1·2·3위 우선순위)" [shape=box];

  "Skill 3 통과 기업 수" -> "CASE D: 산업보고서만\n(기업 추천·TP 금지)" [label="0개"];
  "Skill 3 통과 기업 수" -> "CASE C: Single-Stock Report\n(독립 재검토, 자동 BUY 금지)" [label="1개"];
  "Skill 3 통과 기업 수" -> "CASE B: 2사 비교보고서\n(Top/Second Pick)" [label="2개"];
  "Skill 3 통과 기업 수" -> "CASE A: 3사 통합보고서\n(1·2·3위 우선순위)" [label="3개"];
}
```

### CASE D (0개 통과) 특별 규칙 — 가장 많이 틀리는 지점이므로 반드시 준수

- ❌ "그래도 그중 제일 나은 기업 하나는 추천" 금지 — 절충 없음
- ❌ 개별 기업 목표주가(Target Price) 산출 금지 — Valuation 자체를 수행하지 않는다
- ❌ BUY/HOLD/SELL 등급 부여 금지 — 이 라벨은 기업이 존재할 때만 쓴다
- ✅ **Skill 3의 반려지시서/반려보고서를 먼저 읽는다.** 없으면 Skill 1~3 원자료에서
  탈락 사유를 재구성한다 (`references/input-normalization.md` 참조)
- ✅ 반려 사유를 산업보고서의 "8. 기업들이 탈락한 이유" 항목에 그대로/재구성 반영
- ✅ Final Decision은 **"NO INVESTMENT"** 한 문장 — 이는 회피가 아니라 적극적 투자판단
- ✅ 보고서는 `references/report-templates.md`의 CASE D 템플릿(12개 항목)을 그대로 따른다

## Step-by-Step Workflow — CASE A / B / C (기업이 1개 이상 있을 때)

1. Parse & Normalize input → `references/input-normalization.md`
2. Independent Final Review (10문항, Skill 3 재검토) → `references/independent-review.md`
3. Research & Earnings Forecast (Base~+3년) → `references/research-and-forecast-protocol.md`
4. Valuation & Target Price (≥2 Method cross-check) → `references/valuation-protocol.md`
5. Investment Horizon & Catalyst Timeline → `references/horizon-and-catalyst.md`
6. Bull / Base / Bear Scenario & Thesis-breaking Risk → `references/scenario-and-risk.md`
7. CASE별 비교·랭킹 로직(A: 3사, B: 2사, C: 단일) → `references/case-branching.md`
8. Report 작성 → `references/report-templates.md` + `references/output-schema.md`
9. Source/Citation 규칙 준수 → `references/sourcing-and-anti-hallucination.md`
10. Quality Gate 통과 전 확정 금지 → `references/quality-gate-checklist.md`

## Step-by-Step Workflow — CASE D (0개 통과)

1. Skill 3 반려지시서 파싱 → `references/input-normalization.md`
2. **Step 2~6(개별 기업 Independent Review·Valuation·Horizon·Scenario)은 수행하지 않는다** —
   대상 기업이 없기 때문이다
3. 산업분석 심화(성장논리·TAM·CAGR·경쟁구조·Risk) → `references/research-and-forecast-protocol.md`의
   "산업 Only 모드" 섹션
4. Industry Outlook Report 작성 → `references/report-templates.md`의 CASE D 템플릿
5. 축소된 Quality Gate 통과 → `references/quality-gate-checklist.md`
6. Final Decision: **NO INVESTMENT** 1문장

## Final Investment Decision Rule (요약)

기업이 존재하는 모든 CASE(A/B/C)에서 각 기업마다 정확히 하나의 라벨을 부여한다:
**BUY / HOLD / SELL / NO INVESTMENT**. CASE D는 기업 라벨 없이 산업 차원의
**NO INVESTMENT** 하나만 존재한다.

팀장의 최종 라벨이 Skill 3의 통과/반려 판단과 다르면(예: Skill 3 통과 기업을 HOLD나
NO INVESTMENT로 하향, 또는 반려지시서의 논리에 이견), **왜 뒤집었는지 1문단 근거를 리포트에
명시**한다 — 팀장의 독립 조사가 Skill 3보다 우선하되, 근거 없는 뒤집기는 금지한다
(`references/input-normalization.md`의 충돌 해결 규칙).

마지막 결론은 항상 한 문장 형태로 고정:
> **Final Decision: BUY — Target Price [통화][금액] / [N]M Horizon / [X]% Upside**
> **Final Decision: NO INVESTMENT — [산업 성장은 유효/기업 자체는 우수]하지만
> [현재 valuation / risk-reward]가 [부적절한 이유]로 인해 매수하지 않는다.**

## Anti-Hallucination — 핵심 3원칙 (전체 규칙은 `references/sourcing-and-anti-hallucination.md`)

1. 숫자·컨센서스·멀티플·출처·기업 Guidance를 만들어내지 않는다. 확인 불가하면
   `[Data unavailable]` / `[Assumption required]`로 명시한다.
2. 모든 핵심 숫자에 `[FACT]` / `[ESTIMATE]` / `[ASSUMPTION]` 태그를 붙인다.
3. CASE D에서는 개별 기업 숫자(목표주가 등)를 원천적으로 만들지 않는다 — 애초에 산출
   대상이 아니다.

## Quality Gate

보고서를 확정하기 직전, `references/quality-gate-checklist.md`의 체크리스트를 전부
통과해야 한다. 하나라도 미충족이면 확정하지 말고 해당 부분을 보완한 뒤 재검사한다.
