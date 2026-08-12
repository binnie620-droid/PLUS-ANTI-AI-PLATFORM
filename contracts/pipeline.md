# 파이프라인 계약

> **4명이 각자 브랜치에서 만든 스킬이 머지될 때 서로 안 맞는 것**이 이 프로젝트의 최대 위험이다.
> 스킬끼리 직접 부르면 한 명만 늦어도 전체가 멈춘다.
> **그래서 파일로 주고받는다.**

---

## 원칙

```
각 단계는 앞 파일을 읽고 다음 파일을 쓰기만 한다.
스킬이 다른 스킬을 직접 호출하지 않는다.
```

이러면 이런 성질이 생긴다.

| 상황 | 결과 |
|---|---|
| B 스킬이 아직 없다 | `01-industry.json`을 **손으로 만들면** C부터 돈다 |
| C 스킬이 아직 없다 | 보고서를 직접 넣으면 D가 돈다 |
| 나중에 B가 올라온다 | 그 파일을 **자동 생성**하게만 바꾸면 끝. 뒷단은 손 안 댐 |
| 중간에 실패했다 | 그 파일부터 **재개** 가능 |

**누가 언제 올라오든 연동된다.**

---

## 실행 폴더 구조

```
runs/<run_id>/
├─ 00-input.md          사용자 요청 (자유 형식)
├─ 01-industry.json     ← B  산업 스크린
├─ 02-companies.json    ← C  기업 판정
├─ 03-valuation.json    ← A  조정률·TP·델타
├─ 04-tackle.json       ← D  pro_tackler 심사
└─ report.md            최종 산출물
```

`run_id` 형식: `YYYY-MM-DD_<산업명>` (예: `2026-08-13_농업`)

---

## 01-industry.json — B 산출

```json
{
  "run_id": "2026-08-13_농업",
  "mode": "verify",
  "selected_industry": "농업",
  "industries": [
    {
      "name": "농업",
      "consensus_universe_count": 7,
      "gate": "PASS",
      "reason": "커버리지 3~5곳 구간, 물질·현장 기반으로 Q1이 명확히 NO",
      "expected_direction": "UP",
      "answerable_questions": ["Q1", "Q2", "Q3", "Q5"]
    }
  ],
  "peers": [
    { "ticker": "000010", "name": "가나농산", "market_cap_bn": 4200 },
    { "ticker": "000011", "name": "다라농기", "market_cap_bn": 3900 },
    { "ticker": "000012", "name": "마바종묘", "market_cap_bn": 3600 }
  ]
}
```

| 필드 | 필수 | 쓰는 곳 |
|---|---|---|
| `mode` | ✓ | `discover` / `verify` |
| `consensus_universe_count` | ✓ | **5 미만이면 gate REJECT** (G1) |
| `gate` | ✓ | `PASS` / `REJECT` |
| `expected_direction` | ✓ | `UP` / `DOWN`. DOWN이면 ☠ 함정 후보 산업 |
| `peers` | ✓ | **M3 동종 3사 비교군.** 심사 대상 자신은 제외해서 넣을 것 |

---

## 02-companies.json — C 산출

**두 가지 형식을 모두 허용한다.** 구조화된 Q1~Q5 답변, 또는 서사형 보고서 경로.
둘 다 있어도 되고, 보고서만 있어도 D가 처리한다.

```json
{
  "run_id": "2026-08-13_농업",
  "industry": "농업",
  "judged_count": 14,
  "companies": [
    {
      "ticker": "000010",
      "name": "가나농산",
      "answers": { "Q1": false, "Q2": true, "Q3": true, "Q4": false, "Q5": true },
      "evidence": {
        "Q2": {
          "quote": "당사는 사료관리법상 제조업 등록과 HACCP 인증을 보유하고 있으며 신규 설비 구축에 통상 3년이 소요됩니다",
          "source": "2025 사업보고서 II.사업의 내용 p.14"
        }
      },
      "segment_top": {
        "name": "배합사료 제조",
        "op_share": 0.72,
        "source": "2025 사업보고서 II.사업의 내용 p.12"
      },
      "report_md": "runs/2026-08-13_농업/reports/000010.md"
    }
  ]
}
```

| 필드 | 필수 | 쓰는 곳 |
|---|---|---|
| `answers` | 둘 중 하나 | A의 조정률 계산 |
| `report_md` | 둘 중 하나 | D의 서사형 심사 |
| `evidence` | YES인 항목만 | **인용 없으면 A의 코드가 NO로 강제** |
| `segment_top` | ✓ | **D의 M1(AI 잠식) 판정 입력.** 없으면 M1 보류 → L3 처리 |

> `segment_top.op_share`는 **매출이 아니라 영업이익 비중**이다.
> 매출 비중밖에 없으면 `"basis": "revenue"`를 붙여 명시할 것.

---

## 03-valuation.json — A 산출

```json
{
  "run_id": "2026-08-13_농업",
  "macro": { "G": 0.85, "basis": "미 10년 실질금리 3개월 +32bp — 황색" },
  "companies": [
    {
      "ticker": "000010",
      "adjust_rate": 0.35,
      "top_question": "Q3",
      "consensus_tp": 32000,
      "our_tp": 41520,
      "delta": 0.2975,
      "price": 28000,
      "upside": 0.4829,
      "coverage_count": 5,
      "last_updated": "2026-05-12",
      "turnover_20d_bn": 3.2,
      "flags": []
    }
  ]
}
```

| 필드 | 쓰는 곳 |
|---|---|
| `G` | FRED 매크로 게이트. **조정률 > 0 일 때만 적용** |
| `top_question` | 팀장의 분산 규칙 (최대 기여 질문 중복 배제) |
| `consensus_tp` · `coverage_count` · `last_updated` | **D의 Phase 4 컨센 게이트 입력** |
| `flags` | `"컨센 미확보"` `"규모 미기재"` 등 |

> **`consensus_tp`가 비면 D의 컨센 게이트가 돌지 않는다.**
> 이 파이프라인에서 가장 자주 비는 필드이므로 `flags`에 반드시 표기할 것.

---

## 04-tackle.json — D 산출 (pro_tackler)

```json
{
  "run_id": "2026-08-13_농업",
  "table": [
    {
      "ticker": "000010",
      "name": "가나농산",
      "F1": "PASS",
      "F2": "PASS",
      "M1": { "level": "L4", "basis": "배합사료 제조 — 영업이익 72% (사업보고서 II p.12)" },
      "causal_breaks": 1,
      "break_detail": "고리②: 필요≠충분",
      "M2": "UP",
      "M3": 2,
      "M4_penalty": 0,
      "win_rate": 0.45,
      "upside": 0.4829,
      "expected_return": 0.2173,
      "verdict": "편입 1위",
      "reason": null
    }
  ],
  "picks": ["000010"],
  "trap_candidates": ["000013"],
  "rejection_notice": null
}
```

| 필드 | 비고 |
|---|---|
| `M1.level` | `L1`~`L5`. **L1·L2는 즉사** |
| `causal_breaks` | **고리 단위**로 센다. 공격 단위가 아니다 |
| `M2` | `UP`/`FLAT`/`DOWN`. **점수 아님** — 함정 매트릭스 축 |
| `M4_penalty` | 0/1/2 감점. 상투어 판정에는 **근거 명시 의무** |
| `win_rate` | `0.55 − 0.10 × (인과 끊김 + M4 감점 + 규모 미기재)` |
| `verdict` | `편입 N위` / `반려` / `☠ 함정` |
| `trap_candidates` | 팀장이 **하향 판단 후보**로 쓴다 |
| `rejection_notice` | **`picks`가 비었을 때만** 채운다 |

---

## report.md — 최종

팀장이 쓴다. `README.md` §7 팀장 형식을 따른다.

```
편입 3종목 (또는 그 이하)
  각각: 인과 사슬 · M1~M4 근거 · 현재가/컨센TP/우리TP · 델타

배분 비중          A 40% / B 35% / C 25%
금액 기대수익       1억 배분 시 +1,700만원
청산 규칙          재심사에서 인과 끊김 2개 이상 → 매도
고객 유형          공격형 / 안정형
심사표             04-tackle.json 의 table 을 그대로 붙인다
```

---

## 계약 위반 시

**다음 단계로 넘기지 않고 멈춘다.** 억지로 진행하면 뒤에서 조용히 틀린 값이 나온다.

```
필수 필드 누락        → 어느 파일 어느 필드인지 지목하고 정지
gate REJECT          → 정지. 사유를 사용자에게 전달
picks 0개            → rejection_notice 작성 후 정지
consensus_tp 전부 없음 → 경고 후 진행하되 report.md에 "델타 미산출" 명시
```
