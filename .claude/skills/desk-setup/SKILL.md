---
name: desk-setup
description: DPIC 데스크를 처음 쓸 때 한 번 실행한다. API 키(DART·FRED) 발급 안내와 저장, 실호출 검증, 종목코드 캐시 생성, 관심 산업의 컨센서스 수집까지 끝내고 다음에 무엇을 할지 알려준다. 설치·세팅·시작·처음·키 등록·환경 준비·체험 시작에 사용.
---

# desk-setup — 처음 한 번

> **PLUS FUTURE AI ANTI PLATFORM · DPIC 데스크**

이 데스크를 처음 쓰는 사람이 **막히지 않고 끝까지 가게** 하는 것이 이 스킬의 전부다.
새로 계산하지 않는다 — 이미 있는 `tools/` 스크립트를 순서대로 부르고, 실패하면
**어디서 왜 멈췄는지 지목**한다.

---

## 0. 먼저 알아야 할 것

### 이 저장소는 두 가지 방식으로 쓰인다

```
① git clone 해서 그 폴더에서 실행     data/ · runs/ 가 저장소 안에 쌓인다
② 플러그인으로 설치                   코드는 읽기 전용, 산출물은 사용자 프로젝트에 쌓인다
```

경로는 `tools/paths.py` 가 알아서 갈라준다. **어느 쪽인지 먼저 확인하고 안내 문구를 맞춘다.**

```bash
python -c "import sys;sys.path.insert(0,'tools');import paths;print(paths.data_dir())"
```

②라면 스크립트 경로 앞에 `${CLAUDE_PLUGIN_ROOT}/` 를 붙여 호출한다.
아래 명령은 ① 기준으로 적혀 있다.

### 절대 하지 말 것

| 금지 | 이유 |
|---|---|
| **키 값을 화면에 출력** | 발표·화면공유 중일 수 있다. 길이와 마스킹만 보여준다 |
| `pip install` 실행 | 서드파티 의존성이 **없다**. 표준 라이브러리만 쓴다 |
| 실패를 삼키고 다음 단계로 | 뒤에서 조용히 틀린 값이 나온다 |
| 키 없이 부분 진행 | 반쪽 상태가 제일 디버깅하기 어렵다 |

---

## 1. 단계

### [0] 환경 확인

```bash
python --version
```

`3.9` 이상이면 된다. **`pip install` 은 필요 없다** — 이 사실을 사용자에게 명시한다.
없다고 착각하고 requirements.txt 를 찾는 사람이 많다.

### [1] API 키

```bash
python tools/env_keys.py check
```

- 종료코드 `0` (`OK`) → [2]로
- 종료코드 `1` (`MISSING:...`) → 출력된 온보딩 메시지를 **그대로 보여주고** 키를 받는다

받을 때 이 안내를 함께 준다.

```
DART  https://opendart.fss.or.kr
      회원가입 → 인증키 신청 → 이메일 인증. 즉시 발급, 무료.
      공시 원문·재무제표·업종코드에 쓴다. 이 데스크의 모든 근거가 여기서 나온다.

FRED  https://fred.stlouisfed.org/docs/api/api_key.html
      계정 만들고 My Account → API Keys. 즉시 발급, 무료.
      환율·금리 맥락에만 쓴다. 32자 소문자 영숫자다.
```

키를 받으면 저장한다. **명령에 키가 들어가므로 실행 후 값을 다시 언급하지 않는다.**

```bash
python tools/env_keys.py save DART_API_KEY=<받은값> FRED_API_KEY=<받은값>
```

사용자가 "나중에" 라고 하면 **중단한다.** 어느 키가 없어서 멈췄는지 명시하고,
키 없이 볼 수 있는 것을 안내한다(아래 [5] 참조).

### [2] 키 실호출 검증 — 저장만 하고 끝내지 않는다

저장은 성공해도 키가 틀렸으면 다음 단계에서 엉뚱한 곳에서 터진다.
**두 키를 따로** 두드려서 어느 쪽이 문제인지 분리한다.

```bash
python - <<'PY'
import sys, json, urllib.request, urllib.error
sys.path.insert(0, 'tools')
import env_keys
v = env_keys.read_env_file(env_keys.DEFAULT_ENV_PATH)

d = v.get('DART_API_KEY', '')
try:
    u = ("https://opendart.fss.or.kr/api/list.json?crtfc_key=%s"
         "&bgn_de=20260801&end_de=20260813&page_count=1" % d)
    st = json.loads(urllib.request.urlopen(u, timeout=20).read().decode())['status']
    print('DART', 'OK' if st == '000' else 'FAIL status=%s' % st)
except Exception as e:
    print('DART FAIL', type(e).__name__)

f = v.get('FRED_API_KEY', '')
print('FRED 키 형식', 'OK' if len(f) == 32 and f.isalnum() and f.islower()
      else 'FAIL (32자 소문자 영숫자여야 함, 현재 %d자)' % len(f))
try:
    u = ("https://api.stlouisfed.org/fred/series/observations?series_id=DGS10"
         "&api_key=%s&file_type=json&limit=1" % f)
    urllib.request.urlopen(u, timeout=20).read()
    print('FRED OK')
except urllib.error.HTTPError as e:
    print('FRED FAIL HTTP', e.code)
except Exception as e:
    print('FRED FAIL', type(e).__name__)
PY
```

실패 시 안내:

```
DART status=010    등록되지 않은 키. 이메일 인증을 마쳤는지 확인
DART status=020    사용 한도 초과. 하루 20,000건
FRED HTTP 400      키가 32자 소문자 영숫자가 아니다. 따옴표를 같이 붙여넣지 않았는지 확인
```

### [3] 종목코드 캐시

```bash
python tools/dart_lookup.py induty-code 062040
```

`data/dart_corp_codes.csv` 가 없으면 DART에서 상장사 약 3,900건을 한 번에 받아 만든다.
**이 파일은 저장소에 커밋하지 않는다**(생성물이라 gitignore). clone 직후 없는 게 정상이다.

### [4] 관심 산업의 컨센서스 수집 ★ 여기를 건너뛰면 다음 단계가 전멸한다

저장소에 커밋된 `data/consensus.csv` 는 **씨앗**이다. 여기 없는 종목은
`company-screen` 이 판정 대상에서 제외하므로, 다른 산업을 보려면 먼저 수집해야 한다.

캐시에 이미 있는 산업을 보여주고 고르게 한다.

```bash
python tools/industry_cache.py list-industries
python tools/industry_cache.py get-industry "<고른 산업>"
```

캐시에 없는 산업이어도 **막지 않는다.** 그 경우 종목을 모르는 상태이므로,
`/dpic-desk:industry-screen` 이 DART로 유니버스를 구성하게 두고 [5]로 넘어간다.

캐시에 있으면 그 티커들로 수집한다.

```bash
python tools/fetch_consensus.py <ticker> <ticker> ...
```

- 종목당 **1.2초** 딜레이가 있다. 20종목이면 약 30초 — 진행 중임을 알린다
- **기존 행은 보존하고 병합**한다. 다른 산업 데이터가 날아가지 않는다
- `cov=0` 은 최근 3개월 내 컨센서스가 없다는 뜻이다. 정상이며, G1 게이트에서 걸러진다

수집 후 몇 종목이 커버리지 3 이상인지 알려준다. **5개 미만이면 그 산업은
`industry-screen` 의 G1 게이트에서 REJECT 된다** — 미리 말해준다.

### [5] 다음에 할 일

```
/dpic-desk:industry-screen     산업 판정 → 01-industry.json
/dpic-desk:company-screen      종목 전수 판정 → 02-companies.json
/dpic-desk:pro_tackler         태클 심사 → 04-tackle.json
/dpic-desk:desk-head           최종 보고서 → report.html
/dpic-desk:desk-run            위 순서를 한 번에 (오케스트레이터)
```

저장소를 clone해서 쓰는 경우엔 `dpic-desk:` 접두어 없이 `/industry-screen` 이다.

**3단계(조정률 산출)에서 멈추는 것은 정상이다.** 그 계산을 하는 `core/` 는 미구현이라
`desk-run` 이 수동 입력을 안내하고 정지한다. 버그가 아니다.

키가 없거나 수집을 건너뛴 사람에게는 **완성된 실행 기록**을 보여준다.

```
runs/2026-08-13_전력기기·중전기/   01~04 + report.html   전력기기 7개사 전수 심사
runs/2026-08-13_discover/          산업 discover 결과
```

---

## 2. 마지막에 출력할 요약

```
DPIC 데스크 준비 완료

  [0] Python           ✓ 3.12.9
  [1] API 키           ✓ DART · FRED  (.env 저장)
  [2] 실호출 검증       ✓ DART status=000 · FRED 200
  [3] 종목코드 캐시     ✓ 3,982건
  [4] 컨센서스          ✓ 조선·조선기자재 6종목 수집 (커버리지 3+ 6개)

→ /dpic-desk:industry-screen 으로 시작하세요.
```

기호: `✓` 완료 · `⏸` 건너뜀 · `✕` 실패(사유 명시)

**`✕` 가 하나라도 있으면 다음 단계를 권하지 않는다.** 무엇을 고쳐야 하는지만 말한다.
