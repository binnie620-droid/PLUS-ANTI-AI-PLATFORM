"""
컨센서스 수집기 — FnGuide 라이선스 없이 data/consensus.csv 를 만든다.

출처: 네이버 금융 종목분석 (navercomp.wisereport.co.kr).
      이 페이지의 컨센서스 블록은 FnGuide가 공급하는 데이터다.
      즉 "FnGuide 컨센서스 필수 활용" 요건을 우회가 아니라 그대로 충족한다.

수집 필드 (contracts/pipeline.md §consensus.csv 와 동일):
    ticker, name, consensus_tp, coverage_count, last_updated

추가 진단 필드는 data/consensus_extra.csv 로 따로 뺀다 (계약 스키마를 오염시키지 않음):
    investment_opinion, eps, per

사용:
    python tools/fetch_consensus.py 005930 000660 034020
    python tools/fetch_consensus.py --from-file data/target_tickers.txt
"""
import csv
import io
import os
import re
import sys
import time
import urllib.request

BASE = "https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={}"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
DELAY_SEC = 1.2          # 서버 예의. 줄이지 말 것
TIMEOUT = 25

OUT_MAIN = os.path.join("data", "consensus.csv")
OUT_EXTRA = os.path.join("data", "consensus_extra.csv")


def fetch(ticker):
    req = urllib.request.Request(BASE.format(ticker), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        raw = r.read()
    for enc in ("utf-8", "euc-kr", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def flatten(html):
    txt = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", txt)


def num(s):
    """1,234.5 -> 1234.5 / 빈값·'-' -> None"""
    if s is None:
        return None
    s = s.replace(",", "").strip()
    if not s or s in ("-", "N/A"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def parse(txt, ticker):
    """컨센서스 블록에서 5+3 필드를 뽑는다. 못 뽑으면 None 을 채우고 사유를 남긴다."""
    out = {
        "ticker": ticker, "name": None, "consensus_tp": None,
        "coverage_count": None, "last_updated": None,
        "investment_opinion": None, "eps": None, "per": None,
        "note": "",
    }

    # 종목명 — "삼성전자 005930 SamsungElec KOSPI" 패턴에서 티커 직전 토큰
    m = re.search(r"([가-힣A-Za-z0-9()\.&]+)\s+" + ticker + r"\s", txt)
    if m:
        out["name"] = m.group(1).strip()

    # 기준일 — [기준:2026.08.11]
    m = re.search(r"기준\s*:\s*(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})", txt)
    if m:
        y, mo, d = m.groups()
        out["last_updated"] = "{}-{:02d}-{:02d}".format(y, int(mo), int(d))

    # 컨센서스 본체.
    # 실제 DOM 순서:
    #   [헤더] 투자의견  목표주가(원)  EPS(원)  PER(배)  추정기관수
    #   [값]        4.04     491,875   47,821    5.01          24
    # 값 행이 헤더 마지막 단어("추정기관수") 바로 뒤에 온다.
    m = re.search(
        r"추정기관수\s+([\d.]+)\s+([\d,]+)\s+([\d,\-]+)\s+([\d.,\-]+)\s+(\d+)", txt)
    if m:
        out["investment_opinion"] = num(m.group(1))
        out["consensus_tp"] = int(num(m.group(2)) or 0) or None
        out["eps"] = num(m.group(3))
        out["per"] = num(m.group(4))
        out["coverage_count"] = int(m.group(5))
        return out

    # 폴백 — 목표주가가 '-'로 비어 있는 저커버리지 종목
    m = re.search(r"추정기관수\s+([\d.]+)\s+([\d,\-]+)\s+([\d,\-]+)\s+([\d.,\-]+)\s+(\d+)", txt)
    if m:
        out["investment_opinion"] = num(m.group(1))
        out["consensus_tp"] = int(num(m.group(2)) or 0) or None
        out["eps"] = num(m.group(3))
        out["per"] = num(m.group(4))
        out["coverage_count"] = int(m.group(5))
        if out["consensus_tp"] is None:
            out["note"] = "목표주가 미제시 (투자의견만 존재)"
        return out

    # 네이버 컨센서스는 "최근 3개월 이내 제시된 의견"만 집계한다.
    # 3개월간 리포트가 없으면 아래 문구가 나온다 — 파싱 실패가 아니라 커버리지 0이다.
    if "최근3개월 이내에 제시된 의견이 없습니다" in txt or "제시된 의견이 없습니다" in txt:
        out["coverage_count"] = 0
        out["note"] = "최근 3개월 내 의견 없음 — 커버리지 0 (G1 탈락)"
    elif "추정기관수" in txt:
        out["note"] = "추정기관수 헤더는 있으나 값 파싱 실패 — 페이지 구조 확인 필요"
    else:
        out["note"] = "컨센서스 블록 없음 (G1 탈락)"
    return out


def main(tickers):
    rows, extra = [], []
    for i, t in enumerate(tickers, 1):
        try:
            r = parse(flatten(fetch(t)), t)
        except Exception as e:
            r = {"ticker": t, "name": None, "consensus_tp": None,
                 "coverage_count": None, "last_updated": None,
                 "investment_opinion": None, "eps": None, "per": None,
                 "note": "fetch 실패: {}".format(type(e).__name__)}
        rows.append(r)
        cov = r["coverage_count"]
        status = "cov={:<3}".format(cov) if cov is not None else "MISS  "
        print("[{}/{}] {} {} tp={} {}".format(
            i, len(tickers), t, status,
            r["consensus_tp"] or "-", r["note"]), flush=True)
        if i < len(tickers):
            time.sleep(DELAY_SEC)

    os.makedirs("data", exist_ok=True)
    with io.open(OUT_MAIN, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ticker", "name", "consensus_tp", "coverage_count", "last_updated"])
        for r in rows:
            if r["coverage_count"] is None:
                continue          # 컨센 없는 종목은 애초에 대상이 아니다 (G1)
            w.writerow([r["ticker"], r["name"], r["consensus_tp"],
                        r["coverage_count"], r["last_updated"]])

    with io.open(OUT_EXTRA, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ticker", "investment_opinion", "eps", "per", "note"])
        for r in rows:
            w.writerow([r["ticker"], r["investment_opinion"], r["eps"],
                        r["per"], r["note"]])

    kept = sum(1 for r in rows if r["coverage_count"] is not None)
    print("\n수집 {}개 중 컨센 보유 {}개 -> {}".format(len(rows), kept, OUT_MAIN))
    print("진단 필드 -> {}".format(OUT_EXTRA))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--from-file":
        with io.open(args[1], encoding="utf-8") as f:
            tk = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    else:
        tk = args
    if not tk:
        print(__doc__)
        sys.exit(1)
    main(tk)
