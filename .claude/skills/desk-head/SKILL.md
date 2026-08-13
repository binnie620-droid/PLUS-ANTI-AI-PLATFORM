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

## 출력 형식 — **HTML이 정본이다. md로 내지 않는다.**

최종 산출물은 `runs/<run_id>/report.html` 이다. 마크다운은 중간 산출물일 뿐이며,
투자위원회에 제출하는 것은 **읽을 수 있는 문서**여야 한다.

```
runs/<run_id>/report.html     ← 제출물. Artifact 로 발행한다
runs/<run_id>/04-tackle.json  ← 원장. Appendix 에 그대로 싣는다
```

### 판형·문체·Investment Point 구조는 `references/report-style.md` 가 정본이다

**보고서를 쓰기 전에 그 파일을 반드시 먼저 읽는다.**

> ⚠ **참조 구현(`runs/2026-08-13_전력기기/report.html`)에서 복사할 것은 CSS뿐이다.**
> 본문·수치·업종명을 복사하면 안 된다. `940억원` `6,976원` `40.0배` `데이터센터` 같은
> 문자열이 다른 업종 보고서에 남아 있으면 그 보고서는 폐기 대상이다.
> 발행 전 **업종명·종목명·수치를 전수 확인**한다. 초안이 Equity Research Report가
아니라 투자 아이디어 에세이로 나오는 실패가 반복됐고, 그 파일이 대응 규칙이다.

핵심 네 가지만 옮겨두면:

1. **구어체는 사이드노트와 IP 제목에만.** 소제목 `(1)(2)(3)`은 반드시 분석형
   (`Driver → 변화 → 영향`). 제목만 읽어도 Investment Logic이 보여야 한다
2. **Investment Point는 산업 이야기가 아니라 실적 드라이버다.**
   `Industry Driver → Company Exposure → KPI → Revenue/Margin → EPS → Target Price`
   연결고리를 갖추고, 각 IP에 정량 근거 2~3개를 넣는다
3. **기업이 N개면 IP도 N×3개다.** 산업분석만 공유하고 IP는 절대 공유하지 않는다.
   두 번째 기업부터 산업 서술은 `I장 참조`로 뺀다
4. **목표주가는 Target PER 유지 + EPS 상향으로 산출**한다. Multiple Re-rating을
   함부로 가정하지 않는다. IP에서 제시한 근거가 곧 EPS 상향 근거이며, 둘이
   일치하는지 검증한다

**Consensus vs DPIC View 표를 각 기업 장에 반드시 넣는다.**
**Top Pick은 Upside 단독이 아니라 Risk-adjusted Return 8개 항목으로 선정한다.**

### 문서 구조

문서 구성·색·조판 규칙이 그 파일에 있다. **매 회차 새로 설계하지 않는다.**
참조 구현: `runs/2026-08-13_전력기기/report.html`

```
P1   표지        assets/logo-dreamplus.png 중앙 + 편입 후보 세로 나열
P2   Contents
P3~  I. 산업분석        수요 구조 → 공급 구조(Peer Group)      ← 가장 자세히
P?~  II. 기업분석 A     산업 내 위치 → 사업구조 → 진입장벽 → 투자포인트 → Valuation → 리스크
P?~  III. 기업분석 B    동일 구조. 단 산업분석은 "I장 참조"로 뺀다
P?~  IV. 기업분석 C     (CASE A, 3개일 때만)
P?   최종장            포트폴리오 종합 — 상대비교 → 배분 → 운용규칙
```

**기업이 여러 개면 병렬로 세운다. 하나로 합치지 않는다.**
각 기업이 독립된 장을 갖고, 산업분석만 공유한다. 두 번째 기업부터는
산업 서술을 반복하지 말고 **Peer Group 내 위치**만 다룬다.

**표는 문서당 3~4개를 넘기지 않는다.** 심사표 전수·Q1~Q5 판정표·5종 공격 결과표는
**우리 채점 과정이지 독자가 볼 것이 아니다.** 판정 근거는 줄글로 푼다.

### 참고 — 일반 리서치 보고서 블록과의 대응

실제 리서치 보고서(40p 규모)의 장 구성을 우리 데이터에 매핑한다.
**분량을 맞추라는 뜻이 아니라 독자가 찾는 자리에 있어야 한다는 뜻이다.**

| # | 블록 | 우리 데이터 출처 | 없으면 |
|---|---|---|---|
| 1 | **표지 — Rating 블록** | 투자의견 / TP / 현재가 / 상승여력 / 기준일 | 필수 |
| 2 | Stock Information | 시총·52주 밴드·거래대금 (`data/price.csv`) | `[Data unavailable]` 명시 |
| 3 | **투자포인트 3개** | 인과 사슬의 P·M·R 을 3줄로 | 필수 |
| 4 | I. 산업분석 | `01-industry.json` — G1 게이트, 적격 종목 수, 평균 커버리지, FRED 매크로 | 필수 |
| 5 | II. 기업분석 | `02-companies.json` — `segment_top`, Q1~Q5 판정과 DART 인용 | 필수 |
| 6 | II-A. 주가분석 | 현재가 vs 컨센 TP vs 우리 TP 3점 비교 | 필수 |
| 7 | III. 투자포인트 상세 | 인과 사슬 전개 + 공시 인용 원문 | 필수 |
| 8 | IV. 리스크 | 미해결 항목 + 반증 조건 | 필수 |
| 9 | **V. 매출·비용 추정** | **하지 않는다.** 아래 참조 | 대체 사유를 명시 |
| 10 | VI. Valuation | 컨센 TP → 조정률 → 우리 TP 산식 전개 + 시나리오 | 필수 |
| 11 | VII. Appendix | **심사표 전문** — 탈락 종목 포함 전수 | 필수 |
| 12 | 데이터 출처표 | 항목별 출처와 실호출 여부 | 필수 |

### 9번(매출·비용 추정)을 하지 않는 이유를 반드시 밝힌다

원본 리포트는 분량의 절반 이상을 P×Q 추정과 DCF에 쓴다. **우리는 그걸 대체한다.**

```
원본   매출 P×Q 추정 → FCFF → WACC → DCF → 목표주가
우리   컨센 TP (FnGuide N개사) × (1 + 조정률)
```

**애널리스트보다 재무모델을 잘 만들 수 없다.** 우리가 잘하는 것은 그들이 안 본 것을
반영해 그 숫자를 밀거나 당기는 것이다. 이 문장을 리포트 VI장에 그대로 싣는다 —
안 밝히면 "추정을 안 했다"로 읽히고, 밝히면 "설계 선택"이 된다.

### HTML 작성 규칙

**스타일은 `references/report-style.md` 를 따르고, CSS는 참조 구현
(`runs/2026-08-13_전력기기/report.html` 의 `<style>` 블록)을 그대로 복사한다.**
디자인을 매번 새로 짜지 않는다 — 데스크 산출물은 종목이 달라도 같은 얼굴이어야 한다.

**DPIC 메인 컬러는 주황(`#F26522`)이다.** 단 본문 텍스트에는 쓰지 않고 구조 요소에만
쓴다 — 챕터 제목·사이드노트 세로선·BUY 배지·표 헤더·페이지 하단 바.
**상승 적색 / 하락 청색**(한국 관행)을 지킨다.

**로고는 `assets/logo-dreamplus.png` 를 base64 인라인**으로 넣는다.
외부 기관 로고나 클럽명은 절대 쓰지 않는다 — 판형 참고와 사칭은 다르다.

**사이드노트를 반드시 쓴다.** 각 문단 왼쪽에 결론 한 줄을 붙이고,
**사이드노트만 위에서 아래로 읽어도 논리가 완성**되어야 한다. 속독 독자를 위한 장치다.
명사구가 아니라 문장으로 쓴다 — "리스크"가 아니라 "계약 1건에 논리가 걸려 있다".


- **자체 완결**: 외부 CSS·폰트·스크립트 금지. 인라인으로 넣는다
- **라이트/다크 양쪽**: `:root` 에 라이트 토큰, `@media (prefers-color-scheme: dark)` 로 재정의.
  `body` 에 배경색을 명시하지 않으면 다크에서 글자가 안 보인다
- **표는 `overflow-x: auto` 컨테이너 안에** — 좁은 화면에서 페이지가 가로로 밀리면 안 된다
- **숫자는 `font-variant-numeric: tabular-nums`** — 자릿수가 맞아야 표로 읽힌다
- **`[FACT]`/`[ESTIMATE]`/`[ASSUMPTION]` 태그를 시각적으로 구분** — 색이나 배지로.
  이게 anti-hallucination 규칙의 가시적 구현체다
- **탈락 종목을 숨기지 않는다.** Appendix 심사표에 전수를 싣는다 —
  "5개 중 3개를 골랐다"는 증거가 안 되지만 "2개를 이 사유로 죽였다"는 증거가 된다

## Quality Gate

보고서를 확정하기 직전, `references/quality-gate-checklist.md`의 체크리스트를 전부
통과해야 한다. 하나라도 미충족이면 확정하지 말고 해당 부분을 보완한 뒤 재검사한다.
