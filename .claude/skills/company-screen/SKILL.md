---
name: company-screen
description: 산업 하나를 받아 그 산업의 컨센서스 보유 종목 전체를 전수 판정한다. 종목마다 moat-scorer 에이전트를 호출해 Q1~Q5 예/아니오 + DART 인용을 모으고, industry/judged_count/companies 스키마로 JSON을 낸다. 상위 종목을 미리 추리지 않는다 — 정렬·조정률 계산은 core(A)의 몫이다. "기업 판정", "company screen", "산업 지정" 경로에서 skill 1/1.5 PASS 이후 요청에 사용.
---

# Company Screen — Skill 2 (기업 판정)

이 데스크의 차별성이 전부 여기서 만들어진다. 산업 하나를 받아 그 산업에서 **컨센서스가 있는 종목을 전수** 판정한다. 순위를 매기지 않는다 — [[moat-scorer]]로 Q1~Q5만 채우고, 정렬·조정률·목표주가 계산은 `core/`(A)의 몫이다.

**첫 실행 예시**: "농업 산업 기업 판정해줘" / `python -m core.run --industry "농업"` 경로 안에서 자동 호출

## 입력

- `industry`: skill 1/1.5가 PASS로 넘긴 산업명
- 산업 내 종목 목록 — 아래 우선순위로 확보한다:
  1. 호출자(팀장/오케스트레이터)가 ticker 리스트를 직접 준 경우 그대로 쓴다
  2. `data/industry_universe.csv`에 종목 단위 열(`industry,ticker,name`)이 있으면 그 산업으로 필터한다
  3. 둘 다 없으면 판정을 시작하지 않는다. "산업→종목 매핑이 없다"고 보고한다 — 이건 B와 맞출 데이터 계약이지, C가 임의로 채우거나 지어낼 데이터가 아니다.
- `data/consensus.csv`에서 각 ticker의 `last_updated`를 가져와 Q5 입력으로 넘긴다. `consensus.csv`에 없는 ticker는 판정 대상에서 제외하고 사유를 남긴다 (G1 게이트 — 컨센서스 없는 종목은 애초에 대상이 아니다).

## 절차

1. 산업의 전체 종목 리스트를 위 규칙대로 확보한다.
2. **상위 종목을 미리 고르지 않는다.** 시총·거래대금 등으로 사전 필터링하지 않고, 컨센서스가 있는 종목 전부를 대상으로 삼는다. 정렬은 A의 `core/select.py`가 한다.
3. 종목마다 [[moat-scorer]] 에이전트를 호출한다. 입력: `ticker`, `name`, `industry`, `consensus_last_updated`.
4. 결과를 모아 아래 고정 스키마로 하나의 JSON을 만든다.
5. 종목 수가 많으면(10개 이상) 중간 진행 상황을 알린다 — 조용히 오래 도는 것보다 낫다.

## 출력 스키마 (고정 — `core/adjust.py`가 그대로 파싱한다. 임의로 바꾸지 않는다)

```json
{
  "industry": "농업",
  "judged_count": 14,
  "companies": [
    {
      "ticker": "000000",
      "name": "○○○",
      "answers": { "Q1": false, "Q2": true, "Q3": true, "Q4": false, "Q5": true },
      "evidence": {
        "Q2": {
          "quote": "당사는 사료관리법상 제조업 등록과 HACCP 인증을 보유하고 있으며 신규 설비 구축에 통상 3년이 소요됩니다",
          "source": "2025 사업보고서 II.사업의 내용 p.14",
          "durability": "structural"
        }
      },
      "long_term": {
        "verdict": "structural_growth",
        "basis": ["면허 기반 진입장벽", "영업레버리지 — 인건비 매출 대비 7%"],
        "risk": "가격 결정력이 공급 부족에 기대 증설 시 약화 가능",
        "quote": "...", "source": "..."
      },
      "ai_impact": {
        "revenue": "positive", "cost": "neutral", "moat": "neutral",
        "duration": "5-10y", "pattern": "persistent",
        "duration_basis": "데이터센터 증설 사이클 기간. 설비 증설 리드타임이 공급을 제약",
        "evidence_level": "disclosed", "quote": "...", "source": "..."
      }
    }
  ]
}
```

- `answers`는 boolean(`true`/`false`)만 쓴다. `"YES"/"NO"` 문자열 금지.
- `evidence`는 `true`인 질문의 키만 담는다. `false`인 질문은 `evidence`에 키 자체를 만들지 않는다.
- `durability`(`"structural"`/`"temporary"`)는 **Q1·Q2에만** 붙는다. moat-scorer가 채운다 — company-screen은 그대로 옮긴다.
- `judged_count`는 판정을 시도한 종목 수(컨센서스 없어서 제외한 종목은 포함하지 않음)와 `companies` 배열 길이가 일치해야 한다.
- 저장 위치: `data/company_scores/<industry>.json` (예: `data/company_scores/농업.json`)

## 장기 관점 — 이 데스크는 10~15년을 본다

**컨센서스 목표주가는 대조 기준선이지 보유기간이 아니다.** Q1~Q5는 "지금 시장이
틀렸는가"를 묻지만, 편입 여부는 "10~15년 뒤에도 이 이익이 있는가"로 결정된다.
두 축이 따로 있다.

```
Q1~Q5 + 컨센 델타     진입 판단 — 시장이 지금 틀린 곳인가        (12M 기준선)
long_term + ai_impact  보유 판단 — 10~15년 뒤 이익이 더 큰가      (DPIC 고유)
```

그래서 moat-scorer는 Q1~Q5 외에 **두 블록을 항상 채운다.** 상세 판정 기준은
`moat-scorer.md` 에 있으며, company-screen은 그대로 옮기기만 한다.

| 블록 | 묻는 것 | 핵심 필드 |
|---|---|---|
| `long_term` | 10~15년 뒤 이익이 구조적으로 커지는가 | `verdict` (structural_growth / flat / erosion / undetermined) |
| `ai_impact` | AI가 매출·비용·해자를 어떻게 바꾸는가, **얼마나 오래** | `revenue` `cost` `moat` `duration` `pattern` `evidence_level` |

### 오케스트레이터가 강제할 것

- **`long_term`·`ai_impact` 키가 없는 종목은 판정 미완료로 처리**한다. Q1~Q5만 있고
  이 둘이 없으면 D가 장기 판단을 할 수 없다
- **TAM 성장만으로 `structural_growth`를 주지 않는다.** `산업 성장 → 경쟁우위 →
  매출 → 마진/ROIC → 장기 이익` 인과가 basis에 있어야 한다
- **AI가 중요하지 않은 기업에 억지로 AI 논리를 만들지 않는다.** 전 축 `neutral` +
  `duration: null` 도 유효한 판정이다. 무리한 AI 서사가 오히려 신뢰를 깎는다
- **`quote`가 없으면 `evidence_level`은 반드시 `inferred`.** Narrative를 Evidence로
  올리지 않는다

## 절대 규칙 (moat-scorer와 동일 — 오케스트레이터 레벨에서 한 번 더 강제)

- **인용 없으면 false.** `evidence.quote`가 20자 미만이거나 금지어(`업계 통념상` `일반적으로` `~로 알려져 있다` `~로 판단된다` `~일 것으로 보인다`)를 포함하면 그 질문을 `answers`에서 `false`로 되돌리고 `evidence`에서 그 키를 지운다. (최종 방어선은 A의 `core` 코드지만, 여기서 한 번 걸러야 관통 테스트가 빠르다.)
- **종목 하나가 실패해도 전체를 멈추지 않는다.** DART 접근 불가 등으로 판정을 못 하면 그 종목은 5문항 전부 `false` + `evidence` 없음으로 기록하고 넘어간다 — "근거를 못 찾았다"는 이 프로젝트에서 `NO`와 같은 뜻이다.
- **전수 판정이 끝나기 전까지 어떤 종목도 "유망하다/탈락"으로 언급하지 않는다.** 이 스킬은 판정만 한다, 선정은 하지 않는다.
- **상위 종목을 먼저 정하고 답을 맞추지 않는다.** 역방향 오염이며, 발생하면 조정표 전체가 장식이 된다.

## 하지 말 것

- 종목 사전 필터링·순위 매기기
- 조정률·목표주가 계산
- 뉴스·리포트·IR을 근거로 인정
- 판정 실패 종목을 조용히 리스트에서 빼기 (반드시 `judged_count`에 포함하고 사유를 남긴다)
- 산업→종목 매핑이 없는데 임의로 종목을 골라서 판정 시작하기

## 완료 정의

산업명 하나를 넣으면 그 산업의 컨센서스 보유 종목 전체가 Q1~Q5 판정과 (`true`인 항목의) DART 인용을 담은 JSON으로 나온다. 근거를 못 찾은 항목은 자동으로 `false`다.

## 블록 1(스키마 고정)에서 B·A와 확인해야 할 것

- `data/industry_universe.csv`가 종목 단위(`industry,ticker,name`)까지 담는지, 아니면 산업별 개수만 담는지 B와 맞춘다. 개수만 담는 스키마라면 이 스킬은 종목 리스트를 받을 방법이 없다 — 팀장/skill1 쪽에서 ticker 리스트를 직접 넘기는 경로를 대신 열어야 한다.
- `data/consensus.csv`의 `last_updated` 날짜 포맷(예: `2026-06-30`)을 A와 통일한다 — Q5 판정에서 날짜 비교에 그대로 쓴다.

## A·D에게 제안 — 10~15년 홀딩 관점을 담는 방법

이 데스크는 12개월 컨센 TP를 앵커로 쓰지만, 실제 투자는 10~15년 홀딩을 전제로 한다. 10~15년짜리 목표주가는 만들지 않는다 — 그러려면 DART로 인용 불가능한 성장률·할인율 가정이 필요해서, "인용 없으면 NO"라는 이 데스크의 근간과 충돌한다. 대신 Q1·Q2가 `true`일 때 `evidence.durability`(`structural`/`temporary`)를 이미 붙여서 넘긴다.

이걸 실제로 쓰려면 A·D 쪽에서 결정할 일이 남아있다 (C가 임의로 core/select.py나 desk-head를 건드리지 않는다):
- **하드컷으로 쓸지**: 조정률의 최대 기여 질문이 `temporary`면 "10~15년 보유 후보"에서 빼고 "단기 트레이딩 후보"로만 분류할지 — 최대 기여 질문 판별은 이미 A의 코드가 한다.
- **V1(프론티어랩 진입)에 반영할지**: FAIL 조건을 "장벽이 구조적이지 않아 수년 내 무너질 수 있음"으로 좁혀서, `durability=structural`인 Q2 YES는 V1이 더 엄격하게, `temporary`는 그대로 두는 식.
- **청산 규칙에 한 줄 추가할지**: "구조적 가정이 깨지는 공시가 나오면 보유기간과 무관하게 즉시 재평가."

이 셋 다 숫자(TP 앵커·V1~V3 조건 값·손절/익절 %)는 안 바꾼다 — `durability` 필드를 어떻게 쓸지만 A·D가 정하면 된다.
