# Scenario & Risk Protocol (Bull / Base / Bear)

CASE D에는 적용하지 않는다. CASE A/B/C의 모든 최종 후보 기업에 대해 Bull Case만 쓰는 것을
금지한다 — 반드시 Bull/Base/Bear **3개 시나리오**를 숫자로 제시한다.

## 1. 3-Scenario 테이블 (기업별 필수)

| Scenario | 핵심 가정 | Earnings(참조 연도) | Applied Multiple | Target Price | Upside/Downside |
|---|---|---|---|---|---|
| Bull | [무엇이 기대보다 잘될 때] | | | | |
| Base | [현재 desk-head 추정] | | | | |
| Bear | [무엇이 기대보다 나빠질 때] | | | | |

- Bull/Bear는 Base와 다른 임의의 숫자를 넣는 게 아니라, **가정을 바꾼 결과**여야 한다
  (예: 수주 가정 물량 변화, Margin 가정 변화, Multiple 재평가 여부 변화). 어떤 가정이
  바뀌었는지 명시한다.
- 가능하면 Bear Case는 **실제 유사 사례(precedent)**를 인용해서 근거를 강화한다
  (두산 보고서가 SMR 리스크를 설명할 때 NuScale UAMPS 프로젝트 취소 사례와 PPI 상승
  데이터를 인용한 방식). 유사 사례가 없으면 그렇다고 명시하고 정성적 논리로 대체한다.

## 2. Thesis-Breaking Trigger (기업별 필수, 최소 1개)

Bull/Base/Bear 테이블만으로는 부족하다. "**무엇이 발생하면 이 Investment Thesis가
깨지는지**"를 명시적인 조건문으로 최소 1개 이상 정의한다.

```
Thesis Invalidation Trigger:
  IF [관측 가능한 구체적 사건/지표] THEN Investment Thesis 무효
  예) IF 26년까지 확정 수주 파이프라인의 50% 이상이 지연/취소 THEN 가스터빈 성장
      스토리의 핵심 전제가 깨짐 → 재평가 필요
```

이 트리거는 `case-branching.md`의 청산/재평가 로직과도 연결되며, Quality Gate에서
"Bull/Base/Bear가 숫자로 검증되었는가" 항목의 통과 조건이다.

## 3. Bear Case 감당 가능성 판단 (Independent Review 질문 7과 연결)

Bear Case의 Downside가 아래 중 하나라도 해당하면 **BUY를 유지할 수 없다**:
- Downside가 −30% 이상이고 발생 확률이 낮지 않다고 판단되는 경우
- Bear Case의 트리거 조건이 이미 일부 관측되고 있는 경우

이 경우 등급을 HOLD로 낮추거나, Bear 요인이 해소될 시점까지 Investment Horizon을
조정하거나, NO INVESTMENT로 전환할 수 있다 — 어느 쪽을 택했는지와 근거를 리포트에
명시한다.
