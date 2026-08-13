# industry-screen UX/유니버스 재설계 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `industry-screen` 스킬(Skill 1/1.5)이 (1) DART/FRED API 키를 채팅으로 온보딩하고, (2) 고정 CSV 대신 자동 성장하는 캐시 + DART/FnSpace 실시간 조회로 산업 유니버스를 만들고, (3) 진행상황을 보여주며 다음 스킬(company-screen)로 자연스럽게 이어지도록 만든다.

**Architecture:** 결정론적/네트워크 로직은 표준 라이브러리만 쓰는 작은 Python 헬퍼 스크립트(`tools/env_keys.py`, `tools/industry_cache.py`, `tools/dart_lookup.py`)로 빼서 유닛 테스트로 검증하고, `SKILL.md`는 이 헬퍼들을 Bash로 호출하는 오케스트레이션 지시문으로 재작성한다. FnSpace(FnGuide) 컨센서스 조회는 MCP 도구로만 접근 가능하므로 헬퍼 스크립트가 아니라 `SKILL.md`의 지시문으로 남긴다 (Claude가 실행 시점에 `mcp__plugin_fnspace_fnspace__get_target_price`/`get_estimates`를 직접 호출).

**Tech Stack:** Python 3.11 표준 라이브러리만 (csv, io, os, json, sys, zipfile, xml.etree.ElementTree, urllib.request, unittest.mock) — 기존 `tools/fetch_consensus.py`와 동일한 무의존성 스타일. 테스트는 `pytest` 미설치 상태이므로 표준 `unittest` 사용.

## Global Constraints

- `01-industry.json`의 필드명/스키마는 절대 바꾸지 않는다 (`contracts/pipeline.md` 계약).
- `data/consensus.csv`, `adapters/consensus.py`는 A 소유 — 이 계획에서 건드리지 않는다.
- `company-screen`/`pro_tackler`/`desk-head` 스킬의 판정 로직은 바꾸지 않는다 — 이번 계획은 `industry-screen`(B)만의 범위.
- `DART_API_KEY`/`FRED_API_KEY` 둘 중 하나라도 없으면 스킬은 즉시 abort한다 — 저하된 모드로 부분 진행하지 않는다.
- `data/industry_universe.csv`(고정 CSV)를 `data/industry_cache.json`(자동 성장 캐시)으로 대체한다 — 새 CSV를 만들지 않는다.
- 외부 pip 의존성을 추가하지 않는다 — 표준 라이브러리만 사용 (기존 `tools/fetch_consensus.py` 관례).
- `pytest`가 설치되어 있지 않으므로 표준 `unittest`로 테스트를 작성하고 `python <파일경로>` 또는 `python -m unittest`로 실행 가능하게 한다.

---

## File Structure

| 파일 | 역할 |
|---|---|
| `tools/env_keys.py` (신규) | `DART_API_KEY`/`FRED_API_KEY` 존재 확인, `.env` 저장, 온보딩 메시지 생성. CLI 겸용. |
| `tests/tools/test_env_keys.py` (신규) | 위 모듈의 유닛 테스트. |
| `tools/industry_cache.py` (신규) | `data/industry_cache.json` 읽기/쓰기/조회/추가. CLI 겸용. |
| `tests/tools/test_industry_cache.py` (신규) | 위 모듈의 유닛 테스트. |
| `tools/dart_lookup.py` (신규) | DART corpCode.xml 캐싱 + `company.json`으로 `induty_code` 조회. CLI 겸용. |
| `tests/tools/test_dart_lookup.py` (신규) | 위 모듈의 유닛 테스트 (HTTP는 fake fetcher로 모킹). |
| `tools/migrate_industry_cache.py` (신규) | 기존 `data/industry_universe.csv`(6산업/59종목)를 `data/industry_cache.json` 시드로 1회성 변환. |
| `tests/tools/test_migrate_industry_cache.py` (신규) | 위 스크립트의 유닛 테스트 (fixture CSV + fake fetcher). |
| `.claude/skills/industry-screen/SKILL.md` (수정) | 스킬 전체를 새 흐름으로 재작성 (키 온보딩, 캐시 기반 유니버스, discover 브레인스토밍, 진행상황/친절한 용어/파이프라인 유도). |
| `README.md` (수정) | §5 저장소 구조, §7 B 역할 설명에서 `industry_universe.csv` → `industry_cache.json` 반영. |
| `.gitignore` (수정) | `data/dart_corp_codes.csv`는 이미 gitignore 대상 — `data/industry_cache.json`은 **커밋 대상**이므로 gitignore에 추가하지 않는다 (기존 `industry_universe.csv`와 동일하게 팀 공유 자산). |

---

### Task 1: `tools/env_keys.py` — API 키 온보딩

**Files:**
- Create: `tools/env_keys.py`
- Test: `tests/tools/test_env_keys.py`

**Interfaces:**
- Produces:
  - `REQUIRED_KEYS: list[str]` = `["DART_API_KEY", "FRED_API_KEY"]`
  - `read_env_file(path: str) -> dict[str, str]`
  - `find_missing_keys(path: str, environ: dict | None = None) -> list[str]`
  - `save_keys(new_keys: dict[str, str], path: str) -> None`
  - `onboarding_message(missing: list[str]) -> str`
  - CLI: `python tools/env_keys.py check` (exit 0 + `OK`, 또는 exit 1 + `MISSING:K1,K2` + 온보딩 메시지)
  - CLI: `python tools/env_keys.py save K1=V1 K2=V2` (exit 0 + `SAVED:K1,K2`)

- [ ] **Step 1: Write the failing tests**

Create `tests/tools/test_env_keys.py`:

```python
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import env_keys


class TestEnvKeys(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.env_path = os.path.join(self.tmpdir, ".env")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_find_missing_keys_when_nothing_set(self):
        missing = env_keys.find_missing_keys(self.env_path, environ={})
        self.assertEqual(sorted(missing), ["DART_API_KEY", "FRED_API_KEY"])

    def test_find_missing_keys_reads_from_environ(self):
        missing = env_keys.find_missing_keys(
            self.env_path, environ={"DART_API_KEY": "abc"}
        )
        self.assertEqual(missing, ["FRED_API_KEY"])

    def test_find_missing_keys_reads_from_dotenv_file(self):
        with open(self.env_path, "w", encoding="utf-8") as f:
            f.write("DART_API_KEY=abc\nFRED_API_KEY=def\n")
        missing = env_keys.find_missing_keys(self.env_path, environ={})
        self.assertEqual(missing, [])

    def test_read_env_file_ignores_comments_and_blank_lines(self):
        with open(self.env_path, "w", encoding="utf-8") as f:
            f.write("# comment\n\nDART_API_KEY=abc\n")
        values = env_keys.read_env_file(self.env_path)
        self.assertEqual(values, {"DART_API_KEY": "abc"})

    def test_read_env_file_missing_file_returns_empty_dict(self):
        values = env_keys.read_env_file(os.path.join(self.tmpdir, "nope.env"))
        self.assertEqual(values, {})

    def test_save_keys_creates_file_and_round_trips(self):
        env_keys.save_keys({"DART_API_KEY": "abc"}, self.env_path)
        values = env_keys.read_env_file(self.env_path)
        self.assertEqual(values, {"DART_API_KEY": "abc"})

    def test_save_keys_preserves_existing_keys(self):
        env_keys.save_keys({"DART_API_KEY": "abc"}, self.env_path)
        env_keys.save_keys({"FRED_API_KEY": "def"}, self.env_path)
        values = env_keys.read_env_file(self.env_path)
        self.assertEqual(values, {"DART_API_KEY": "abc", "FRED_API_KEY": "def"})

    def test_save_keys_overwrites_same_key(self):
        env_keys.save_keys({"DART_API_KEY": "abc"}, self.env_path)
        env_keys.save_keys({"DART_API_KEY": "xyz"}, self.env_path)
        values = env_keys.read_env_file(self.env_path)
        self.assertEqual(values, {"DART_API_KEY": "xyz"})

    def test_onboarding_message_lists_missing_keys(self):
        msg = env_keys.onboarding_message(["DART_API_KEY", "FRED_API_KEY"])
        self.assertIn("DART_API_KEY", msg)
        self.assertIn("FRED_API_KEY", msg)
        self.assertIn("opendart.fss.or.kr", msg)
        self.assertIn("fred.stlouisfed.org", msg)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python tests/tools/test_env_keys.py -v`
Expected: `ModuleNotFoundError: No module named 'env_keys'` (module doesn't exist yet)

- [ ] **Step 3: Write the implementation**

Create `tools/env_keys.py`:

```python
"""
DART_API_KEY / FRED_API_KEY 온보딩 — 없으면 채팅으로 물어보고 .env에 저장한다.

사용:
    python tools/env_keys.py check
    python tools/env_keys.py save DART_API_KEY=xxxx FRED_API_KEY=yyyy
"""
import os
import sys

REQUIRED_KEYS = ["DART_API_KEY", "FRED_API_KEY"]

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ENV_PATH = os.path.join(_REPO_ROOT, ".env")

ONBOARDING_TEMPLATE = (
    "이 스킬은 {keys}가 필요합니다. 채팅에 바로 붙여넣어 주세요.\n"
    " - DART: https://opendart.fss.or.kr 에서 발급\n"
    " - FRED: https://fred.stlouisfed.org/docs/api/api_key.html 에서 발급\n"
    "(다음부터 다시 안 묻도록 로컬 .env에 저장합니다)"
)


def read_env_file(path):
    values = {}
    if not os.path.exists(path):
        return values
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip()
    return values


def find_missing_keys(path=DEFAULT_ENV_PATH, environ=None):
    environ = os.environ if environ is None else environ
    file_values = read_env_file(path)
    missing = []
    for key in REQUIRED_KEYS:
        if environ.get(key) or file_values.get(key):
            continue
        missing.append(key)
    return missing


def save_keys(new_keys, path=DEFAULT_ENV_PATH):
    existing = read_env_file(path)
    existing.update(new_keys)
    with open(path, "w", encoding="utf-8") as f:
        for k, v in existing.items():
            f.write("{}={}\n".format(k, v))


def onboarding_message(missing):
    return ONBOARDING_TEMPLATE.format(keys=", ".join(missing))


def main(argv):
    if not argv:
        print("usage: env_keys.py check | save KEY=VALUE [KEY=VALUE ...]")
        return 2
    cmd = argv[0]
    if cmd == "check":
        missing = find_missing_keys()
        if missing:
            print("MISSING:" + ",".join(missing))
            print(onboarding_message(missing))
            return 1
        print("OK")
        return 0
    if cmd == "save":
        pairs = {}
        for item in argv[1:]:
            if "=" not in item:
                print("bad pair: {}".format(item))
                return 2
            k, v = item.split("=", 1)
            pairs[k.strip()] = v.strip()
        if not pairs:
            print("no KEY=VALUE pairs given")
            return 2
        save_keys(pairs)
        print("SAVED:" + ",".join(pairs.keys()))
        return 0
    print("unknown command: {}".format(cmd))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python tests/tools/test_env_keys.py -v`
Expected: all 9 tests PASS

- [ ] **Step 5: Manually verify the CLI**

Run: `python tools/env_keys.py check`
Expected: prints `MISSING:...` and the onboarding message if keys aren't set in the real `.env`/environ, or `OK` if they are. (Don't worry which — just confirm it runs without a traceback.)

- [ ] **Step 6: Commit**

```bash
git add tools/env_keys.py tests/tools/test_env_keys.py
git commit -m "feat(industry-screen): add DART/FRED API key onboarding helper"
```

---

### Task 2: `tools/industry_cache.py` — 산업 캐시 읽기/쓰기

**Files:**
- Create: `tools/industry_cache.py`
- Test: `tests/tools/test_industry_cache.py`

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces:
  - `CACHE_PATH: str` = `"data/industry_cache.json"` (relative to repo root)
  - `empty_cache() -> dict` — `{"companies": {}, "industries": {}}`
  - `load_cache(path: str) -> dict`
  - `save_cache(cache: dict, path: str) -> None`
  - `get_company(cache: dict, ticker: str) -> dict | None`
  - `get_industry(cache: dict, name: str) -> dict | None`
  - `list_industries(cache: dict) -> list[str]` (정렬됨)
  - `add_company(cache: dict, ticker: str, name: str, induty_code: str | None, industry_label: str, today: str | None = None) -> dict`
    — `cache["companies"][ticker]`를 만들거나 갱신하고, `cache["industries"][industry_label]`에도 등록한다 (mutates and returns `cache`).
  - CLI: `python tools/industry_cache.py list-industries`
  - CLI: `python tools/industry_cache.py get-industry "<name>"`
  - CLI: `python tools/industry_cache.py get-company <ticker>`
  - CLI: `python tools/industry_cache.py add-company <ticker> <name> <induty_code|-> <industry_label>` (`-`는 induty_code 미상)

- [ ] **Step 1: Write the failing tests**

Create `tests/tools/test_industry_cache.py`:

```python
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import industry_cache as ic


class TestIndustryCache(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache_path = os.path.join(self.tmpdir, "data", "industry_cache.json")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_load_cache_missing_file_returns_empty_structure(self):
        cache = ic.load_cache(self.cache_path)
        self.assertEqual(cache, {"companies": {}, "industries": {}})

    def test_save_then_load_round_trips(self):
        cache = ic.empty_cache()
        ic.add_company(cache, "009540", "HD한국조선해양", "31114", "조선·조선기자재", today="2026-08-13")
        ic.save_cache(cache, self.cache_path)
        loaded = ic.load_cache(self.cache_path)
        self.assertEqual(loaded, cache)

    def test_add_company_creates_company_and_industry_entries(self):
        cache = ic.empty_cache()
        ic.add_company(cache, "009540", "HD한국조선해양", "31114", "조선·조선기자재", today="2026-08-13")

        company = ic.get_company(cache, "009540")
        self.assertEqual(company["name"], "HD한국조선해양")
        self.assertEqual(company["induty_code"], "31114")
        self.assertEqual(company["industry_labels"], ["조선·조선기자재"])
        self.assertEqual(company["cached_at"], "2026-08-13")

        industry = ic.get_industry(cache, "조선·조선기자재")
        self.assertEqual(industry["tickers"], ["009540"])
        self.assertEqual(industry["induty_codes"], ["31114"])
        self.assertEqual(industry["first_seen"], "2026-08-13")

    def test_add_company_twice_does_not_duplicate(self):
        cache = ic.empty_cache()
        ic.add_company(cache, "009540", "HD한국조선해양", "31114", "조선·조선기자재", today="2026-08-13")
        ic.add_company(cache, "009540", "HD한국조선해양", "31114", "조선·조선기자재", today="2026-08-14")

        industry = ic.get_industry(cache, "조선·조선기자재")
        self.assertEqual(industry["tickers"], ["009540"])
        self.assertEqual(industry["induty_codes"], ["31114"])

    def test_add_company_same_ticker_multiple_industries(self):
        cache = ic.empty_cache()
        ic.add_company(cache, "009540", "HD한국조선해양", "31114", "조선·조선기자재")
        ic.add_company(cache, "009540", "HD한국조선해양", "31114", "방산·항공")

        company = ic.get_company(cache, "009540")
        self.assertEqual(company["industry_labels"], ["조선·조선기자재", "방산·항공"])

    def test_get_company_missing_returns_none(self):
        cache = ic.empty_cache()
        self.assertIsNone(ic.get_company(cache, "999999"))

    def test_get_industry_missing_returns_none(self):
        cache = ic.empty_cache()
        self.assertIsNone(ic.get_industry(cache, "없는산업"))

    def test_list_industries_sorted(self):
        cache = ic.empty_cache()
        ic.add_company(cache, "1", "가", "1", "다산업")
        ic.add_company(cache, "2", "나", "2", "가산업")
        self.assertEqual(ic.list_industries(cache), ["가산업", "다산업"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python tests/tools/test_industry_cache.py -v`
Expected: `ModuleNotFoundError: No module named 'industry_cache'`

- [ ] **Step 3: Write the implementation**

Create `tools/industry_cache.py`:

```python
"""
data/industry_cache.json 읽기/쓰기 — 산업-종목 매핑을 자동으로 쌓아가는 캐시.

고정된 "허용 산업 목록"이 아니라, 지금까지 discover/verify가 확인한 것들의 기록이다.
새 산업/종목은 언제든 add-company로 편입된다.

사용:
    python tools/industry_cache.py list-industries
    python tools/industry_cache.py get-industry "조선·조선기자재"
    python tools/industry_cache.py get-company 009540
    python tools/industry_cache.py add-company 009540 HD한국조선해양 31114 "조선·조선기자재"
"""
import datetime
import json
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(_REPO_ROOT, "data", "industry_cache.json")


def empty_cache():
    return {"companies": {}, "industries": {}}


def load_cache(path=CACHE_PATH):
    if not os.path.exists(path):
        return empty_cache()
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("companies", {})
    data.setdefault("industries", {})
    return data


def save_cache(cache, path=CACHE_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2, sort_keys=True)


def get_company(cache, ticker):
    return cache["companies"].get(ticker)


def get_industry(cache, name):
    return cache["industries"].get(name)


def list_industries(cache):
    return sorted(cache["industries"].keys())


def add_company(cache, ticker, name, induty_code, industry_label, today=None):
    today = today or datetime.date.today().isoformat()

    entry = cache["companies"].get(ticker)
    if entry is None:
        entry = {"name": name, "induty_code": induty_code, "industry_labels": [], "cached_at": today}
        cache["companies"][ticker] = entry
    entry["name"] = name
    entry["induty_code"] = induty_code
    if industry_label not in entry["industry_labels"]:
        entry["industry_labels"].append(industry_label)

    ind = cache["industries"].get(industry_label)
    if ind is None:
        ind = {"induty_codes": [], "tickers": [], "first_seen": today}
        cache["industries"][industry_label] = ind
    if induty_code and induty_code not in ind["induty_codes"]:
        ind["induty_codes"].append(induty_code)
    if ticker not in ind["tickers"]:
        ind["tickers"].append(ticker)

    return cache


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    cache = load_cache()

    if cmd == "list-industries":
        print(json.dumps(list_industries(cache), ensure_ascii=False))
        return 0

    if cmd == "get-industry":
        if len(argv) < 2:
            print("usage: get-industry <name>")
            return 2
        result = get_industry(cache, argv[1])
        print(json.dumps(result, ensure_ascii=False) if result else "NOT_FOUND")
        return 0 if result else 1

    if cmd == "get-company":
        if len(argv) < 2:
            print("usage: get-company <ticker>")
            return 2
        result = get_company(cache, argv[1])
        print(json.dumps(result, ensure_ascii=False) if result else "NOT_FOUND")
        return 0 if result else 1

    if cmd == "add-company":
        if len(argv) < 5:
            print("usage: add-company <ticker> <name> <induty_code|-> <industry_label>")
            return 2
        ticker, name, induty_code, industry_label = argv[1], argv[2], argv[3], argv[4]
        induty_code = None if induty_code == "-" else induty_code
        add_company(cache, ticker, name, induty_code, industry_label)
        save_cache(cache)
        print("SAVED")
        return 0

    print("unknown command: {}".format(cmd))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python tests/tools/test_industry_cache.py -v`
Expected: all 8 tests PASS

- [ ] **Step 5: Manually verify the CLI**

```bash
python tools/industry_cache.py add-company 009540 HD한국조선해양 31114 "조선·조선기자재"
python tools/industry_cache.py get-industry "조선·조선기자재"
python tools/industry_cache.py list-industries
```
Expected: `SAVED`, then a JSON object with `tickers: ["009540"]`, then `["조선·조선기자재"]`. Confirm `data/industry_cache.json` was created in the repo root.

Then remove this test artifact so it doesn't pollute the real migration in Task 4:
```bash
rm -f data/industry_cache.json
```

- [ ] **Step 6: Commit**

```bash
git add tools/industry_cache.py tests/tools/test_industry_cache.py
git commit -m "feat(industry-screen): add auto-growing industry cache (replaces fixed CSV)"
```

---

### Task 3: `tools/dart_lookup.py` — DART 업종코드 조회

**Files:**
- Create: `tools/dart_lookup.py`
- Test: `tests/tools/test_dart_lookup.py`

**Interfaces:**
- Consumes: nothing from Task 1/2 (standalone; `migrate_industry_cache.py` in Task 4 will import it).
- Produces:
  - `CORP_CODE_CACHE_PATH: str` = `"data/dart_corp_codes.csv"` (gitignored, already in `.gitignore`)
  - `parse_corp_code_zip(zip_bytes: bytes) -> list[dict]` — each dict has `corp_code`, `corp_name`, `stock_code`, `modify_date`; only rows with non-empty `stock_code` (listed companies).
  - `build_corp_code_cache(api_key: str, path: str, fetcher=None) -> list[dict]` — fetches corpCode.xml, writes CSV, returns rows.
  - `load_corp_code_cache(path: str) -> dict[str, str]` — ticker → corp_code.
  - `get_corp_code(ticker: str, api_key: str, cache_path: str, fetcher=None) -> str | None`
  - `fetch_company_info(corp_code: str, api_key: str, fetcher=None) -> dict` — parses DART `company.json` response.
  - `get_induty_code(ticker: str, api_key: str, cache_path: str, fetcher=None) -> dict | None` — `{"corp_code", "corp_name", "induty_code"}` or `None` if ticker not found.
  - `fetcher` param: injectable `callable(url: str) -> bytes`, defaults to a real HTTP GET. Tests always pass a fake.
  - CLI: `python tools/dart_lookup.py induty-code <ticker>` (reads `DART_API_KEY` from env; prints JSON or `NOT_FOUND`, exit 1 if not found, exit 2 if no API key)

- [ ] **Step 1: Write the failing tests**

Create `tests/tools/test_dart_lookup.py`:

```python
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import dart_lookup as dl


def make_corp_code_zip(rows):
    """rows: list of (corp_code, corp_name, stock_code, modify_date) -> zip bytes with corpCode.xml inside"""
    parts = ["<result>"]
    for corp_code, corp_name, stock_code, modify_date in rows:
        parts.append(
            "<list><corp_code>{}</corp_code><corp_name>{}</corp_name>"
            "<stock_code>{}</stock_code><modify_date>{}</modify_date></list>".format(
                corp_code, corp_name, stock_code, modify_date
            )
        )
    parts.append("</result>")
    xml_bytes = "".join(parts).encode("utf-8")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("CORPCODE.xml", xml_bytes)
    return buf.getvalue()


class TestParseCorpCodeZip(unittest.TestCase):
    def test_filters_out_unlisted_rows(self):
        zip_bytes = make_corp_code_zip([
            ("00126380", "삼성전자", "005930", "20260101"),
            ("00999999", "비상장회사", "", "20260101"),
        ])
        rows = dl.parse_corp_code_zip(zip_bytes)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["stock_code"], "005930")
        self.assertEqual(rows[0]["corp_name"], "삼성전자")


class TestCorpCodeCache(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache_path = os.path.join(self.tmpdir, "dart_corp_codes.csv")
        self.zip_bytes = make_corp_code_zip([
            ("00126380", "삼성전자", "005930", "20260101"),
            ("00164742", "HD한국조선해양", "009540", "20260101"),
        ])

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_build_corp_code_cache_writes_csv(self):
        calls = []

        def fake_fetcher(url):
            calls.append(url)
            return self.zip_bytes

        rows = dl.build_corp_code_cache("APIKEY", path=self.cache_path, fetcher=fake_fetcher)
        self.assertEqual(len(rows), 2)
        self.assertTrue(os.path.exists(self.cache_path))
        self.assertEqual(len(calls), 1)
        self.assertIn("APIKEY", calls[0])

    def test_get_corp_code_uses_existing_cache_without_refetch(self):
        dl.build_corp_code_cache("APIKEY", path=self.cache_path, fetcher=lambda url: self.zip_bytes)

        def fail_if_called(url):
            raise AssertionError("should not refetch when cache already has the ticker")

        corp_code = dl.get_corp_code("005930", "APIKEY", cache_path=self.cache_path, fetcher=fail_if_called)
        self.assertEqual(corp_code, "00126380")

    def test_get_corp_code_builds_cache_when_missing(self):
        corp_code = dl.get_corp_code(
            "009540", "APIKEY", cache_path=self.cache_path, fetcher=lambda url: self.zip_bytes
        )
        self.assertEqual(corp_code, "00164742")

    def test_get_corp_code_unknown_ticker_returns_none(self):
        corp_code = dl.get_corp_code(
            "000000", "APIKEY", cache_path=self.cache_path, fetcher=lambda url: self.zip_bytes
        )
        self.assertIsNone(corp_code)


class TestCompanyInfoAndIndutyCode(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cache_path = os.path.join(self.tmpdir, "dart_corp_codes.csv")
        self.zip_bytes = make_corp_code_zip([("00164742", "HD한국조선해양", "009540", "20260101")])

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_fetch_company_info_parses_json(self):
        payload = json.dumps({
            "status": "000", "corp_name": "HD한국조선해양", "induty_code": "31114"
        }).encode("utf-8")
        info = dl.fetch_company_info("00164742", "APIKEY", fetcher=lambda url: payload)
        self.assertEqual(info["induty_code"], "31114")
        self.assertEqual(info["corp_name"], "HD한국조선해양")

    def test_get_induty_code_happy_path(self):
        fetch_log = []

        def fake_fetcher(url):
            fetch_log.append(url)
            if "corpCode.xml" in url:
                return self.zip_bytes
            return json.dumps({"corp_name": "HD한국조선해양", "induty_code": "31114"}).encode("utf-8")

        result = dl.get_induty_code("009540", "APIKEY", cache_path=self.cache_path, fetcher=fake_fetcher)
        self.assertEqual(result, {
            "corp_code": "00164742", "corp_name": "HD한국조선해양", "induty_code": "31114"
        })

    def test_get_induty_code_unknown_ticker_returns_none_without_company_call(self):
        fetch_log = []

        def fake_fetcher(url):
            fetch_log.append(url)
            return self.zip_bytes

        result = dl.get_induty_code("999999", "APIKEY", cache_path=self.cache_path, fetcher=fake_fetcher)
        self.assertIsNone(result)
        # only the corpCode.xml lookup should have happened, never company.json
        self.assertEqual(len(fetch_log), 1)
        self.assertIn("corpCode.xml", fetch_log[0])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python tests/tools/test_dart_lookup.py -v`
Expected: `ModuleNotFoundError: No module named 'dart_lookup'`

- [ ] **Step 3: Write the implementation**

Create `tools/dart_lookup.py`:

```python
"""
DART 업종코드(induty_code) 조회 — Step 0의 유니버스 구축에서 쓰인다.

DART에는 "업종코드로 회사 목록 일괄 검색"이 없다. 회사별 induty_code는 company.json을
회사 하나하나 호출해야 안다. 그래서 corpCode.xml(전체 상장사 목록, 1회 호출)을 로컬에
캐싱해두고, 처음 만난 티커만 company.json을 호출해 induty_code를 알아낸다.

사용:
    python tools/dart_lookup.py induty-code 009540
"""
import csv
import io
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

CORP_CODE_URL = "https://opendart.fss.or.kr/api/corpCode.xml"
COMPANY_URL = "https://opendart.fss.or.kr/api/company.json"

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORP_CODE_CACHE_PATH = os.path.join(_REPO_ROOT, "data", "dart_corp_codes.csv")


def _http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_corp_code_zip(zip_bytes):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        xml_bytes = zf.read(zf.namelist()[0])
    root = ET.fromstring(xml_bytes)
    rows = []
    for el in root.findall("list"):
        stock_code = (el.findtext("stock_code") or "").strip()
        if not stock_code:
            continue
        rows.append({
            "corp_code": (el.findtext("corp_code") or "").strip(),
            "corp_name": (el.findtext("corp_name") or "").strip(),
            "stock_code": stock_code,
            "modify_date": (el.findtext("modify_date") or "").strip(),
        })
    return rows


def build_corp_code_cache(api_key, path=CORP_CODE_CACHE_PATH, fetcher=None):
    fetcher = fetcher or _http_get
    url = "{}?crtfc_key={}".format(CORP_CODE_URL, api_key)
    zip_bytes = fetcher(url)
    rows = parse_corp_code_zip(zip_bytes)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ticker", "corp_code", "corp_name", "modify_date"])
        for r in rows:
            w.writerow([r["stock_code"], r["corp_code"], r["corp_name"], r["modify_date"]])
    return rows


def load_corp_code_cache(path=CORP_CODE_CACHE_PATH):
    mapping = {}
    if not os.path.exists(path):
        return mapping
    with io.open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mapping[row["ticker"]] = row["corp_code"]
    return mapping


def get_corp_code(ticker, api_key, cache_path=CORP_CODE_CACHE_PATH, fetcher=None):
    mapping = load_corp_code_cache(cache_path)
    if ticker in mapping:
        return mapping[ticker]
    build_corp_code_cache(api_key, cache_path, fetcher=fetcher)
    mapping = load_corp_code_cache(cache_path)
    return mapping.get(ticker)


def fetch_company_info(corp_code, api_key, fetcher=None):
    fetcher = fetcher or _http_get
    url = "{}?crtfc_key={}&corp_code={}".format(COMPANY_URL, api_key, corp_code)
    raw = fetcher(url)
    return json.loads(raw)


def get_induty_code(ticker, api_key, cache_path=CORP_CODE_CACHE_PATH, fetcher=None):
    corp_code = get_corp_code(ticker, api_key, cache_path, fetcher=fetcher)
    if not corp_code:
        return None
    info = fetch_company_info(corp_code, api_key, fetcher=fetcher)
    return {
        "corp_code": corp_code,
        "corp_name": info.get("corp_name"),
        "induty_code": info.get("induty_code"),
    }


def main(argv):
    if not argv or argv[0] != "induty-code" or len(argv) < 2:
        print("usage: dart_lookup.py induty-code <ticker>")
        return 2
    api_key = os.environ.get("DART_API_KEY")
    if not api_key:
        print("DART_API_KEY not set")
        return 2
    result = get_induty_code(argv[1], api_key)
    if result is None:
        print("NOT_FOUND")
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python tests/tools/test_dart_lookup.py -v`
Expected: all 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add tools/dart_lookup.py tests/tools/test_dart_lookup.py
git commit -m "feat(industry-screen): add DART induty_code lookup with auto-caching"
```

---

### Task 4: `tools/migrate_industry_cache.py` — 기존 CSV를 캐시로 이관

**Files:**
- Create: `tools/migrate_industry_cache.py`
- Test: `tests/tools/test_migrate_industry_cache.py`

**Interfaces:**
- Consumes: `industry_cache.load_cache`, `industry_cache.save_cache`, `industry_cache.add_company` (Task 2); `dart_lookup.get_induty_code` (Task 3).
- Produces:
  - `migrate(api_key: str | None, source_path: str, cache_path: str, dart_cache_path: str, fetcher=None) -> dict` — returns the resulting cache dict.
  - CLI: `python tools/migrate_industry_cache.py` (no args; reads `DART_API_KEY` from env, uses real paths)

- [ ] **Step 1: Write the failing test**

Create `tests/tools/test_migrate_industry_cache.py`:

```python
import io
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import migrate_industry_cache as migrate_mod
import industry_cache as ic


FIXTURE_CSV = (
    "industry,ticker,name,ksic_code\n"
    "조선·조선기자재,009540,HD한국조선해양,\n"
    "조선·조선기자재,042660,한화오션,\n"
    "방산·항공,012450,한화에어로스페이스,\n"
)


class TestMigrateIndustryCache(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.source_path = os.path.join(self.tmpdir, "industry_universe.csv")
        self.cache_path = os.path.join(self.tmpdir, "industry_cache.json")
        self.dart_cache_path = os.path.join(self.tmpdir, "dart_corp_codes.csv")
        with io.open(self.source_path, "w", encoding="utf-8") as f:
            f.write(FIXTURE_CSV)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_migrate_without_api_key_leaves_induty_code_none(self):
        cache = migrate_mod.migrate(
            api_key=None,
            source_path=self.source_path,
            cache_path=self.cache_path,
            dart_cache_path=self.dart_cache_path,
        )
        company = ic.get_company(cache, "009540")
        self.assertEqual(company["name"], "HD한국조선해양")
        self.assertIsNone(company["induty_code"])

        industry = ic.get_industry(cache, "조선·조선기자재")
        self.assertEqual(sorted(industry["tickers"]), ["009540", "042660"])

        self.assertTrue(os.path.exists(self.cache_path))

    def test_migrate_with_api_key_fills_induty_code(self):
        def fake_fetcher(url):
            raise AssertionError("this test doesn't need real DART calls")

        # Patch get_induty_code to avoid needing real HTTP fixtures here —
        # dart_lookup's own network behavior is already covered in Task 3's tests.
        original = migrate_mod.dart_lookup.get_induty_code
        migrate_mod.dart_lookup.get_induty_code = (
            lambda ticker, api_key, cache_path=None, fetcher=None: {
                "corp_code": "X", "corp_name": "n/a", "induty_code": "31114"
            }
        )
        try:
            cache = migrate_mod.migrate(
                api_key="APIKEY",
                source_path=self.source_path,
                cache_path=self.cache_path,
                dart_cache_path=self.dart_cache_path,
            )
        finally:
            migrate_mod.dart_lookup.get_induty_code = original

        company = ic.get_company(cache, "009540")
        self.assertEqual(company["induty_code"], "31114")

    def test_migrate_covers_all_rows(self):
        cache = migrate_mod.migrate(
            api_key=None,
            source_path=self.source_path,
            cache_path=self.cache_path,
            dart_cache_path=self.dart_cache_path,
        )
        self.assertEqual(sorted(ic.list_industries(cache)), ["방산·항공", "조선·조선기자재"])
        self.assertEqual(len(cache["companies"]), 3)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/tools/test_migrate_industry_cache.py -v`
Expected: `ModuleNotFoundError: No module named 'migrate_industry_cache'`

- [ ] **Step 3: Write the implementation**

Create `tools/migrate_industry_cache.py`:

```python
"""
1회성 이관: data/industry_universe.csv(고정 6산업/59종목) -> data/industry_cache.json

기존 industry_universe.csv를 없애기 전에 한 번 실행해서 자동 성장 캐시의 시드로 옮긴다.
DART_API_KEY가 있으면 각 티커의 induty_code도 채운다 — 없으면 null로 두고, 이후
discover/verify가 그 종목을 다시 만날 때 dart_lookup.get_induty_code로 지연 채움한다.

사용:
    python tools/migrate_industry_cache.py
"""
import csv
import io
import os
import sys

import dart_lookup
import industry_cache as ic

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SOURCE_PATH = os.path.join(_REPO_ROOT, "data", "industry_universe.csv")


def migrate(api_key=None, source_path=DEFAULT_SOURCE_PATH, cache_path=ic.CACHE_PATH,
            dart_cache_path=dart_lookup.CORP_CODE_CACHE_PATH, fetcher=None):
    cache = ic.load_cache(cache_path)
    with io.open(source_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        ticker = row["ticker"].strip()
        name = row["name"].strip()
        industry = row["industry"].strip()
        induty_code = None
        if api_key:
            info = dart_lookup.get_induty_code(
                ticker, api_key, cache_path=dart_cache_path, fetcher=fetcher
            )
            if info:
                induty_code = info.get("induty_code")
        ic.add_company(cache, ticker, name, induty_code, industry)

    ic.save_cache(cache, cache_path)
    return cache


if __name__ == "__main__":
    key = os.environ.get("DART_API_KEY")
    result = migrate(api_key=key)
    print("migrated {} companies across {} industries -> {}".format(
        len(result["companies"]), len(result["industries"]), ic.CACHE_PATH
    ))
    sys.exit(0)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/tools/test_migrate_industry_cache.py -v`
Expected: all 3 tests PASS

- [ ] **Step 5: Run the real migration**

```bash
python tools/migrate_industry_cache.py
```
Expected: prints `migrated 59 companies across 6 industries -> .../data/industry_cache.json`
(Runs with whatever `DART_API_KEY` is currently set — `induty_code` will be filled if the key works, `null` otherwise, either is fine per the design.)

- [ ] **Step 6: Spot-check the generated cache**

Run: `python tools/industry_cache.py get-industry "조선·조선기자재"`
Expected: JSON with 6 tickers including `"009540"`.

- [ ] **Step 7: Commit**

```bash
git add tools/migrate_industry_cache.py tests/tools/test_migrate_industry_cache.py data/industry_cache.json
git commit -m "feat(industry-screen): migrate fixed industry_universe.csv into auto-growing cache"
```

---

### Task 5: `data/industry_universe.csv` 제거 + `.gitignore`/README 업데이트

**Files:**
- Delete: `data/industry_universe.csv`
- Modify: `README.md:218-240` (§5 저장소 구조), `README.md:297-333` (§7 B 역할)

**Interfaces:** none (docs/cleanup only).

- [ ] **Step 1: Remove the now-migrated fixed CSV**

```bash
git rm data/industry_universe.csv
```

- [ ] **Step 2: Update README §5 저장소 구조**

In `README.md`, find this block (around line 234-237):

```
├─ data/
│  ├─ consensus.csv
│  ├─ price.csv
│  └─ industry_universe.csv               산업별 컨센 종목 수 [B]
└─ reports/
```

Replace with:

```
├─ data/
│  ├─ consensus.csv
│  ├─ price.csv
│  ├─ industry_cache.json                 산업-종목 캐시, 자동 성장 [B]
│  └─ dart_corp_codes.csv                 DART 상장사 캐시 (gitignore) [B]
└─ reports/
```

- [ ] **Step 3: Update README §7 B 역할 설명**

In `README.md`, find this line (around line 318):

```
- **discover와 verify는 파일 하나 안의 두 모드.** 나누면 기준이 갈라진다.
```

Add immediately after it (before `- **출력은 JSON.**`):

```
- **유니버스는 고정 CSV가 아니라 `data/industry_cache.json`.** discover가 브레인스토밍한
  후보 산업은 `tools/dart_lookup.py`로 실존을 확인하며 캐시에 자동 편입된다 — 사람이 손으로
  채우는 목록이 아니다. 이래야 "설비·물질 기반 중공업"에만 몰리지 않고 서비스·금융 등
  Q1-YES 함정(☠) 후보도 나올 수 있다.
```

- [ ] **Step 4: Verify no other references to the removed CSV remain**

Run: `grep -rn "industry_universe.csv" README.md .claude/ contracts/ tools/ 2>/dev/null`
Expected: no output (Task 6 will have already rewritten `SKILL.md`'s references — if this task runs before Task 6, expect matches only inside `SKILL.md`, which Task 6 fixes next)

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: replace industry_universe.csv references with industry_cache.json"
```

---

### Task 6: `SKILL.md` 재작성 — 키 온보딩, 캐시 기반 유니버스, discover 브레인스토밍, UX

**Files:**
- Modify: `.claude/skills/industry-screen/SKILL.md` (전체 재작성)

**Interfaces:**
- Consumes: `tools/env_keys.py` CLI (Task 1), `tools/industry_cache.py` CLI (Task 2), `tools/dart_lookup.py` CLI (Task 3), MCP tools `mcp__plugin_fnspace_fnspace__get_target_price` / `get_estimates` (already available, no code change needed).
- Produces: same `01-industry.json` schema as before (unchanged, see Global Constraints).

- [ ] **Step 1: Replace the entire file content**

Replace the full content of `.claude/skills/industry-screen/SKILL.md` with:

```markdown
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
1. 캐시에 이미 있는가?
     python tools/industry_cache.py get-industry "<산업명>"
     있다 → 그 tickers로 Step 1(candidate set)로 진행
     없다 → 2로

2. 각 후보 종목마다 DART로 실존/업종코드를 확인한다 (처음 만난 티커만 — 캐시에
   있으면 다시 안 부른다)
     python tools/dart_lookup.py induty-code <ticker>
   반환된 induty_code로 캐시에 등록 (JSON의 `induty_code`가 `null`이면 `-`를 넣는다 —
   `add-company`는 `-`를 "미상"으로 처리한다):
     python tools/industry_cache.py add-company <ticker> <name> <induty_code-or-"-"> "<산업명>"

3. 등록 후 Step 1(candidate set)로 진행
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
freshly DART-confirmed, see above), get each ticker's consensus coverage **directly
from FnSpace** — call `mcp__plugin_fnspace_fnspace__get_target_price` (또는
`get_estimates`) per ticker. `coverage_count`는 그 응답에서 컨센서스를 낸 기관 수로
판단한다 (FnSpace 응답 필드명은 실제 호출 결과를 보고 확인 — 항목 코드가 궁금하면
`list_items(apigb="A000003")`으로 카탈로그를 먼저 훑는다). Candidates = tickers with
`coverage_count >= 3`.

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
   캐싱하고, 처음 만난 티커에 한해 `company.json`을 호출해 `induty_code`를 얻는다.
   이미 캐시에 있는 티커는 재호출하지 않는다.

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
  "_universe_source": "data/industry_cache.json (auto-discovered via DART + FnSpace, not a fixed list)"
}
```

`_dart_check`, `_macro_context`, `_universe_source`는 **파이프라인 계약이 아니다** —
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
```

- [ ] **Step 2: Confirm no stray references to the old CSV remain**

Run: `grep -n "industry_universe.csv" .claude/skills/industry-screen/SKILL.md`
Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/industry-screen/SKILL.md
git commit -m "feat(industry-screen): rewrite skill for key onboarding, dynamic universe, guided UX"
```

---

### Task 7: 전 구간 수동 검증 (dogfood)

**Files:** none (검증만).

**Interfaces:** none.

- [ ] **Step 1: `.env`에서 두 키를 잠깐 지워 abort 경로를 확인**

```bash
mv .env .env.bak 2>/dev/null || true
python tools/env_keys.py check
```
Expected: exit 1, `MISSING:DART_API_KEY,FRED_API_KEY` + 온보딩 메시지가 출력된다.

```bash
mv .env.bak .env 2>/dev/null || true
```
(원래 `.env` 복원 — 없었다면 이 단계는 아무것도 안 함)

- [ ] **Step 2: 실제 skill 호출로 verify 모드 1회 관통**

Claude Code 세션에서 `/industry-screen` 실행 후 이미 캐시에 있는 산업 하나(예: "조선·조선기자재")를
verify 모드로 지정해 실행한다.

Expected:
- Step -1이 조용히 통과한다 (키가 이미 있으므로).
- `runs/<오늘날짜>_조선·조선기자재/01-industry.json`이 생성되고 기존 스키마와 필드명이 동일하다.
- 채팅 요약에 쉬운 말 병기와 "Skill 2로 넘길까요?" 질문이 포함된다.

- [ ] **Step 3: discover 모드 1회 관통 (새 산업이 섞여 나오는지 확인)**

`/industry-screen` 실행 후 산업 미지정 → discover 선택.

Expected:
- 후보 브레인스토밍이 기존 6개 산업(중공업 위주)에 갇히지 않고 최소 1개는 새로운
  업종(서비스/금융/컨설팅 등)이 섞여 나온다.
- 진행상황이 산업별로 짧게 출력된다.
- `data/industry_cache.json`에 새로 확인된 산업/종목이 추가되어 있다
  (`python tools/industry_cache.py list-industries`로 확인).

- [ ] **Step 4: 위 두 관통에서 발견된 실제 문제를 기록하고 필요하면 Task 6의 SKILL.md를 소폭 수정**

이 단계는 코드 변경이 아니라 **관찰** — README §8 timeline이 강조하는 "종목 1개로 끝까지
관통이 최우선"을 이 스킬 단위로 반복한 것. 문제가 나오면 Task 6에서 수정한 해당 섹션만
고치고 새 커밋을 만든다 (기존 커밋을 amend하지 않는다).
