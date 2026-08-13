# DPIC Equity Research — Report Writing Logic

`report.html` 작성 규칙. **판형·문체·Investment Point 구조가 전부 여기 있다.**
매 회차 새로 설계하지 않는다.

**참조 구현**: `runs/2026-08-13_전력기기/report.html`
CSS는 그 파일의 `<style>` 블록을 그대로 복사한다.

---

## 0. 이 문서가 존재하는 이유

초안이 **Equity Research Report가 아니라 투자 아이디어 에세이**로 나왔다.
제목이 광고 카피였고, Investment Point가 산업 서사 3개였으며, 목표주가가 실적과
연결되지 않았다. 아래 규칙은 그 실패에서 나왔다.

---

## 1. 제목 위계 — 구어체를 쓸 수 있는 자리는 두 곳뿐이다

```
III. 투자포인트 1                              ← 장 번호. 고정 형식
    북미 데이터센터 수주 확보에 따른 매출 성장 가시성   ← IP 제목: 분석형 권장
    (1) 업종 내 유일하게 수주가 계약으로 확인된 기업    ← 소제목: 반드시 분석형
      [기대감이 아닌 계약서로 말한다]                ← 사이드노트: 구어체 허용
```

| 자리 | 문체 | 예 |
|---|---|---|
| 장 제목 | 고정 | `I. 산업분석` |
| 장 부제 | **분석형** | `AI 데이터센터 확대로 송·배전 설비 수요의 구조적 성장 전망` |
| IP 제목 | **분석형** | `단일 사업 구조에 기반한 높은 실적 전이율` |
| 소제목 `(1)(2)(3)` | **분석형 필수** | `제한적 생산능력 증설에 따른 Seller's Market 지속 전망` |
| **사이드노트** | **구어체 허용** | `팔 사람보다 살 사람이 많다` / `컨센서스가 아직 안 넣은 숫자` |

### 분석형 제목의 구조

```
Driver → 변화 → 기업/산업 영향
```

```
✕  AI는 결국 전기를 먹는다
○  AI 데이터센터 확대로 전력기기 수요의 구조적 성장 전망

✕  팔 사람보다 살 사람이 많다              ← 사이드노트로 내리면 OK
○  제한적 생산능력 증설에 따른 Seller's Market 지속 전망

✕  시장의 시선이 얕은 곳에 기회가 남는다
○  제한적 Analyst Coverage에 따른 Valuation Re-rating 가능성
```

**제목만 읽어도 Investment Logic이 보여야 한다.**

---

## 1-5. DPIC Investment Framework — 보고서 초반에 반드시 밝힌다

**이 데스크는 10~15년 보유를 전제한다.** 컨센서스 목표주가는 대조 기준선이지
보유기간이 아니다. 이 차이를 보고서 앞부분에서 밝히지 않으면 일반 리서치와
구분되지 않는다.

표지 다음, 업종 선정 논리가 시작되기 전에 **짧은 섹션 하나**를 넣는다.
장황한 방법론 설명이 아니라 **단정적인 문장 3~4개**다. 기존 사이드노트 문법을 그대로 쓴다.

```
[우리는 1년 뒤보다 10년 뒤를 본다]
    DPIC Investment Framework
    일반 리서치가 향후 1~2년의 실적과 목표주가에 집중한다면, DPIC는 기업을
    10~15년 보유한다는 관점에서 본다. 현재의 실적 개선이 아니라 장기간 이익을
    키울 수 있는 구조적 원인이 존재하는지를 판단한다.

[AI 수혜가 아니라 지속기간을 본다]
    AI가 매출·비용·경쟁우위를 어떻게 바꾸는지, 그리고 그 효과가 몇 년 동안
    지속될 수 있는지를 함께 분석한다. 크기보다 지속기간과 누적 효과를 중시한다.
```

### 두 축을 혼동하지 않는다

```
컨센 델타 · Q1~Q5     진입 판단 — 시장이 지금 틀린 곳인가       12M 기준선
long_term · ai_impact  보유 판단 — 10~15년 뒤 이익이 더 큰가     DPIC 고유
```

**Investment Horizon을 `24개월`로 쓰지 않는다.** 목표주가 도달 시점과 보유기간은
다르다. 목표주가는 12M 컨센 기준선에서 산출하되, **보유 전제는 10~15년**임을 명시한다.

### Long-Term Lens — Top Picks에 짧게 표기

큰 표를 만들지 않는다. 종목별로 네 줄이면 충분하다.

```
10~15Y Earnings   구조적 성장
AI Impact         Positive (Revenue) / Neutral (Cost·Moat)
AI Duration       5~10년 — 데이터센터 증설 사이클
핵심 근거          데이터센터 전력수요 + 고객 전환비용 기반 진입장벽
```

AI가 중요하지 않은 기업이면 `Limited Impact`로 적는다. **억지로 AI 논리를 만들지 않는다.**

### 기업 장마다 Long-term earnings test를 반영한다

`산업 성장 → 경쟁우위 → 매출 → 마진/ROIC → 장기 이익` 인과가 성립하는지 서술한다.
**TAM 성장만으로 장기 성장기업이라고 쓰지 않는다.**

특히 **가격 결정력의 출처**를 구분한다. 공급 부족 같은 일시적 수급에서 나온 가격
결정력은 증설과 함께 사라진다 — 이것을 장기 이익 근거로 쓰면 안 된다.

### AI 주장은 증거 수준을 표기한다

```
disclosed   AI 관련 매출·수주·CAPEX·R&D·고객 도입 사례가 공시에 있음
inferred    사업 구조로부터 추론. 공시 근거 없음 — 반드시 추정임을 밝힌다
```

`AI로 생산성이 높아질 것이다` `AI 수혜가 예상된다` 같은 표현은 근거가 아니다.
**Narrative와 Evidence를 구분한다.**

---

## 2. Investment Point — 산업 이야기 3개가 아니다

각 IP는 독립적으로 다음에 답한다.

> **왜 이 기업의 Earnings와 Valuation이 시장 기대치를 상회하는가**

IP 3개를 모두 읽으면 **Target Price의 Upside가 왜 발생하는지** 설명되어야 한다.

### 필수 연결고리

```
Structural / Industry Driver
   ↓
Company-specific Exposure          ← 그 수요가 왜 이 회사로 오는가
   ↓
Quantifiable KPI                   ← 수주액 · Backlog · Capacity · ASP
   ↓
Revenue / Margin Impact
   ↓
Earnings Estimate Impact           ← EPS 몇 % 상향인가
   ↓
Valuation Implication              ← 목표주가
```

**&ldquo;AI 데이터센터가 성장한다&rdquo;에서 끝나면 Investment Point가 아니다.**

### IP 3개의 역할 분담 (기본형 — 기계적으로 적용하지 않는다)

| | 역할 |
|---|---|
| **IP 1** | Structural Growth — 시장의 구조적 성장과 회사의 노출도 |
| **IP 2** | Company-specific Earnings Driver — 수주·Capacity·Mix·Margin |
| **IP 3** | Earnings Surprise / Re-rating Catalyst — Consensus 미반영 요소 |

기업마다 가장 중요한 3개를 **새로 선정**한다. 위 틀은 출발점이지 정답이 아니다.

### 정량 근거 필수

각 IP에 **최소 2~3개의 숫자**가 있어야 한다. 후보:

```
TAM · CAGR · Order Intake · Backlog · Book-to-Bill · Capacity · Utilization
ASP · Market Share · Revenue Growth · Margin · CAPEX · EPS Growth · ROIC
Consensus Difference
```

Narrative만으로 IP를 쓰지 않는다.

---

## 3. Consensus vs Our View — 매 IP마다

단순히 좋은 산업·좋은 기업을 설명하는 것은 투자보고서가 아니다.
각 기업 장에 **반드시 이 표를 넣는다.**

| 구분 | Market Expectation | DPIC View | 차이 발생 근거 |
|---|---|---|---|
| 북미 수요 | 중장기 성장 전망 반영 | 동일 | 차이 없음 |
| 데이터센터 수주 | 추정치 반영 제한적 | 940억원 수주 반영 | 공시가 컨센 갱신 직전 |
| Target PER | 40.0배 | 40.0배 유지 | 금리 상승, Re-rating 미가정 |
| **12M Fwd EPS** | **6,976원** | **8,449원 (+21.1%)** | 수주 매출 인식 반영 |

답해야 할 네 질문:
```
What does the market already know?
What is our differentiated view?
Why could consensus be wrong?
What changes the earnings estimate?
```

**&ldquo;차이 없음&rdquo; 행을 숨기지 않는다.** 전 항목이 다르다고 쓰면 신뢰를 잃는다.

---

## 4. Valuation — Target PER 유지 + EPS 상향

**Multiple Re-rating을 함부로 가정하지 않는다.** 특히 금리 상승 국면에서는 금지에 가깝다.

```
Consensus 목표 PER  =  Consensus 목표주가 ÷ Consensus 12M Fwd EPS
DPIC EPS 추정       =  Consensus EPS × (1 + 상향률 × 매크로 계수)
목표주가            =  Consensus 목표 PER × DPIC EPS 추정
```

- **상향률의 근거는 IP에서 나온다.** IP에서 제시한 수주·Capacity·Mix가 곧 EPS 상향 근거다
- **IP의 가정과 Valuation의 EPS가 일치하는지 반드시 검증**한다
- EPS 상향률별 **민감도 표**를 넣는다 (0% / +10% / Base / +30%)
- Bear Case = EPS 상향 미실현. 이때도 Consensus 목표주가가 남는다

### 쓰지 말아야 할 서술

```
✕  "9개 증권사가 만든 추정치를 앵커로 쓴다"
✕  "애널리스트보다 재무모델을 잘 만들 수 없다"
     → 곧 "우리는 분석하지 않았다"로 읽힌다

○  "시장 컨센서스의 목표 PER을 유지한 상태에서 EPS 추정치 상향을 반영해 산출했다"
○  "금리 상승 국면을 감안해 Multiple Re-rating은 가정하지 않았다"
```

**우리가 무엇을 안 했는지가 아니라 무엇을 더 봤는지를 쓴다.**

---

## 5. 기업이 여러 개일 때

### 산업분석은 공유, Investment Point는 절대 공유하지 않는다

```
I.   산업분석                    ← 공통. 가장 자세히
II.  기업분석                    ← 기업 개요·KPI 비교 (공통 표)
III. 투자포인트 — 기업 A          ← A만의 IP 1·2·3
IV.  투자포인트 — 기업 B          ← B만의 IP 1·2·3
V.   Valuation                  ← 양사 병렬
VI.  Top Pick 선정               ← Cross-company Comparison
```

**&ldquo;전력기기 산업의 Investment Point 1~3&rdquo;만 쓰면 안 된다.**
기업 3개면 IP가 9개다.

두 번째 기업부터 **산업 서술을 반복하지 않는다.** Peer Group 내 위치만 다루고
`I장 참조`로 뺀다.

### Top Pick 선정 — Upside 단독 기준 금지

동일 잣대 8개 항목으로 비교한다.

```
Earnings Growth · Earnings Visibility · Valuation · Upside Potential
Catalyst 명확성 · Downside Risk · Market Expectation 격차 · AI 구조적 노출
```

**Upside가 가장 높다고 Top Pick이 되지 않는다. Risk-adjusted Return으로 판단한다.**
순위가 갈린 이유를 표로 보여준다.

---

## 6. 페이지 구성 — Key Message → Evidence → Data → Implication

에세이처럼 길게 서술하지 않는다. 한 페이지에서 즉시 보여야 하는 것:

```
1. 이 페이지가 주장하는 것          ← 소제목
2. 이를 증명하는 데이터             ← 표 · 인용 · 수치
3. 실적에 미치는 영향               ← 문단 마지막
```

긴 Text보다 **Chart · Table · Timeline · Peer Comparison**을 우선한다.
표는 문서당 **6~8개**가 적정하다. 3개 이하면 근거가 부족하고, 12개를 넘으면 산만하다.

**내부 채점 표는 싣지 않는다.** 심사표 전수·Q1~Q5 판정표·공격 결과표는 우리 채점
과정이지 독자가 볼 것이 아니다.

---

## 7. 표지

```
INDUSTRY REPORT · <업종>
<분석형 제목 — Driver → 영향>
<부제 — 보조 논리>

Coverage Initiation
[매수]  종목명 티커 / 한 줄 근거          목표주가 / 상승여력
[매수]  종목명 티커 / 한 줄 근거          목표주가 / 상승여력

주석 — 투자기간, 목표주가 산출 방식
```

```
✕  "모두가 전망을 말할 때, 수주를 보여준 곳"
○  "AI 데이터센터 투자 확대에 따른 전력기기 수요의 구조적 성장"
```

**Rating / Current Price / Target Price / Upside / Investment Horizon**이 명확히 보여야 한다.
`최선호주 / 차선호주`만 쓰고 끝내지 않는다 — 근거는 VI장 표에서 정량으로 제시한다.

---

## 8. 문체

### 금지 / 최소화

```
~인 셈이다        ~라는 얘기다      ~인 자리다       ~이 먼저 막혔다
~을 먹는다        ~을 보여준 곳     우리가 고른 이유   우리가 택한 근거
팔 사람이 없다     시장이 아직 모른다
```

### 사용

```
~할 것으로 전망           ~에 따른 수혜 예상        ~가 지속될 것으로 판단
~를 기반으로 실적 성장 전망  ~로 인한 수익성 개선 예상
~가 Valuation Re-rating의 Catalyst로 작용할 전망
~가 Consensus에 충분히 반영되지 않은 것으로 판단
```

### 내부 용어 → 리서치 문어

| 채점 용어 | 보고서 표현 |
|---|---|
| 편입 1위 / 2위 | Top Pick / 매수 |
| 인과 무결 | 수주 확보 · 실적 가시성 |
| 세그먼트 집중 97.4% | 영업이익의 97.4%가 전기사업에서 발생 |
| 승률 0.45 | (삭제) → Earnings Visibility로 서술 |
| 조정률 +25% | EPS 추정치 상향 +21% |
| 매크로 게이트 0.85 | 금리 상승 국면 감안한 보수적 조정 |
| L4 (제조) | 설비 기반 제조업 |
| 이익 귀속 절반 방어 | 이익 귀속이 부분적으로 확인 |
| 상투어 감점 | Consensus에 이미 반영된 논리 |

**우리 채점 어휘가 보고서에 새어나가면 안 된다.**

---

## 9. 금지 요약

| 금지 | 이유 |
|---|---|
| 외부 기관 로고·클럽명 | 판형 참고와 사칭은 다르다. 로고는 `assets/logo-dreamplus.png` |
| 소제목에 구어체 | 사이드노트와 IP 제목에만 허용 |
| 산업 서사를 IP 3개로 | IP는 실적 드라이버지 이야기가 아니다 |
| 기업 여러 개인데 IP 공유 | 기업마다 별도 IP 1·2·3 |
| Multiple Re-rating 가정 | 금리 상승 국면에서 특히. EPS 상향으로 설명 |
| "추정치를 앵커로 쓴다" 류 서술 | "우리는 분석 안 했다"로 읽힌다 |
| Upside 단독 Top Pick 선정 | Risk-adjusted Return 기준 |
| Investment Horizon 을 24개월로 표기 | 데스크 전제는 10~15년 보유. 목표주가 시점과 보유기간은 다르다 |
| TAM 성장만으로 장기 성장기업 판정 | 산업 성장 → 경쟁우위 → 매출 → 마진 → 장기 이익 인과 필요 |
| 일시적 수급에서 나온 가격 결정력을 장기 근거로 사용 | 증설과 함께 사라진다 |
| AI가 중요하지 않은 기업에 AI 서사 부여 | Limited Impact 도 유효한 판정 |
| 공시 근거 없는 AI 주장을 단정적으로 서술 | evidence_level 을 inferred 로 표기 |
| 내부 채점표 게재 | 독자가 볼 것이 아니다 |
| 상승에 녹색 | 국내 관행은 상승 적색 / 하락 청색 |
| 본문 텍스트를 주황으로 | 구조 요소에만 (`#F26522`) |
| 외부 폰트·CSS·스크립트 | 자체 완결. 로고는 base64 인라인 |
