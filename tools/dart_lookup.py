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

import env_keys

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
    data = json.loads(raw)
    if data.get("status") != "000":
        error_msg = data.get("message", "Unknown error")
        raise RuntimeError("DART API error (status={}): {}".format(data.get("status"), error_msg))
    return data


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
    api_key = os.environ.get("DART_API_KEY") or env_keys.read_env_file(env_keys.DEFAULT_ENV_PATH).get("DART_API_KEY")
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
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
