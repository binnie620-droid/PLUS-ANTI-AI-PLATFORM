"""DART 재무제표에서 ROE·ROIC를 계산한다.

    python tools/fetch_roic.py 062040 103590
    python tools/fetch_roic.py 062040 --year 2025 --json

ROE  = 당기순이익 / 평균 자본총계
ROIC = NOPAT / 평균 투하자본
       NOPAT   = 영업이익 x (1 - 유효법인세율)
       유효법인세율 = 법인세비용 / 법인세비용차감전순이익
       투하자본 = 자본총계 + 총차입금 - (현금및현금성자산 + 단기금융상품)

평균을 쓰는 이유: 증설 기업은 기말 자본이 기초보다 크게 늘어 ROIC가 과소평가된다.
DART API는 당기(thstrm)와 전기(frmtrm)를 함께 주므로 한 번 호출로 평균이 나온다.
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import time
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
E = 1e8  # 억원

EQUITY = [r"^자본총계$"]
DEBT = [r"차입금", r"^사채$"]
CASH = [r"^현금및현금성자산$", r"^단기금융상품$"]
OP = [r"^영업이익"]
NI = [r"^당기순이익"]
TAX = [r"^법인세비용"]
PRETAX = [r"법인세비용차감전순이익"]


def api_key():
    """tools/env_keys.py 와 같은 규칙으로 읽는다 — .env 값이 따옴표로 감싸여 있을 수 있다.
    직접 파싱하면 FRED 키에서 실제로 겪었듯 길이가 32자를 넘어 API가 400을 낸다."""
    key = os.environ.get("DART_API_KEY")
    if key:
        return key.strip().strip("\"'")
    env = os.path.join(BASE, ".env")
    if os.path.exists(env):
        for line in io.open(env, encoding="utf-8"):
            if line.strip().startswith("DART_API_KEY"):
                return line.split("=", 1)[1].strip().strip("\"'")
    sys.exit("DART_API_KEY 없음 — python tools/env_keys.py check 로 확인하라")


def corp_code(ticker):
    """ticker -> (회사명, corp_code).

    캐시 파일은 gitignore 대상이라 clone 직후에는 없다. 없으면 DART에서 자동으로
    받아온다. 헤더는 두 가지가 돌아다닌다 — dart_lookup.py 가 만드는
    `ticker,corp_code,corp_name,modify_date` 와 초기 수기 파일의
    `ticker,name,corp_code` 다. 소비자 쪽에서 둘 다 받는다.
    """
    sys.path.insert(0, os.path.join(BASE, "tools"))
    import dart_lookup
    path = dart_lookup.CORP_CODE_CACHE_PATH
    if not os.path.exists(path):
        print("종목코드 캐시가 없어 DART에서 받아온다 (최초 1회)...")
        dart_lookup.build_corp_code_cache(api_key(), path=path)
    for row in csv.DictReader(io.open(path, encoding="utf-8")):
        if row.get("ticker") != ticker:
            continue
        name = row.get("name") or row.get("corp_name") or ticker
        return name, row["corp_code"]
    sys.exit("data/dart_corp_codes.csv 에 %s 없음 — 상장 종목 코드인지 확인하라" % ticker)


def fetch(key, code, year):
    """연결(CFS) 우선, 없으면 별도(OFS). 일시 오류는 3회까지 재시도."""
    last = {}
    for div in ("CFS", "OFS"):
        for _ in range(3):
            url = "%s?crtfc_key=%s&corp_code=%s&bsns_year=%s&reprt_code=11011&fs_div=%s" % (
                API, key, code, year, div)
            last = json.loads(urllib.request.urlopen(url, timeout=30).read().decode("utf-8"))
            if last.get("status") == "000":
                return last["list"]
            time.sleep(1.5)
    return None


def num(x):
    s = str(x).replace(",", "")
    return int(s) if s.lstrip("-").isdigit() else 0


def grab(rows, pats, divs, col, exclude=r"차감전"):
    """계정명 정규식 합계. 기본적으로 '법인세비용차감전순이익'처럼
    접두가 겹치는 계정을 배제한다 — 이걸 빼먹으면 유효세율이 2배로 튄다."""
    total = 0
    for it in rows:
        if it["sj_div"] not in divs:
            continue
        name = it["account_nm"]
        if exclude and re.search(exclude, name):
            continue
        if any(re.search(p, name) for p in pats):
            total += num(it.get(col))
    return total


def snapshot(rows, col):
    eq = grab(rows, EQUITY, ("BS",), col)
    debt = grab(rows, DEBT, ("BS",), col)
    cash = grab(rows, CASH, ("BS",), col)
    return eq, debt, cash


def measure(ticker, year, key):
    name, code = corp_code(ticker)
    cur = fetch(key, code, str(year))
    prv = fetch(key, code, str(int(year) - 1))
    if cur is None:
        return {"ticker": ticker, "name": name, "error": "DART 조회 실패 (%s)" % year}

    e1, d1, c1 = snapshot(cur, "thstrm_amount")   # 당기말
    e0, d0, c0 = snapshot(cur, "frmtrm_amount")   # 전기말
    ic1, ic0 = (e1 + d1 - c1) / E, (e0 + d0 - c0) / E

    inc = ("CIS", "IS")
    op = grab(cur, OP, inc, "thstrm_amount")
    ni = grab(cur, NI, inc, "thstrm_amount")
    tax = grab(cur, TAX, inc, "thstrm_amount")
    pre = grab(cur, PRETAX, inc, "thstrm_amount", exclude=None) or (ni + tax)

    if not (op and pre and e1 and e0):
        return {"ticker": ticker, "name": name, "error": "필수 계정 누락 — 적자/지주/금융업 여부 확인"}

    etr = tax / pre
    nopat = op * (1 - etr) / E
    avg_ic = (ic1 + ic0) / 2
    avg_eq = (e1 + e0) / 2 / E

    out = {
        "ticker": ticker, "name": name, "year": int(year), "unit": "억원",
        "op": round(op / E), "ni": round(ni / E), "pretax": round(pre / E),
        "effective_tax_rate": round(etr * 100, 1),
        "nopat": round(nopat), "avg_invested_capital": round(avg_ic),
        "avg_equity": round(avg_eq),
        "roic": round(nopat / avg_ic * 100, 1) if avg_ic else None,
        "roe": round(ni / E / avg_eq * 100, 1) if avg_eq else None,
    }
    # 직전 연도 — 방향을 보려면 최소 2개년이 필요하다
    if prv:
        p1, pd1, pc1 = snapshot(prv, "thstrm_amount")
        p0, pd0, pc0 = snapshot(prv, "frmtrm_amount")
        pic = ((p1 + pd1 - pc1) + (p0 + pd0 - pc0)) / 2 / E
        pop = grab(cur, OP, inc, "frmtrm_amount")
        pni = grab(cur, NI, inc, "frmtrm_amount")
        ptax = grab(cur, TAX, inc, "frmtrm_amount")
        ppre = grab(cur, PRETAX, inc, "frmtrm_amount", exclude=None) or (pni + ptax)
        if pop and ppre and pic:
            petr = ptax / ppre
            pnopat = pop * (1 - petr) / E
            out["prev"] = {
                "year": int(year) - 1,
                "roic": round(pnopat / pic * 100, 1),
                "roe": round(pni / E / ((p1 + p0) / 2 / E) * 100, 1),
                "nopat": round(pnopat), "avg_invested_capital": round(pic),
            }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tickers", nargs="+")
    ap.add_argument("--year", default="2025")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    key = api_key()
    results = [measure(t, a.year, key) for t in a.tickers]

    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    for r in results:
        print("=" * 62)
        if r.get("error"):
            print("%s (%s)  %s" % (r["name"], r["ticker"], r["error"]))
            continue
        p = r.get("prev", {})
        print("%s (%s)  단위 억원" % (r["name"], r["ticker"]))
        print("  영업이익 %-8s 순이익 %-8s 유효세율 %s%%" % (r["op"], r["ni"], r["effective_tax_rate"]))
        print("  NOPAT %-11s 평균투하자본 %s" % (r["nopat"], r["avg_invested_capital"]))
        if p:
            print("  ROIC  %s%% → %s%%   (전년 NOPAT %s / IC %s)"
                  % (p["roic"], r["roic"], p["nopat"], p["avg_invested_capital"]))
            print("  ROE   %s%% → %s%%" % (p["roe"], r["roe"]))
        else:
            print("  ROIC  %s%%   ROE %s%%" % (r["roic"], r["roe"]))


if __name__ == "__main__":
    main()
