# Report Structure Templates

전 CASE 공통 컨벤션(두산에너빌리티 보고서에서 예외 없이 관찰된 규칙, 최소 기준으로
채택):

- **모든 차트/표 하단에 출처를 표기한다**: `자료: [기관/공시명], [팀명] 리서치팀`.
  desk-head가 스스로 계산한 표는 `자료: [원 데이터 출처], desk-head 추정`으로 표기.
- 각 챕터 도입부에 **1~2줄짜리 Key Message**(무엇을 보여주려는 챕터인지)를 먼저 제시한 뒤
  본문 서술로 들어간다.
- 서술은 "~로 판단된다/추정된다"처럼 근거를 흐리는 표현 자체를 금지하지는 않되, 그
  뒤에는 반드시 구체적 근거(숫자·공시·계약)가 따라와야 한다. 근거 없는 판단 서술은
  `sourcing-and-anti-hallucination.md`의 금지 대상이다.

---

## CASE A (3개 기업) / CASE B (2개 기업) — 통합 투자보고서 구조

```
0. Cover Summary Block
   - Rating: [BUY/HOLD/SELL/NO INVESTMENT] × N개 기업 각각
   - 기업별: 목표주가 / 현재주가 / 상승여력(%) / 기준일자 / Investment Horizon
   - 1문단: 왜 이 산업·이 기업들인지 핵심 논리 요약
   - 1·2위(A) 또는 Top/Second Pick(B) 한 줄 선언

1. Contents (챕터·페이지 목차)

2. AI 구조적 변화 & 산업 선정 논리
   - Skill 1의 6개 산업 중 이 산업(들)이 최종까지 남은 이유
   - 산업 성장 논리, TAM/CAGR, AI와의 관계 (research-and-forecast-protocol.md 기준)

3. 후보 기업 비교 (Skill 2 → Skill 3 압축 요약)
   - 산업별 5개 후보 중 이 N개가 왜 살아남았는지 1개 표로 요약

4. 기업별 상세 분석 (기업마다 반복, 두산 보고서의 II.기업분석+II-A.주가분석 대응)
   4-1. Business Model / Revenue Driver / Competitive Position / Market Share
   4-2. 경쟁사 비교 (Peer 목록과 비교 기준)
   4-3. (선택) 주가 히스토리 — 과거 주가를 움직인 이벤트를 시기별로 주석

5. 기업별 투자포인트 (기업마다, 3~5개 Investment Point)
   - independent-review.md의 5단 연결고리 템플릿을 그대로 채운 형태
   - 매 Point마다 뒷받침하는 수치·계약·공시 인용

6. 기업별 리스크 & Bull/Base/Bear (scenario-and-risk.md 기준)

7. 기업별 매출·비용 추정 & Earnings Table (research-and-forecast-protocol.md 기준)

8. 기업별 Valuation & Target Price (valuation-protocol.md 기준 — 계산식·WACC·민감도 포함)

9. 기업별 Investment Horizon & Catalyst Timeline (horizon-and-catalyst.md 기준)

10. 기업 간 투자매력도 비교 (case-branching.md의 비교표)

11. Portfolio 관점 (Catalyst/리스크 중복도)

12. 최종 투자 판단
    - CASE A: 1위/2위/3위 + 개별 BUY/HOLD/SELL/NO INVESTMENT
    - CASE B: Top Pick/Second Pick + 개별 등급
    - 기업별 Final Decision 한 줄 문장 (SKILL.md 포맷)

13. Appendix (세부 추정 backup 테이블, 가정 목록)

14. Output Schema 블록 (output-schema.md 형식)
```

---

## CASE C (1개 기업) — Single-Stock Investment Report 구조

```
0. Cover Summary Block
   - Rating: BUY/HOLD/SELL/투자보류 (자동 BUY 아님을 리포트 서두에 명시:
     "Skill 3 통과 여부와 무관하게 독립 재검토 결과")
   - 목표주가/현재주가/상승여력/기준일자/Investment Horizon

1. Contents
2. 산업 선정 논리 (해당 산업만, 요약)
3. 기업 상세 분석 (Business Model/Revenue Driver/Competitive Position/Market Share/경쟁사)
4. Investment Point (3~5개, 5단 연결고리)
5. 더 나은 대체 투자처 검토 (case-branching.md CASE C 요건 — 단일종목이라도 진공비교 금지)
6. 리스크 & Bull/Base/Bear
7. 매출·비용 추정 & Earnings Table
8. Valuation & Target Price (계산식·WACC·민감도)
9. Investment Horizon & Catalyst Timeline
10. Final Decision (한 줄 문장)
11. Appendix
12. Output Schema 블록
```

---

## CASE D (0개 통과) — Industry Outlook Report 구조 (개별 기업 챕터 전면 금지)

**이 템플릿에는 기업 챕터, Valuation 챕터, Target Price가 존재하지 않는다.** 있다면
Skill 4가 규칙을 위반한 것이다. 12개 항목을 그대로 목차로 쓴다:

```
0. Cover Summary
   - Final Decision: NO INVESTMENT (산업 차원)
   - 1문단 결론 요약: 예) "산업의 장기 성장성은 유효하지만, 현재 valuation 및
     risk/reward를 고려하면 투자 가능한 종목은 없다."

1. AI 시대의 구조적 변화
2. Skill 1에서 선정된 산업 (해당 산업 개요)
3. 산업별 성장 논리
4. AI와 산업의 관계
5. TAM / 성장률 / 수요 Driver
6. 산업별 경쟁구조
7. 산업별 Risk
8. 기업들이 탈락한 이유
   - Skill 3의 반려지시서를 원문 또는 재구성해서 반영 (input-normalization.md 참조)
   - 기업별로 어떤 Independent Review 질문(1~10)에서 걸렸는지 매핑하면 좋음
9. 현재 시점에서 투자하지 않는 이유
10. 향후 투자 가능성이 생길 조건
11. Monitoring Indicator (무엇을 계속 지켜봐야 하는가)
12. 향후 재검토해야 할 Trigger (구체적 조건문 — scenario-and-risk.md의
    Thesis-Breaking Trigger와 반대 방향: "이게 바뀌면 재검토를 시작한다")

13. Final Decision: NO INVESTMENT (한 줄, SKILL.md 포맷)
14. Output Schema 블록 (companies: [] 빈 배열, decision: "NO_INVESTMENT")
```
