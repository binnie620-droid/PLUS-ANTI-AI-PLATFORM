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
