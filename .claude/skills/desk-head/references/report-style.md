# Report House Style — 증권사 리서치 보고서

`report.html` 을 만들 때 **이 파일의 CSS를 그대로 복사해 인라인으로 넣는다.**
디자인을 매번 새로 짜지 않는다 — 데스크 산출물은 회차가 달라도 같은 얼굴이어야 한다.

---

## 원칙 4가지

| | 원칙 | 이유 |
|---|---|---|
| 1 | **화이트 지면 · 네이비 액센트** | 리서치 보고서는 인쇄·PDF 배포를 전제한다. 어두운 패널은 잉크를 먹고 표를 읽기 어렵게 만든다 |
| 2 | **상승 적색 / 하락 청색** | 한국 시장 관행. 국제 관행(상승 녹색)을 쓰면 국내 독자가 순간 반대로 읽는다 |
| 3 | **좌측 사이드노트** | 각 문단 왼쪽에 결론 한 줄. **사이드노트만 위에서 아래로 읽어도 논리가 완성**되어야 한다 |
| 4 | **표가 본문이다** | 숫자는 우측 정렬 + `tabular-nums`. 헤더는 대문자 모노. 세로줄 없이 가로 헤어라인만 |

### 사이드노트 규칙

원본 리서치 보고서의 이중 레이어 설계를 따른다. 속독 독자를 위한 장치다.

```html
<div class="sn-row">
  <div class="sn">전망이 아니라 계약이다</div>
  <div class="sn-body">
    <p>6개 경쟁 종목이 "AI로 전력수요가 는다"는 산업 서술을 근거로 냈다…</p>
  </div>
</div>
```

- 사이드노트는 **주장의 요약**이지 제목이 아니다. 명사구가 아니라 **문장**으로 쓴다
- 문단마다 하나. 없으면 그 문단은 주장이 없는 문단이다
- 좁은 화면에서는 본문 위로 접힌다 (CSS가 처리)

---

## 색 토큰

| 토큰 | 라이트 | 용도 |
|---|---|---|
| `--nv` | `#14324F` | 하우스 네이비. 장 번호·강조·Rating 박스 |
| `--up` | `#C0392B` | **상승·긍정** (한국 관행) |
| `--dn` | `#1F5FA6` | **하락·부정** |
| `--ink` | `#141A20` | 본문 |
| `--paper` | `#FFFFFF` | 지면 |
| `--bg` | `#F2F4F6` | 페이지 배경 |
| `--rule` | `#E1E5E9` | 헤어라인 |

`[FACT]` / `[ESTIMATE]` / `[ASSUMPTION]` / `[Data unavailable]` 배지는
각각 네이비 / 앰버 / 회색 / 적색을 쓴다. **판정의 확실성이 색으로 보여야 한다.**

---

## CSS — 그대로 복사

```css
:root{
  --bg:#F2F4F6; --paper:#FFFFFF; --paper2:#F8F9FA;
  --ink:#141A20; --ink2:#3A454F; --muted:#697884; --faint:#98A4AE;
  --rule:#E1E5E9; --rule2:#C7CFD6;
  --nv:#14324F; --nv-bg:#EAEFF4;
  --up:#C0392B; --up-bg:#FBEDEB;
  --dn:#1F5FA6; --dn-bg:#EAF1F9;
  --est:#8A5A00; --est-bg:#FBF3E3;
  --f:'Pretendard Variable',Pretendard,'Apple SD Gothic Neo','Malgun Gothic',system-ui,sans-serif;
  --m:'JetBrains Mono','D2Coding',Consolas,ui-monospace,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0D1115; --paper:#151B21; --paper2:#1B2229;
  --ink:#E2E7EB; --ink2:#BEC7CF; --muted:#8D99A4; --faint:#6B7681;
  --rule:#28313A; --rule2:#3B4650;
  --nv:#6FA8D6; --nv-bg:#16283A;
  --up:#E27668; --up-bg:#341C19;
  --dn:#6FA8D6; --dn-bg:#16283A;
  --est:#D4A155; --est-bg:#332714;
}}
:root[data-theme="dark"]{
  --bg:#0D1115; --paper:#151B21; --paper2:#1B2229;
  --ink:#E2E7EB; --ink2:#BEC7CF; --muted:#8D99A4; --faint:#6B7681;
  --rule:#28313A; --rule2:#3B4650;
  --nv:#6FA8D6; --nv-bg:#16283A;
  --up:#E27668; --up-bg:#341C19;
  --dn:#6FA8D6; --dn-bg:#16283A;
  --est:#D4A155; --est-bg:#332714;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--f);
  font-size:16px;line-height:1.78;-webkit-font-smoothing:antialiased}
.sheet{max-width:1080px;margin:0 auto;background:var(--paper);
  padding:0 clamp(16px,4.5vw,56px) 90px;
  box-shadow:0 0 0 1px var(--rule)}
:focus-visible{outline:2px solid var(--nv);outline-offset:2px}

/* 사이드노트 2단 */
.sn-row{display:grid;grid-template-columns:1fr;gap:6px;margin:0 0 22px}
@media(min-width:900px){.sn-row{grid-template-columns:172px 1fr;column-gap:28px}}
.sn{font-size:.82rem;font-weight:700;color:var(--nv);line-height:1.5;
  padding-top:2px;border-left:2px solid var(--nv);padding-left:11px}
@media(max-width:899px){.sn{border-left:none;border-top:2px solid var(--nv);
  padding-left:0;padding-top:7px}}
.sn-body>*:last-child{margin-bottom:0}

/* 배지 */
.tg{font-family:var(--m);font-size:.6rem;letter-spacing:.05em;padding:1px 5px;
  border-radius:2px;vertical-align:1px;white-space:nowrap;font-weight:600}
.tg.f{background:var(--nv-bg);color:var(--nv)}
.tg.e{background:var(--est-bg);color:var(--est)}
.tg.a{background:var(--paper2);color:var(--muted)}
.tg.x{background:var(--up-bg);color:var(--up)}

/* 표 */
.tw{overflow-x:auto;margin:0 0 20px}
table{border-collapse:collapse;width:100%;font-size:.85rem;min-width:520px}
caption{text-align:left;font-family:var(--m);font-size:.6rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--faint);padding-bottom:7px;caption-side:top}
th,td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--rule);vertical-align:top}
thead th{font-family:var(--m);font-size:.61rem;letter-spacing:.09em;text-transform:uppercase;
  color:var(--muted);font-weight:600;border-bottom:1.5px solid var(--rule2);
  border-top:1.5px solid var(--ink);white-space:nowrap}
tbody tr:last-child td{border-bottom:1.5px solid var(--rule2)}
.num{font-family:var(--m);font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
tr.hi{background:var(--nv-bg)}
tr.hi td{font-weight:600}
.up{color:var(--up);font-weight:650}
.dn{color:var(--dn);font-weight:650}
.mu{color:var(--muted)}
```

---

## 금지

| 금지 | 이유 |
|---|---|
| 어두운 배경 패널을 지면 전체에 | 인쇄·PDF에서 잉크를 먹고 표가 안 읽힌다 |
| 상승에 녹색 | 국내 독자가 반대로 읽는다 |
| 표에 세로 괘선 | 가로 헤어라인만으로 충분하다. 세로줄은 밀도만 높인다 |
| 숫자 좌측 정렬 | 자릿수 비교가 불가능해진다 |
| 사이드노트에 명사구 | "리스크" 가 아니라 "계약 1건에 논리가 걸려 있다" 처럼 문장으로 |
| 외부 폰트·CSS·스크립트 | 자체 완결이어야 한다 |
