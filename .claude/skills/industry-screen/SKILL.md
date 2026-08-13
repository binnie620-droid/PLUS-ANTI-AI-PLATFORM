---
name: industry-screen
description: Use when picking or validating candidate industries for the PLUS FUTURE AI ANTI-PLATFORM desk, before Skill 2 (company-screen) runs — either no industry is named (recommend up to 3) or a teammate names one directly ("농업 검토해줘") and it must be verified against the same gate. Produces runs/<run_id>/01-industry.json per contracts/pipeline.md.
---

# Industry Screen (Skill 1 / 1.5)

## Overview

One file, two modes: **discover** (no industry named → recommend ≤3) and **verify**
(industry named → judge exactly that one). Both run the identical gate and emit the
identical `industries[]` item shape, because teammates from other desks always enter
through `verify` — if `verify` were looser than `discover`, the whole desk's gate would
be fake.

This skill does **not** score industries. There is no industry-level point total.
It answers: does the industry clear the coverage floor (PASS/REJECT), which of the
RULEBOOK's Q1–Q5 questions can even be answered for member companies of this industry,
which direction (UP/DOWN) it's expected to skew, and — for `verify` — which 3 peer
tickers company-level comparison (D's M3 test) should use.

**Downstream contract:** this skill's output is `01-industry.json` in the pipeline
defined by `contracts/pipeline.md` (falsify branch). Company-screen (C) reads the
selected industry name from it; desk-head/pro_tackler (D) reads `peers` for the M3
동종 비교 test. Field names below are copied verbatim from that contract — do not
rename them.

**No fixed universe.** There is no hand-picked CSV of "allowed" industries anymore.
`data/industry_cache.json` is an auto-growing record of what's been checked so far —
`tools/industry_cache.py` reads/writes it, `tools/dart_lookup.py` confirms new tickers
against DART before they're added. Any industry can be checked; the cache just remembers
what's already been verified so repeat runs don't re-pay the DART/FnSpace cost.

## When to Use

- **discover**: "AI 수혜/피해 산업 추천해줘", no specific industry named.
- **verify**: any teammate names an industry directly ("농업", "조선기자재", ...).
- Do **not** use for individual stock judgment (that's Skill 2 / `moat-scorer`).
- Do **not** use to produce a target price or compute the FRED macro gate `G`
  (that's `core/macro.py`, owned by A — see FRED section below for why this skill
  only *reads* FRED, never *decides* with it).

## Step -1 — API 키 확인 (항상 먼저)

이 스킬은 `DART_API_KEY`와 `FRED_API_KEY`가 **둘 다** 필요하다. 다른 어떤 단계보다
먼저 확인한다.

```bash
python tools/env_keys.py check
```

- exit 0 (`OK`) → Step 0으로 진행.
- exit 1 (`MISSING:...`) → 출력된 온보딩 메시지를 **그대로 사용자에게 채팅으로 보여주고**,
  키 값을 받는다. 받으면:
  ```bash
  python tools/env_keys.py save DART_API_KEY=<받은값> FRED_API_KEY=<받은값>
  ```
  (하나만 받았으면 받은 것만 저장 — 다음 `check`에서 나머지가 다시 물어짐)
- 사용자가 "없다/나중에"라고 답하면 — **abort한다.** JSON을 만들지 않고, 어떤 키가 없어서
  멈췄는지 명시한 뒤 대화를 종료한다. 저하된 모드로 부분 진행하지 않는다.

## Step 0 — 산업이 지정되지 않았으면 **반드시 먼저 물어본다**

호출 시점에 산업명이 주어지지 않았다면, **discover를 자동 실행하지 말고 사용자에게 되묻는다.**

```
"어느 산업을 보시겠습니까?

  ① 산업명을 직접 지정          → verify 모드 (예: "조선기자재", "폐기물처리")
  ② 데스크가 후보를 추천          → discover 모드

②를 고르시면 AI 고도화 테마로 업종을 가리지 않고 폭넓게 후보를 찾습니다
(제조업뿐 아니라 서비스·금융·컨설팅 등도 포함). 특정 산업을 염두에 두고
계시면 ①이 정확합니다."
```

**왜 물어야 하는가 — 안 물으면 데스크가 산업을 대신 고르게 된다.**
discover가 무엇을 후보로 떠올릴지는 브레인스토밍 시점의 판단이다. 사용자에게 묻지 않고
discover를 돌리면 그 판단이 숨겨진다.

`verify`가 정식 진입점이다 — 다른 팀 사람은 항상 자기 관심 산업을 들고 온다.

## 유니버스 구축 — 캐시 확인 → 없으면 DART로 확인 → 캐시에 추가

`verify`든 `discover`든, 후보 산업이 정해지면 그 산업의 종목 목록을 다음 순서로 얻는다:

```
1. 산업이 캐시에 이미 있는가?
     python tools/industry_cache.py get-industry "<산업명>"
     있다 → 그 tickers로 Step 1(candidate set)로 진행
     없다 → 2로

2. 후보 티커 각각에 대해 먼저 종목 단위 캐시를 확인한다 (다른 산업 아래 이미
   등록되어 있을 수 있다 — 회사는 여러 산업에 속할 수 있음):
     python tools/industry_cache.py get-company <ticker>
     있다 → 그 name/induty_code를 그대로 쓰고 4로 (DART 재호출 안 함)
     없다 → 3으로

3. 종목 캐시에도 없으면 DART로 실존/업종코드를 확인한다:
     python tools/dart_lookup.py induty-code <ticker>
   반환된 JSON의 corp_name을 그대로 <name>으로 쓴다 — Claude가 기억하는
   이름으로 임의로 바꾸지 않는다. induty-code가 종료코드 3(DART_ERROR)을
   반환하면 — 키 문제/rate-limit 등 실제 조회 실패이지 "종목 없음"이 아니다.
   이 경우 그 산업 전체를 REJECT 처리하지 말고 사용자에게 "DART 조회 실패,
   재시도 필요"라고 보고하며 중단한다. 종료코드 1(NOT_FOUND)일 때만 그
   티커를 후보에서 뺀다.

4. 확보한 name/induty_code로 캐시에 등록 (JSON의 `induty_code`가 `null`이면 `-`를
   넣는다 — `add-company`는 `-`를 "미상"으로 처리한다):
     python tools/industry_cache.py add-company <ticker> <name> <induty_code-or-"-"> "<산업명>"

5. 등록 후 Step 1(candidate set)로 진행
```

**verify에서 종목을 모를 때** — 사용자가 "농업" 같은 산업명만 주고 구성 종목을 안
줬으면, 이 스킬(Claude)이 일반 지식으로 그 산업의 대표 상장사 후보를 몇 개 떠올려서
위 2번으로 넘긴다. DART가 실존을 확인 못 하는 종목은 절대 임의로 지어내지 않는다 —
확인 안 되면 후보에서 뺀다.

**DART_API_KEY는 Step -1에서 이미 확인했으므로 여기서 없을 일은 없다.**

## Gate Logic — the only judgment this skill makes

Run these four steps **in this order** — the DART sanity pass happens *before* G1 is
finalized, because it can shrink the qualifying ticker count:

**Step 1 — build the candidate set.** From the industry's ticker list (cache or
freshly DART-confirmed, see above), get each ticker's consensus coverage.
Candidates = tickers with `coverage_count >= 3`.

### 커버리지 조회 경로는 두 가지다 — **먼저 어느 쪽이 가능한지 확인한다**

```
FnSpace MCP 도구가 이 세션에 로드돼 있는가?

  있다  →  mcp__plugin_fnspace_fnspace__get_target_price (또는 get_estimates) 를
           종목마다 호출한다. coverage_count 는 응답에서 컨센서스를 낸 기관 수다
           (필드명은 실제 호출 결과로 확인 — 항목 코드는 list_items(apigb="A000003"))

  없다  →  python tools/fetch_consensus.py <ticker> <ticker> ...
           수집 후 data/consensus.csv 의 coverage_count 를 쓴다
```

**미연결이 예외가 아니라 기본값이다.** 이 저장소를 clone하거나 플러그인으로 설치한
사람에게 FnSpace MCP는 없다. 구독 만료(2026-08-15 예정) 때도 같은 경로를 탄다.
**둘 중 어느 쪽도 안 되면 정지**하고 `tools/fetch_consensus.py` 실행을 안내한다 —
커버리지를 추정하거나 지어내지 않는다.

두 소스는 **모두 FnGuide가 공급하는 데이터**다. `fetch_consensus.py` 는 FnGuide
컨센서스를 네이버 금융 종목분석 페이지 경유로 읽는다. 우회가 아니라 **같은 출처의
다른 경로**이며, "FnGuide 컨센서스 필수 활용" 요건을 그대로 충족한다.

어느 경로를 썼는지 **출력의 `_coverage_source` 에 반드시 기록한다.** 두 소스는
갱신 시점이 달라 목표주가가 미세하게 어긋날 수 있고, 그때 원인을 추적하려면
어느 쪽을 읽었는지가 남아 있어야 한다.

진행상황을 짧게 출력한다: 종목을 조회할 때마다 "○○○ 컨센서스 확인 중..." 한 줄.

**Step 2 — DART sanity filter.** Sample up to 5 candidates and check they're active
filers (see DART section below). Drop any sampled ticker found dead (delisted/suspended)
from the candidate set. This step can reduce the candidate count — that's expected, it's
data cleaning, not a second gate.

**Step 3 — G1, coverage floor (hard cut).** After step 2, the industry **PASSES** only
if `consensus_universe_count >= 5` (tickers remaining in the candidate set). Fewer than
5 → **REJECT**, `reason` states `"coverage_below_5"` plus the actual count.

**Step 4 — FRED macro context (read-only, informational).** Attached only after the
PASS/REJECT decision. Never changes the Step 3 outcome.

**Sweet-spot heuristic (soft — ranks discover candidates, never overrides G1).**
- `consensus_universe_count` 3–5 tickers with `coverage_count` in the 3–9 range →
  ideal, comparison is possible and the industry isn't fully priced yet.
- avg `coverage_count` >= 10 across candidates → industry is "already_covered" (say so
  in `reason`). Industries like robotics, semiconductors, or data centers usually land
  here — they may still pass G1, but `discover` should rank them last since there's no
  information edge left.
- **Tie-break**: if two candidates land in the same band, prefer the one with more
  `answerable_questions`; if still tied, prefer a `trap_flag` (Q1-YES, DOWN) candidate
  over another UP candidate — the desk needs at least one hostile pick more than a
  second similar UP pick.

**Q-judgeability check (`answerable_questions`).** For each of Q1–Q5 below, state
whether the industry's *structure* lets the question be answered at all for its member
companies — e.g. a licensed/physical-asset industry makes Q1 answerable as a clean NO
before any single filing is read. List only the ones structurally answerable; Skill 2
still does the actual per-company YES/NO with DART citation.

| # | question |
|---|---|
| Q1 이익 대체성 | 영업이익의 50% 이상이 AI로 대체 가능한 인지노동에서 나오는가 |
| Q2 진입 장벽 | 면허·설비·실적 때문에 신규 경쟁자가 3년 내 진입 불가한가 |
| Q3 수요 연동 | AI 확산이 매출을 직접 늘리는 경로가 공시에 있는가 |
| Q4 원가 수혜 | AI로 낮출 수 있는 인건비·설계비가 매출의 10% 이상인가 |
| Q5 갱신 지연 | 컨센 최종 갱신일 이후 중요 공시(수주·실적·제도)가 있었는가 |

**`expected_direction`.** Exactly two rules, no other case exists:
- Core revenue is consulting/SI/translation/staffing/license-brokerage — i.e. Q1 is
  structurally likely YES for member companies — → `expected_direction: "DOWN"`
  (this is the ☠ trap case). Keep it as a valid candidate; do **not** discard it. The
  desk needs at least one hostile pick; discarding traps is a G4-style rationalization
  failure, not caution.
- Otherwise → `expected_direction: "UP"`. Default for every industry where Q1 is
  structurally NO — do not leave it blank or guess.

## Mode: discover

1. **폭넓게 브레인스토밍한다** — AI 고도화 테마와 관련성이 있어 보이는 산업을 업종을
   가리지 않고 20~40개 정도 떠올린다. **제조업/중공업에만 머물지 않는다** — 서비스업,
   컨설팅, 금융, 유통, 헬스케어, 인력파견 등도 반드시 포함한다. 이래야 Q1-YES 함정
   (☠) 후보가 나올 구조적 여지가 생긴다 (제조업·설비 기반 산업만 떠올리면 함정 후보가
   원천적으로 나올 수 없다 — 이게 예전 설계의 결함이었다).
2. 후보 산업마다 "유니버스 구축" 절차(위)로 종목을 확보하고, Steps 1–4를 실행한다.
   확인 없이 바로 진행하되, 산업을 하나씩 처리할 때마다 진행상황을 짧게 출력한다:
   "[3/25] 반도체장비 확인 중..." 같은 형식.
3. Drop every industry that failed Step 3 (G1).
4. Rank survivors per the sweet-spot heuristic and tie-break rule.
5. Return the top 3 (fewer if fewer than 3 pass).
6. `selected_industry: null`, `peers: []` — no single industry has been chosen yet, so
   there's nothing to build a peer group against. Once a teammate/orchestrator picks
   one of the 3, re-run in `verify` mode on that name to get the full record including
   `peers`.

## Mode: verify

Run Steps 1–4 for exactly the named industry. `industries` holds exactly one item.
`selected_industry` = that industry name. If REJECT, still fill in
`consensus_universe_count` and `reason` so the caller knows *why*, and set `peers: []`.
If PASS, populate `peers` (see below).

### Selecting `peers` (verify only, PASS only)

3 tickers from the candidate set, for D's M3 동종 3사 비교 test downstream. Rank
candidates by `coverage_count` descending (most-covered = most established/liquid name
in the industry) and take the top 3.

`market_cap_bn` **has no fixed data source yet** — it isn't in `data/consensus.csv` or
`data/price.csv` (see README §4). Best effort, in order:
1. If `data/market_cap.csv` exists (ticker,market_cap_bn), use it.
2. Otherwise try DART's 주식의총수현황 endpoint (`stockTotqySttus.json`, field
   `istc_totqy` — **verify the exact field name against current Open DART docs before
   relying on it, it may have changed**) × `price.csv` price, in units of 억원.
3. If neither works, set `market_cap_bn: null` for that peer and add a top-level
   `_note: "market_cap_bn 데이터 소스 미확정 — A/C와 데이터 계약 확인 필요"` so it's
   visible, not silently wrong. Do not invent a number.

The subject ticker that C/D later judge is **not** excluded here — B doesn't know which
single ticker will be selected yet. D excludes it at comparison time if it happens to
be one of the 3 (per `contracts/pipeline.md`).

## DART calls

Requires `DART_API_KEY` (already confirmed in Step -1).

1. **업종코드 조회 (유니버스 구축용, 이 스킬 전용 wrapper 사용):**
   ```bash
   python tools/dart_lookup.py induty-code <ticker>
   ```
   내부적으로 `corpCode.xml`(전체 상장사 목록)을 `data/dart_corp_codes.csv`에 한 번만
   캐싱한다 — 이 캐시는 티커→corp_code 매핑까지다. `company.json`(induty_code 조회)은
   호출될 때마다 실제로 요청이 나간다 — 반복 호출을 막는 건 이 스크립트가 아니라 한 단계
   위의 `data/industry_cache.json`이다 (유니버스 구축 절차의 2번, 종목 캐시 확인).

2. **disclosure recency, sampled (Step 2, sanity check only):**
   `GET https://opendart.fss.or.kr/api/list.json?crtfc_key={DART_API_KEY}&corp_code={corp_code}&bgn_de={YYYYMMDD}&end_de={YYYYMMDD}&page_count=100`
   For up to 5 sampled tickers per industry, count disclosures in the trailing 90 days.
   Zero disclosures across a 2-year window on a sampled ticker means it's likely
   delisted/suspended — drop it from the candidate set (this can flip Step 3's G1 from
   PASS to REJECT if it drops the count below 5 — that's intended, not a bug).
   **This is a sanity/context check, not a citation source** — DART citations for
   individual Q1–Q5 YES answers are Skill 2's job (`moat-scorer`), not this skill's.

## FnSpace calls (컨센서스 — Step 1, live)

FnSpace(FnGuide) MCP 도구를 **직접** 호출한다 — `data/consensus.csv`(A 소유, 배치성)를
거치지 않고 실시간 값을 쓴다. 처음 쓴다면 `mcp__plugin_fnspace_fnspace__quickstart`로
키 상태를 먼저 확인해도 좋다.

- `mcp__plugin_fnspace_fnspace__get_target_price` — 종목별 목표주가·투자의견 컨센서스.
- `mcp__plugin_fnspace_fnspace__get_estimates` — 추정실적 컨센서스(연간), 커버리지
  기관 수 판단의 보조 자료.

**유료 구독 만료 주의**: 2026-08-15 이후 위 두 도구가 응답하지 않을 수 있다. 만료된
것으로 보이면(에러 또는 빈 응답) 그 사실을 `_note`에 남기고, `data/consensus.csv`가
있으면 그걸로 폴백한다 — 조용히 값을 비우지 않는다.

**consensus.csv와 다를 수 있음**: 이 스킬이 쓰는 값은 실시간이라 A의 배치 파일
(`data/consensus.csv`)과 다를 수 있다. 이는 알려진 리스크다 — 값이 크게 다르면
`_note`에 남긴다.

## FRED calls (거시 맥락 — Step 4, read-only)

Requires `FRED_API_KEY` (already confirmed in Step -1). Purpose: attach macro context
to `reason`, purely informational. **A's `core/macro.py` owns the actual FRED-derived
gate `G`** used in target-price adjustment — this skill must not compute or output a
competing `G` value, just cite context in prose.

`GET https://api.stlouisfed.org/fred/series/observations?series_id={ID}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=13`
(trailing 13 months)

Always pull the two universal series: `DEXKOUS` (원/달러) and `DGS10` (미 10년물).
Plus a sector series if the industry matches this table (extend as needed — do not
invent a series ID that doesn't exist):

| industry keyword | series_id | proxy |
|---|---|---|
| 농업 / 사료 / 식품 | `PWHEAMTUSDM`, `PMAIZMTUSDM` | wheat / corn global price |
| 에너지 / 화학 / 정유 | `DCOILWTICO` | WTI crude |
| 해운 / 조선 | `DCOILWTICO` | fuel cost proxy (no direct BDI series on FRED) |

If no keyword matches, cite only the two universal series in `reason` (or omit macro
commentary entirely — it's optional color, not a required field).

## Output — `01-industry.json` (contracts/pipeline.md — do not rename fields)

Write to `runs/<run_id>/01-industry.json` where `run_id` = `YYYY-MM-DD_<산업명>`
(verify) or `YYYY-MM-DD_discover` (discover), **and** return the same JSON to the caller.

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
      "reason": "커버리지 3~5곳 구간, 물질·현장 기반으로 Q1이 명확히 NO. DART 표본 5종목 전원 최근 90일 내 공시 확인.",
      "expected_direction": "UP",
      "answerable_questions": ["Q1", "Q2", "Q3", "Q5"]
    }
  ],
  "peers": [
    { "ticker": "000010", "name": "가나농산", "market_cap_bn": 4200 },
    { "ticker": "000011", "name": "다라농기", "market_cap_bn": 3900 },
    { "ticker": "000012", "name": "마바종묘", "market_cap_bn": 3600 }
  ],
  "_dart_check": { "sampled_tickers": ["000010","000011","000012"], "active_filers": 3, "median_disclosures_90d": 3 },
  "_macro_context": { "sector_series": ["PWHEAMTUSDM","PMAIZMTUSDM"], "universal_series": ["DEXKOUS","DGS10"], "as_of": "2026-07" },
  "_universe_source": "data/industry_cache.json (auto-discovered via DART + FnSpace, not a fixed list)",
  "_coverage_source": "FnSpace MCP" 또는 "FnGuide via tools/fetch_consensus.py (FnSpace MCP 미연결)"
}
```

`_dart_check`, `_macro_context`, `_universe_source`, `_coverage_source`는
**파이프라인 계약이 아니다** —
언더스코어 접두 진단 필드이며, 다운스트림 파서는 모르는 키를 무시해야 한다. 이 필드들의
존재/내용이 `gate`를 바꾸지 않는다.

`discover` mode: same top-level shape, `mode: "discover"`, `selected_industry: null`,
`industries` holds up to 3 items (each with the same per-item fields as above), `peers: []`.

## 채팅 요약 — 용어 병기 + 다음 단계 유도

`01-industry.json`을 저장한 뒤, 채팅에는 표 요약과 함께 내부 용어를 쉬운 말로 병기한다:
- `G1` → "컨센서스 커버리지 최소 5종목 조건"
- `coverage_count` → "그 종목을 커버하는 애널리스트/기관 수"
- `expected_direction: DOWN` → "AI로 인한 하향 압력이 예상되는 함정 후보"

**항상 다음 단계 유도로 마무리한다** — 산업→기업→검증→팀장 흐름이 끊기지 않도록:
```
"이 중 하나를 골라 Skill 2(기업 판정, company-screen)로 넘길까요?"
```
(company-screen 자체의 로직은 이 스킬 범위 밖 — 유도 질문만 담당한다.)

## Common Mistakes

| Mistake | Fix |
|---|---|
| API 키 확인 없이 바로 진행 | **Step -1 위반.** 항상 `env_keys.py check`부터. 없으면 abort. |
| 산업명이 없다고 바로 discover를 실행 | **Step 0 위반.** 먼저 물어본다 — 안 물으면 데스크가 산업을 대신 고르게 된다. |
| discover에서 제조업/중공업만 브레인스토밍 | 서비스·금융·컨설팅 등도 반드시 포함 — 안 그러면 Q1-YES 함정 후보가 구조적으로 나올 수 없다. |
| 캐시에 없는 산업을 "목록에 없다"며 즉시 반려 | 유니버스 구축 절차(DART 확인 → 캐시 추가)를 먼저 시도한다. |
| Ranking industries by a point total | There is no industry score. PASS/REJECT + sweet-spot rank only. |
| Recommending already-crowded industries (robotics, semis, data centers) | Clear G1 easily but avg coverage >= 10 — rank last, say so in `reason`. |
| Dropping trap (Q1-YES) industries because they're "bad news" | Keep them, `expected_direction: "DOWN"`. A desk with only UP picks isn't credible. |
| Computing/outputting a FRED-derived `G` value here | That's `core/macro.py` (A). This skill only cites FRED in prose. |
| Inventing a `market_cap_bn` number with no source | Use the fallback order above; `null` + `_note` beats a fabricated figure. |
| Calling DART `list.json` for every ticker in a large industry | Sample up to 5. Sanity check, not a census. |
| Renaming `industries`/`peers`/`consensus_universe_count` to match your own taste | C and D already parse these exact names. Renaming breaks the pipeline silently. |
| Writing prose instead of JSON to `runs/<run_id>/01-industry.json` | Downstream reads the file programmatically — prose breaks the pipeline. |
| 결과만 보여주고 끝내기 | 항상 Skill 2로 넘길지 물어보며 마무리한다. |

## Do Not

- Score industries (no point total, no weighted average).
- Recommend more than 3 industries in `discover`.
- Include a ticker DART cannot confirm exists.
- Mention a target price or valuation multiple anywhere in the output.
- Judge an individual company (Skill 2's job — this stops at the industry).
- Cite DART filings as Q1–Q5 evidence for a specific company (Skill 2's job).
- Proceed without both `DART_API_KEY` and `FRED_API_KEY` confirmed.

## Completion Definition

Input: `"농업"` (verify mode). Output: `runs/2026-08-13_농업/01-industry.json` matching
the schema above — `consensus_universe_count`, `gate` (+ `reason` if REJECT),
`answerable_questions`, `expected_direction`, and (if PASS) 3 `peers` — cross-checked
against DART for candidate survivorship, with FRED context cited in `reason` when
relevant, and a chat summary ending in a Skill-2 handoff question.
