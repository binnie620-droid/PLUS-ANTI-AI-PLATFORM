# Quality-Control Checklist

보고서를 **확정하기 직전** 반드시 이 체크리스트를 통과한다. 하나라도 미충족이면 확정하지
말고 해당 부분을 보완한 뒤 재검사한다. `output-schema.md`의 `quality_gate_passed`는 이
체크리스트를 전부 통과했을 때만 `true`로 표시한다.

## CASE A / B / C 체크리스트 (기업이 있을 때, 15개 항목)

- [ ] AI와 산업의 연결이 단순 Narrative에 그치지 않았는가? (계약/공시로 뒷받침되는가)
- [ ] 산업 성장 → 기업 Revenue 연결이 증명되었는가?
- [ ] Revenue → Earnings 연결이 설명되었는가? (매출은 늘어도 마진이 무너지는 경우는
      없는가)
- [ ] Earnings → Valuation 연결이 설명되었는가?
- [ ] 현재 주가가 반영하고 있는 기대 수준을 고려했는가? (Independent Review 질문 4)
- [ ] 목표주가 산식이 재현 가능한가? (계산식이 리포트에 명시적으로 드러나는가)
- [ ] Target Multiple의 근거가 있는가? (임의 입력이 아닌가)
- [ ] 투자기간(Investment Horizon)이 Catalyst와 연결되어 있는가?
- [ ] Bull/Base/Bear가 숫자로 검증되었는가? (정성적 서술만 있고 숫자가 없는 경우 실패)
- [ ] 핵심 숫자마다 출처가 있는가?
- [ ] Fact와 Assumption을 구분했는가? ([FACT]/[ESTIMATE]/[ASSUMPTION] 태그)
- [ ] 반대 논리를 충분히 검토했는가? (Independent Review 10문항 전부 답했는가)
- [ ] 투자하지 않는 것이 더 나은 선택인지 검토했는가? (자동 BUY로 흐르지 않았는가)
- [ ] 2~3개 기업일 경우 상대적인 투자매력도를 비교했는가?
- [ ] 최종 Top Pick/1위 선정 이유가 명확한가?

## CASE D 체크리스트 (0개 통과, 축소된 7개 항목 — 기업 관련 항목은 해당 없음)

- [ ] Skill 3의 반려지시서(또는 재구성한 탈락 근거)를 실제로 반영했는가?
- [ ] 산업 성장 논리에 출처가 있는가? (TAM/CAGR/수요 Driver)
- [ ] Fact와 Assumption을 구분했는가?
- [ ] "왜 지금 투자하지 않는가"에 대한 논리가 valuation/risk-reward 관점에서 구체적인가
      (단순히 "리스크가 있다"가 아니라 무엇이 부족한지)
- [ ] Monitoring Indicator와 재검토 Trigger가 관측 가능한 구체적 조건인가?
- [ ] **개별 기업 목표주가·등급이 리포트 어디에도 등장하지 않는가?** (등장하면 CASE D
      규칙 위반 — 즉시 삭제)
- [ ] Final Decision이 "NO INVESTMENT"이며 이를 적극적 판단으로 서술했는가?

## 공통 최종 확인

- [ ] `output-schema.md` 형식의 구조화 블록이 리포트 끝에 존재하는가?
- [ ] CASE 분류(A/B/C/D)가 Skill 3 통과 기업 수와 정확히 일치하는가? (SKILL.md Step 0
      표와 대조)
