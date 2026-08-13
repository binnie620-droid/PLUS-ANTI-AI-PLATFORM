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

import paths

CACHE_NAME = "industry_cache.json"
# 쓰기 기준 경로. 플러그인으로 설치되면 사용자 프로젝트 쪽을 가리킨다.
CACHE_PATH = paths.target(CACHE_NAME)


def empty_cache():
    return {"companies": {}, "industries": {}}


def load_cache(path=None):
    # 기본 읽기는 작업본 우선, 없으면 저장소에 커밋된 씨앗 캐시를 본다.
    path = path or paths.source(CACHE_NAME)
    if not os.path.exists(path):
        return empty_cache()
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("companies", {})
    data.setdefault("industries", {})
    return data


def save_cache(cache, path=None):
    path = paths.ensure_dir(path or paths.target(CACHE_NAME))
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
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
