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

## When to Use

- **discover**: "AI 수혜/피해 산업 추천해줘", no specific industry named.
- **verify**: any teammate names an industry directly ("농업", "조선기자재", ...).
- Do **not** use for individual stock judgment (that's Skill 2 / `moat-scorer`).
- Do **not** use to produce a target price or compute the FRED macro gate `G`
  (that's `core/macro.py`, owned by A — see FRED section below for why this skill
  only *reads* FRED, never *decides* with it).

## Gate Logic — the only judgment this skill makes

Run these four steps **in this order** — the DART sanity pass happens *before* G1 is
finalized, because it can shrink the qualifying ticker count:

**Step 1 — build the candidate set.** Join `data/industry_universe.csv` (`industry,ticker,name`)
to `data/consensus.csv` (ticker→coverage_count). Candidates = tickers in this industry
with `coverage_count >= 3`.

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

Run Steps 1–4 for every industry present in `data/industry_universe.csv`, then:
1. Drop every industry that failed Step 3 (G1).
2. Rank survivors per the sweet-spot heuristic and tie-break rule.
3. Return the top 3 (fewer if fewer than 3 pass).
4. `selected_industry: null`, `peers: []` — no single industry has been chosen yet, so
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

## DART calls (공시 확인 — Step 2, supplementary)

Requires `DART_API_KEY` env var (register at opendart.fss.or.kr). Purpose: confirm
candidate tickers are live filers (not delisted/suspended) before G1 is computed, and
support the `answerable_questions`/`reason` text for Q5 — thin, slow-updating coverage
usually shows up as low disclosure frequency too. **This is a sanity/context check, not
a citation source** — DART citations for individual Q1–Q5 YES answers are Skill 2's
job (`moat-scorer`), not this skill's.

1. **corp code lookup (once, cache it):**
   `GET https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={DART_API_KEY}`
   Returns a zip of `corp_code / corp_name / stock_code / modify_date` for every DART
   filer. Cache the ticker→corp_code mapping locally (e.g.
   `data/dart_corp_codes.csv`, gitignored) — do not refetch per run.

2. **disclosure recency, sampled (not exhaustive):**
   `GET https://opendart.fss.or.kr/api/list.json?crtfc_key={DART_API_KEY}&corp_code={corp_code}&bgn_de={YYYYMMDD}&end_de={YYYYMMDD}&page_count=100`
   For up to 5 sampled tickers per industry, count disclosures in the trailing 90 days.
   Zero disclosures across a 2-year window on a sampled ticker means it's likely
   delisted/suspended — drop it from the candidate set (this can flip Step 3's G1 from
   PASS to REJECT if it drops the count below 5 — that's intended, not a bug).

## FRED calls (거시 맥락 — Step 4, read-only)

Requires `FRED_API_KEY` env var. Purpose: attach macro context to `reason`, purely
informational. **A's `core/macro.py` owns the actual FRED-derived gate `G`** used in
target-price adjustment — this skill must not compute or output a competing `G` value,
just cite context in prose.

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
(e.g. `2026-08-13_농업`), **and** return the same JSON to the caller.

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
  "_macro_context": { "sector_series": ["PWHEAMTUSDM","PMAIZMTUSDM"], "universal_series": ["DEXKOUS","DGS10"], "as_of": "2026-07" }
}
```

`_dart_check` and `_macro_context` are **not** part of the pipeline contract — they're
underscore-prefixed diagnostic fields for the desk to eyeball, and downstream parsers
must ignore unknown keys. Never let their absence or content change `gate`.

`discover` mode: same top-level shape, `mode: "discover"`, `selected_industry: null`,
`industries` holds up to 3 items (each with the same per-item fields as above), `peers: []`.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Ranking industries by a point total | There is no industry score. PASS/REJECT + sweet-spot rank only. |
| Recommending already-crowded industries (robotics, semis, data centers) | Clear G1 easily but avg coverage >= 10 — rank last, say so in `reason`. |
| Dropping trap (Q1-YES) industries because they're "bad news" | Keep them, `expected_direction: "DOWN"`. A desk with only UP picks isn't credible. |
| Computing/outputting a FRED-derived `G` value here | That's `core/macro.py` (A). This skill only cites FRED in prose. |
| Inventing a `market_cap_bn` number with no source | Use the fallback order above; `null` + `_note` beats a fabricated figure. |
| Calling DART `list.json` for every ticker in a large industry | Sample up to 5. Sanity check, not a census. |
| Renaming `industries`/`peers`/`consensus_universe_count` to match your own taste | C and D already parse these exact names. Renaming breaks the pipeline silently. |
| Writing prose instead of JSON to `runs/<run_id>/01-industry.json` | Downstream reads the file programmatically — prose breaks the pipeline. |

## Do Not

- Score industries (no point total, no weighted average).
- Recommend more than 3 industries in `discover`.
- Include unlisted/non-DART-registered industries.
- Mention a target price or valuation multiple anywhere in the output.
- Judge an individual company (Skill 2's job — this stops at the industry).
- Cite DART filings as Q1–Q5 evidence for a specific company (Skill 2's job).

## Completion Definition

Input: `"농업"` (verify mode). Output: `runs/2026-08-13_농업/01-industry.json` matching
the schema above — `consensus_universe_count`, `gate` (+ `reason` if REJECT),
`answerable_questions`, `expected_direction`, and (if PASS) 3 `peers` — cross-checked
against DART for candidate survivorship, with FRED context cited in `reason` when
relevant.
