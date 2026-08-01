# Odoo MCP × Claude Skill — 실습 워크북

> 대상: "스킬이 뭔지" 처음 배우는 학생/실무자
> 전제: 프로젝트 루트 `.mcp.json`에 `odoo` MCP 서버가 이미 연결되어 있고 (uengine.odoo.com 샌드박스),
> `res.partner`(거래처) · `product.product`(품목) · `stock.warehouse.orderpoint`(재주문 규칙) · `purchase.order`(발주)에
> 실습용 데이터가 이미 seed되어 있음(반도체 장비부품 조달 시나리오)

이 워크북은 **직접 프롬프트를 쳐서 MCP를 호출하는 실습**을 먼저 하고, 각 시나리오 끝에서
"방금 한 대화를 스킬로 만들어줘"라고 시켜 **skill-creator**로 실제 스킬을 만들어보는 순서로 구성되어 있습니다.
즉 이 문서는 정답을 읽는 문서가 아니라, 그대로 따라 치면서 진행하는 **실습지(워크북)**입니다.

> ✅ **이 문서는 실제로 실행되었습니다 (2026-08-01).** 아래 5개 스킬은 전부
> `.claude/skills/odoo-*/SKILL.md`로 실제 존재하고, `Skill` 도구로 직접 트리거해
> 진짜 `uengine.odoo.com` 샌드박스에 대고 MCP를 호출해봤습니다. 각 시나리오의
> **"✅ 실행 검증"** 절에 그때 나온 실제 결과(버그 1건 포함)를 그대로 남겼습니다.
> 이 세션에는 `skill-creator` 스킬 자체가 설치되어 있지 않아서(확인함), 대신
> "스킬로 승격하기" 프롬프트와 같은 의도로 이 세션이 직접 SKILL.md를
> 작성했습니다 — `skill-creator`가 설치되어 있다면 아래 프롬프트를 그대로
> 던지면 같은 결과를 자동으로 얻을 수 있습니다(부록 B 참고).
>
> **이 저장소는 그 실행 결과를 그대로 옮겨 만든 독립 저장소입니다.** 실행
> 당시엔 `process-gpt` 저장소의 `.claude/skills/odoo-*/`, `docs/ko/`,
> `docs/demo/`에 있었고, 이후 `docs/tutorials/odoo`에 git submodule로
> 연결하기 위해 이 저장소(`process-gpt-tutorial-odoo`)로 옮겼습니다. 본문 중
> "`.claude/skills/odoo-*/`" 같은 경로 언급은 **그 당시의 실행 로그**이니
> 그대로 두었습니다 — 지금 이 저장소에서는 [`.claude/skills/`](.claude/skills/)
> 아래에 그대로 있습니다(이 저장소를 단독으로 클론해도 Claude Code가 자동으로
> 인식하도록 일부러 이 경로에 뒀습니다). 다른 프로젝트에서 쓰려면
> `.claude/skills/odoo-*` 폴더를 그 프로젝트의 `.claude/skills/`로
> 복사하면 됩니다.

---

## 0. 시작 전 확인

Claude Code에서 그대로 쳐 보세요.

```
odoo MCP 연결됐는지 확인해줘. 등록된 모델 개수랑 res.partner 샘플 3개만 보여줘.
```

- `mcp__odoo__list_models` → 등록 모델 목록 (200개 안팎)
- `mcp__odoo__search_records(model="res.partner", limit=3)` → 거래처 샘플

정상이면 `uengine`, `SUP-02 반도체부품공급(주)`, `Azure Interior` 같은 이름이 보입니다. 안 보이면 `.mcp.json`의 `odoo` 서버가 아직 승인되지 않은 것이니 먼저 연결부터 승인하세요.

> ⚠️ 이 인스턴스는 `ODOO_YOLO=true`로 **전체 모델에 read/write/create/unlink가 열려 있는 실습용 샌드박스**입니다.
> 운영 인스턴스에 이 워크북을 그대로 적용하지 마세요 — 스킬을 만들 때는 반드시 모델별 필요한 권한만 쓰도록 좁혀야 합니다.

### 개념 먼저 — 프롬프트 / MCP / 스킬

| 층위 | 정체 | 예 | 재사용성 |
|---|---|---|---|
| **프롬프트** | 그때그때 치는 자연어 | "반도체부품 공급업체 연락처 찾아줘" | 없음 (매번 다시 침) |
| **MCP** | 시스템이 제공하는 **동사(도구)** | `search_records`, `create_record`, `aggregate_records` | 높음, 단 "한 번의 동작"뿐 |
| **스킬** | 그 동사들을 엮는 **절차 + 판단 기준 + 산출물 규격** | `odoo-contact-lookup`, `odoo-purchase-report` | 높음, 이름/자연어로 불러 씀 |

> **MCP는 "무엇을 할 수 있는가", 스킬은 "우리 회사에선 그걸 이렇게 한다".**

Odoo MCP 툴을 몇 번 조합해야 하는 일을, 매번 도메인 필터 문법과 순서를 다시 설명하며 프롬프트를 치는 건 낭비입니다.
"이 순서로, 이 조건으로, 이 포맷으로"를 한 번 적어두고 이름을 붙인 것이 **스킬**이고, 그 초안을 자동으로 만들어주는 것이 **skill-creator**입니다.

---

## 시나리오 1 — 거래처 연락처 조회 (난이도 ★)

**스킬명(가제)**: `odoo-contact-lookup`
**성격**: 읽기 전용, MCP 호출 1회. 스킬의 최소 형태.

### 실습

**Step 1.** 그대로 쳐보세요.

```
반도체부품 공급업체 연락처 찾아줘
```

Claude가 하는 일:
```
mcp__odoo__search_records(
  model="res.partner",
  domain=[["name", "ilike", "반도체"]],
  fields=["name", "email", "phone", "mobile"]
)
```

실제 결과 예시:
```
SUP-01 반도체부품공급(주) (장재형) — sup01@example.com
SUP-02 반도체부품공급(주)
```

**Step 2.** 조건을 바꿔서 한 번 더:

```
이번엔 이메일 등록 안 된 거래처만 뽑아줘
```

→ 같은 툴을 다른 domain(`[["email","=",false]]`)으로 다시 호출하는 걸 눈으로 확인합니다.

### 체크포인트
- [ ] `search_records`의 `domain`, `fields` 파라미터가 매번 손으로 다시 조립된다는 걸 확인했다
- [ ] 같은 질문을 팀원이 하면 매번 다른 필드 조합으로 나올 수 있다는 문제를 느꼈다

### ✅ 실행 검증 (2026-08-01)

`.claude/skills/odoo-contact-lookup/`을 실제로 만들고 `Skill` 도구로
"반도체부품 공급업체 연락처 찾아줘"를 그대로 트리거했습니다.

```
mcp__odoo__search_records(model="res.partner",
  domain=[["name","ilike","반도체"]],
  fields=["name","email","phone","mobile","is_company"])
→ Error: Invalid field 'mobile' in request
```

**실제로 버그가 하나 나왔습니다** — 초안 SKILL.md에 넣었던 `mobile` 필드가
이 odoo MCP 서버에서 거부됩니다. `fields`에서 `mobile`을 빼고 재호출:

```
mcp__odoo__search_records(model="res.partner",
  domain=[["name","ilike","반도체"]], fields=["name","email","phone","is_company"])
→ [{"name":"SUP-02 반도체부품공급(주)","email":"sup01@example.com","phone":false,"is_company":true},
    {"name":"SUP-01 반도체부품공급(주)","email":"jaeh@uengine.org","phone":false,"is_company":false}]
```

`.claude/skills/odoo-contact-lookup/SKILL.md`를 그 자리에서 고쳤습니다
(`mobile` 제거 + "실측 노트"로 원인을 남김). **테스트 → 실패 → 스킬 본문 수정 →
재테스트**, 이 사이클 자체가 스킬을 실제로 쓸모 있게 만드는 과정이라는 걸
보여주는 좋은 사례였습니다.

### 스킬로 승격하기

```
지금까지 한 것처럼 "거래처 연락처 조회"를 매번 같은 필드(이름/이메일/전화/휴대폰)로,
같은 우선순위로 보여주는 스킬을 만들고 싶어. skill-creator를 사용해서
odoo-contact-lookup 스킬 초안(SKILL.md)을 만들어줘.
트리거 description에는 "거래처 연락처", "고객 정보 찾아줘", "협력사 연락처" 같은
사용자들이 실제로 쓸 만한 표현을 5개 이상 넣어줘.
```

예상 SKILL.md 뼈대:
```
---
name: odoo-contact-lookup
description: 거래처/고객/협력사 연락처를 조회할 때 사용...(트리거 표현 5개+)
---
1) mcp__odoo__search_records(model="res.partner", domain=<사용자 조건>,
   fields=["name","email","phone","mobile","is_company"])
2) 회사/개인 구분해서 표로 정리해 출력
```

---

## 시나리오 2 — 신규 협력사 대량 등록 (난이도 ★★)

**스킬명(가제)**: `odoo-bulk-partner-import`
**성격**: **쓰기(write)** 스킬. 중복 체크 → 생성 → 결과 리포트.

### 실습

**Step 1.** 실습용 엑셀을 하나 준비합니다 (`신규협력사.xlsx`), 컬럼: `회사명 | 이메일 | 전화 | 담당자`. 5줄 정도 신규 업체를 적어 넣습니다 (예: "SUP-03 정밀가공(주)", "SUP-04 케이블어셈블리" 등 — 기존 SUP-01/02와 겹치지 않게).

**Step 2.** 그대로 쳐보세요.

```
이 엑셀에 있는 신규 협력사를 Odoo 거래처로 등록해줘.
이미 등록된 이름이면 건너뛰고, 등록 결과를 요약해줘.
[신규협력사.xlsx 첨부]
```

Claude가 하는 일 (행마다 반복):
```
1) mcp__odoo__search_records(model="res.partner", domain=[["name","=",행.회사명]])
   → 있으면 스킵
2) 없으면 mcp__odoo__create_record(
     model="res.partner",
     values={"name": 행.회사명, "email": 행.이메일, "phone": 행.전화, "is_company": true}
   )
3) 마지막에 "등록 N건 / 스킵 M건" 요약
```

### 체크포인트
- [ ] 중복 체크(`search_records`)를 매 행마다 먼저 하는 걸 확인했다 — 안 하면 같은 회사가 중복 생성된다
- [ ] 등록 후 다시 `search_records`로 실제 반영됐는지 확인해봤다

### ✅ 실행 검증 (2026-08-01)

`.claude/skills/odoo-bulk-partner-import/`를 실제로 만들고, 2행짜리 목록으로
`Skill` 도구를 트리거했습니다 — 1행은 신규(중복 없음), 1행은 기존 거래처와
이름이 같은 중복 테스트용:

```
행1 "SUP-03 테스트정밀가공(실습용)"
  → search_records(domain=[["name","=","SUP-03 테스트정밀가공(실습용)"]]) → 0건
  → create_record(res.partner, {...}) → 성공, id=10

행2 "SUP-01 반도체부품공급(주)" (기존과 동일 이름)
  → search_records(domain=[["name","=","SUP-01 반도체부품공급(주)"]]) → 1건(id=7) 발견
  → 스킵(중복)
```

**결과 요약**: 등록 1건(id 10) / 스킵(중복) 1건(id 7) / 실패 0건 — 설계한 대로
동작했습니다. 실습 후 정리를 위해 `mcp__odoo__delete_record(res.partner, 10)`으로
테스트 레코드를 삭제해 샌드박스를 원상태로 되돌렸습니다(스킬 4단계에
정의된 "실습용 레코드 정리" 그대로).

### 스킬로 승격하기

```
방금 한 "엑셀 → Odoo 거래처 대량 등록 + 중복 체크 + 결과 요약" 과정을
skill-creator로 스킬을 만들어줘. 이름은 odoo-bulk-partner-import.
컬럼명이 엑셀마다 다를 수 있으니 컬럼 매핑도 유연하게 처리하도록 넣어주고,
실패한 행이 있어도 나머지는 계속 진행하도록 해줘(부분 실패 허용).
```

### 학생에게 심어줄 것
- 사람이 엑셀 보며 한 줄씩 손으로 입력하던 걸 그대로 자동화한 것이 이 스킬의 원형
- **중복 체크 → 생성 → 실패해도 계속 → 결과 요약**, 이 4단계가 정해진 절차라는 게 스킬의 값어치

---

## 시나리오 3 — 발주 현황 집계 리포트 (난이도 ★★★)

**스킬명(가제)**: `odoo-purchase-report`
**성격**: **스킬이 다른 스킬(docx)을 부르는 첫 사례.**

### 실습

**Step 1.**

```
지금까지 발주 현황을 거래처별로 집계해서 워드 문서 보고서로 만들어줘
```

Claude가 하는 일:
```
1) mcp__odoo__aggregate_records(
     model="purchase.order",
     groupby=["partner_id"],
     aggregates=["amount_total:sum", "__count"]
   )
   → 실제 결과 예: SUP-01 반도체부품공급(주) — 1건, 4,500,000원

2) 이 표를 그대로 docx 스킬에 넘겨 워드 문서 생성
   (Claude가 "Skill(docx)"를 다시 호출하는 걸 도구 호출 로그에서 확인할 수 있음)
```

**Step 2.** 결과 문서를 열어 표/제목이 제대로 들어갔는지 확인합니다.

### 체크포인트
- [ ] 도구 호출 로그에서 `mcp__odoo__aggregate_records` 다음에 **docx 스킬 호출**이 별도로 일어나는 걸 확인했다
- [ ] "숫자 집계는 Odoo가, 문서 포맷은 docx 스킬이" 역할이 나뉘어 있다는 걸 이해했다

### ✅ 실행 검증 (2026-08-01)

`.claude/skills/odoo-purchase-report/`를 만들고 실제로 트리거했습니다.

```
mcp__odoo__aggregate_records(model="purchase.order", groupby=["partner_id"],
  aggregates=["amount_total:sum","__count"])
→ SUP-01 반도체부품공급(주): 1건, 4,500,000원

mcp__odoo__search_records(model="purchase.order.line",
  fields=["order_id","product_id","product_qty","price_subtotal"])
→ P00001 / SMPS-001 SMPS 파워모듈 / 45개 / 4,500,000원
```

이 표를 그대로 `Skill(docx)`에 위임해 실제 워드 문서를 생성했습니다 —
[`outputs/purchase-report.docx`](outputs/purchase-report.docx).
`scripts/office/validate.py`로 검증해 `All validations PASSED!`를 확인했습니다.

> 환경 노트: 이 저장소의 기본 `python3`(3.9.6)는 validate.py가 쓰는
> `match`/`case` 문법(3.10+)을 지원하지 않아 `SyntaxError`가 났습니다.
> `/opt/homebrew/bin/python3.11`로 바꾸고, 검증기가 요구하는 `defusedxml`을
> `pip install`한 뒤에야 통과했습니다 — docx 스킬을 처음 쓰는 팀이라면
> 미리 Python 버전을 확인해두면 이 삽질을 건너뛸 수 있습니다.

### 스킬로 승격하기

```
방금 한 "purchase.order를 거래처별로 집계 → docx로 보고서 생성" 과정을
skill-creator로 odoo-purchase-report 스킬로 만들어줘.
스킬 본문에는 "데이터는 aggregate_records로 직접 뽑고,
문서 생성은 반드시 docx 스킬에 위임한다"고 명시해줘 — 이 스킬 안에 워드 서식 코드를
직접 넣지 않도록.
```

### 학생에게 심어줄 것 — 스킬 조합의 기본형: **위임(delegate)**
> 원칙: 도메인 스킬(Odoo를 아는 것)과 표현 스킬(문서를 아는 것)을 한 덩어리로 만들지 마라.
> docx 스킬은 Odoo를 몰라야 다른 곳에도 재사용되고, `odoo-purchase-report`는 워드 문법을 몰라야
> "이번엔 PPT로" 라는 요청에 pptx 스킬로 갈아탈 수 있다.

---

## 시나리오 4 — 조달 현황 대시보드 PPT (난이도 ★★★★)

**스킬명(가제)**: `odoo-procurement-dashboard`
**성격**: 여러 모델 조회 + dataviz 스킬(차트) + pptx 스킬(슬라이드), **팬아웃(fan-out)** 패턴.

### 실습

**Step 1.**

```
재고 부족 품목, 발주 현황, 협력사 현황을 모아서 조달 현황 보고 PPT 만들어줘
```

Claude가 하는 일 (서로 다른 모델을 3번 조회):
```
1) 재고 부족: mcp__odoo__search_records(model="stock.warehouse.orderpoint")
   + mcp__odoo__search_records(model="product.product", fields=["name","default_code","qty_available"])
   → product_min_qty와 qty_available을 비교해 부족 품목 산출
     (실제 예: SMPS-001 SMPS 파워모듈, 현재고 5개 < 최소 10개 → 부족)

2) 발주 현황: mcp__odoo__aggregate_records(model="purchase.order", groupby=["partner_id"], ...)

3) 협력사 현황: mcp__odoo__search_records(model="res.partner", domain=[["supplier_rank",">",0]])

4) 위 3개 결과를 dataviz 스킬로 차트화 → pptx 스킬로 슬라이드 조립
```

**Step 2.** 생성된 PPT에서 "재고 부족" 슬라이드에 SMPS-001이 실제로 잡혔는지 확인합니다.

### 체크포인트
- [ ] MCP 호출이 이번엔 서로 다른 모델(orderpoint, product, purchase.order, partner) 3~4번 일어난 걸 확인했다
- [ ] 차트를 직접 그리라고 시키지 않고 dataviz 스킬에 맡겼다는 걸 확인했다

### ✅ 실행 검증 (2026-08-01)

`.claude/skills/odoo-procurement-dashboard/`를 만들고 실제로 트리거했습니다.
모델 4개를 순서대로 조회한 결과:

```
stock.warehouse.orderpoint × product.product 조인
  SMPS-001 SMPS 파워모듈  : 현재고 5  / 최소 10 / 최대 50  → 부족 (min 미달)
  실습용 무선 마우스      : 현재고 50 / 최소 10 / 최대 100 → 정상

aggregate_records(purchase.order, groupby=partner_id)
  SUP-01 반도체부품공급(주): 1건, 4,500,000원

search_records(res.partner, domain=[["supplier_rank",">",0]])
  SUP-01 반도체부품공급(주), SUP-02 반도체부품공급(주)
```

**실측으로 확인된 사실**: 이 환경에는 pptx 스킬이 설치되어 있지 않았습니다
(`find`로 `.claude/skills`를 뒤져도 없음). SKILL.md 5단계에 미리 적어둔
대로 대안(Artifact HTML)으로 방향을 틀어, dataviz 스킬을 로드해 그 스킬의
검증된 기본 팔레트(`references/palette.md`)와 마크 규칙(얇은 막대, 상태색은
카테고리색과 분리)을 그대로 적용한 대시보드를 만들었습니다. 결과물:
**[조달 현황 대시보드 (Artifact)](https://claude.ai/code/artifact/6ad1355b-024a-447d-b3cf-dca5ba215ae5)**.

> 학생에게 심어줄 것 (실측 추가): SKILL.md에 "pptx가 없으면 이렇게 한다"를
> 미리 적어뒀기 때문에, 실제로 pptx 스킬이 없는 상황을 만나도 스킬이 즉석에서
> 새로 판단하지 않고 **정해진 대안 경로**로 넘어갔습니다. 이게 스킬 본문에
> 예외 상황까지 미리 적어두는 이유입니다.

### 스킬로 승격하기

```
방금 한 "재고부족 + 발주현황 + 협력사현황을 모아 PPT로" 과정을
skill-creator로 odoo-procurement-dashboard 스킬로 만들어줘.
데이터 수집(Odoo MCP 3~4회)과 표현(dataviz, pptx 스킬 위임)을 스킬 본문에서
단계별로 분리해서 적어줘.
```

### 학생에게 심어줄 것
- 스킬은 MCP 호출 하나가 아니라 **여러 데이터 소스 + 여러 스킬을 순서대로 지휘하는 파이프라인**이 될 수 있다
- "부족 판정 기준"(min/max 비교)처럼 반복되는 계산 로직은 스킬이 매번 고정해줘야 사람마다 결과가 달라지지 않는다

---

## 시나리오 5 — 재고 부족 자동 감지 → 발주요청서 → 승인 후 실발주 (난이도 ★★★★★)

**스킬명(가제)**: `odoo-reorder-request`
**성격**: 오케스트레이터 스킬. **ProcessGPT/BPMN 연결 없이, 우리가 방금 만든 스킬들(시나리오 2, 3)을 그대로 재호출**해서 새 워크플로우를 조립하는 사례.

### 실습

**Step 1. 진단**

```
재고 부족 품목 체크해줘
```
```
mcp__odoo__search_records(model="stock.warehouse.orderpoint")
+ mcp__odoo__search_records(model="product.product", fields=["name","default_code","qty_available"])
→ SMPS-001 (SMPS 파워모듈): 현재고 5 / 최소 10 / 최대 50 → 40개 부족
```

**Step 2. 발주요청서 문서 생성 — 시나리오 3 스킬을 재사용**

```
부족한 품목으로 발주요청서 문서 만들어줘
```

여기서 Claude는 새로 문서 서식을 짜지 않고 **시나리오 3에서 이미 만든 `odoo-purchase-report`(또는 docx 스킬)를
그대로 다시 호출**해서 "발주요청서" 포맷으로 문서를 만듭니다. (스킬이 스킬을 부르는 순간)

**Step 3. 사람 승인**

```
SMPS-001 40개를 SUP-01 반도체부품공급(주)에 발주해줘. 나머지는 보류.
```

**Step 4. 실발주 등록 — 시나리오 2의 "생성 패턴"을 재사용**

```
mcp__odoo__create_record(
  model="purchase.order",
  values={"partner_id": 7, "date_order": "<오늘>"}
)
mcp__odoo__create_record(
  model="purchase.order.line",
  values={"order_id": <위에서 생성된 id>, "product_id": 1, "product_qty": 40}
)
```

시나리오 2에서 익힌 "생성 전 중복/유효성 체크 → 생성 → 결과 확인" 패턴을 그대로 다시 씁니다.

**Step 5. 알림**

```
mcp__odoo__post_message(model="purchase.order", res_id=<새 발주 id>,
  body="SMPS-001 40개 발주 등록 완료. 담당자 확인 요청")
```

### 체크포인트
- [ ] Step 2에서 새 문서 서식을 처음부터 짜지 않고 **기존 스킬(odoo-purchase-report)을 재호출**한 것을 확인했다
- [ ] Step 4의 생성 로직이 시나리오 2에서 만든 패턴(중복/유효성 체크 → 생성)과 동일하다는 걸 확인했다
- [ ] 승인 지점(Step 3)이 자동화 이전에 반드시 사람에게 물어보고 넘어간다는 걸 확인했다

### ✅ 실행 검증 (2026-08-01) — 5단계 전부 실제로 실행함

`.claude/skills/odoo-reorder-request/`를 만들고 끝까지 실제로 돌렸습니다.

```
[1] 진단 — 이미 만든 판정 기준 그대로 재사용
    SMPS-001 SMPS 파워모듈: 현재고 5 / 최소 10 / 최대 50 → 부족(발주 필요)

[2] 문서화 — 새로 서식을 짜지 않고 docx 위임 절차를 재사용
    Skill(docx) 호출 → docs/demo/odoo-skill-workbook-outputs/reorder-request.docx
    (validate.py → All validations PASSED!)

[3] 사람 승인 — 실제로 AskUserQuestion으로 사용자에게 물어봄
    "발주요청서(SMPS-001, 40개, SUP-01)를 실제 Odoo 샌드박스에 등록해서
     끝까지 실행해볼까요?" → 사용자가 "네, 실제로 등록"을 선택
    (스킬이 여기서 스스로 판단해 진행하지 않고, 실제로 사람 응답을 기다렸다는 점이 핵심)

[4] 실제 발주 등록 — odoo-bulk-partner-import의 생성 패턴 재사용
    mcp__odoo__create_record(purchase.order, {partner_id:7, date_order:"2026-08-01 09:00:00"})
      → 성공, P00002 (id=2)
    mcp__odoo__create_record(purchase.order.line,
      {order_id:2, product_id:1, product_qty:40})
      → 성공, id=3
    확인: get_record(purchase.order, 2) → amount_total 4,000,000원, state="draft"

[5] 알림
    mcp__odoo__post_message(purchase.order, 2,
      "SMPS-001 40개 발주 등록 완료. 담당자 확인 요청") → message_id 941
```

**이 실습은 uengine.odoo.com 샌드박스에 실제 발주(P00002, draft 상태)를
남겼습니다.** 정리(삭제)가 필요하면 `mcp__odoo__delete_record`로
`purchase.order` id 2를 지우면 되고, 다음 실습을 위해 재고 부족 상태로
그대로 남겨두고 싶다면(SMPS-001은 여전히 현재고 5로 부족 상태) 지우지 않고
두어도 됩니다 — draft 상태라 회계/재고에 실제 영향을 주지 않습니다.

### 스킬로 승격하기

```
방금 한 전체 과정 — 재고 부족 감지 → (odoo-purchase-report 스킬로) 발주요청서 생성 →
사람 승인 → (odoo-bulk-partner-import에서 쓴 생성 패턴으로) 실제 발주 등록 →
담당자 알림 — 을 skill-creator로 odoo-reorder-request 스킬로 만들어줘.

스킬 본문에 "문서 생성이 필요하면 odoo-purchase-report 스킬을 호출한다",
"승인 없이는 4단계(실발주 등록)로 넘어가지 않는다"는 두 가지를 명시적으로 적어줘.
```

### 학생에게 심어줄 것 — 오케스트레이터 스킬
- **오케스트레이터 스킬은 자기가 일을 다 하지 않는다.** 이미 만든 스킬을 부품처럼 다시 부른다
- 외부 엔진(ProcessGPT) 연결 없이도, **스킬 재사용만으로 새 워크플로우가 만들어진다**는 것이 이 시나리오의 핵심
- 승인 지점을 스킬이 미리 설계해둔다 — 재고 부족을 감지했다고 자동으로 발주까지 나가면 안 된다

> 참고: 이 절차가 조직 전체의 정식 업무가 되어 담당자·기한·결재선이 필요해지면,
> 그때는 `bpmn-process-generation-skill`로 ProcessGPT 프로세스로 승격시키는 다음 단계가 있습니다 —
> 이번 워크북에서는 스킬-스킬 재사용까지만 다룹니다.

---

## 난이도 사다리 한눈에

| # | 스킬(가제) | 난이도 | 새로 배우는 것 | 주 MCP 툴 | 부르는 다른 스킬 |
|---|---|---|---|---|---|
| 1 | `odoo-contact-lookup` | ★ | 필드/조건의 고정 | `search_records` | — |
| 2 | `odoo-bulk-partner-import` | ★★ | 중복체크 · 부분실패 허용 | `search_records`+`create_record` | (엑셀) |
| 3 | `odoo-purchase-report` | ★★★ | **스킬이 스킬을 호출(위임)** | `aggregate_records` | docx |
| 4 | `odoo-procurement-dashboard` | ★★★★ | 다중 모델 팬아웃 | `search_records`×3 + `aggregate_records` | dataviz, pptx |
| 5 | `odoo-reorder-request` | ★★★★★ | 스킬 재사용으로 오케스트레이션 | 위 전부 + `create_record`+`post_message` | odoo-purchase-report, odoo-bulk-partner-import 패턴 |

> 5개 전부 `.claude/skills/odoo-*/SKILL.md`로 실제 존재하며(가제가 아니라
> 실제 스킬명), `Skill` 도구로 직접 트리거해 2026-08-01에 끝까지 검증했습니다.
> 산출물 목록은 부록 D 참고.

---

## 부록 A — 스킬로 만들 값어치가 있는지 판별하는 3문항

1. **두 번 이상 같은 순서로 했는가?** (아니면 그냥 프롬프트로 충분)
2. **사람마다 결과가 달라지면 곤란한가?** (그렇다면 판단 기준을 스킬에 박아라 — 예: 재고 부족 판정 기준)
3. **다른 사람에게 설명해야 하는가?** (그 설명문이 곧 SKILL.md 본문이 된다)

## 부록 B — skill-creator에게 잘 시키는 법

- "방금 한 대화를 스킬로 만들어줘"만 던지지 말고, **트리거 표현(description에 들어갈 자연어 5개 이상)**과
  **위임할 다른 스킬 이름**을 프롬프트에서 직접 지정해주면 더 정확한 SKILL.md가 나온다
- 위 5개 시나리오 각각의 "스킬로 승격하기" 프롬프트가 그 예시
- skill-creator가 설치되어 있지 않다면 먼저 `find-skills`로 검색해서 설치부터 한다

> **실측 (2026-08-01)**: 이 워크북을 실행한 세션에는 `skill-creator`
> 스킬 자체가 설치되어 있지 않았습니다(`.claude/skills`, `~/.claude/skills`
> 전부 확인). 그래서 이번엔 세션이 "스킬로 승격하기" 프롬프트와 같은
> 의도로 SKILL.md 5개를 직접 작성해 `.claude/skills/odoo-*/`에 만들었고,
> `Skill` 도구로 실제로 트리거해 동작을 검증했습니다(위 각 시나리오의
> "✅ 실행 검증" 참고). skill-creator가 설치된 환경이라면, 손으로 짠 이
> SKILL.md들과 구조(frontmatter `name`/`description` + 절차 본문)가 거의
> 같은 결과를 자동으로 만들어 줄 것입니다 — 트리거 표현·위임 대상만
> 프롬프트에 명시해주면 됩니다.

## 부록 C — 흔한 안티패턴

| 안티패턴 | 왜 나쁜가 | 대신 |
|---|---|---|
| MCP 툴 하나를 그대로 감싼 스킬 | 스킬의 부가가치 0 | 최소 2~3 호출을 엮고 판단 기준을 넣어라 |
| 도메인 로직 + 문서 포맷을 한 스킬에 | PPT 요청 오면 통째로 재작성 | 도메인/표현 분리 (시나리오 3) |
| 승인 없이 대량 쓰기 | 잘못된 데이터가 그대로 들어감 | 중복/유효성 체크 → 사람 확인 → 실행 (시나리오 2, 5) |
| description이 한 줄 | 자연어로 트리거 안 됨 | 사용자가 쓸 표현을 5개 이상 나열 |

## 부록 D — 이번 실행에서 실제로 나온 산출물

| 산출물 | 위치 | 만든 스킬 |
|---|---|---|
| 스킬 5개 (SKILL.md) | [`.claude/skills/odoo-contact-lookup/`](.claude/skills/odoo-contact-lookup/), [`odoo-bulk-partner-import/`](.claude/skills/odoo-bulk-partner-import/), [`odoo-purchase-report/`](.claude/skills/odoo-purchase-report/), [`odoo-procurement-dashboard/`](.claude/skills/odoo-procurement-dashboard/), [`odoo-reorder-request/`](.claude/skills/odoo-reorder-request/) | (직접 작성 — skill-creator 부재) |
| MCP 연결 템플릿 | [`.mcp.json`](.mcp.json) (플레이스홀더만, 실제 키 제외) | — |
| 발주 현황 보고서 (docx) | [`outputs/purchase-report.docx`](outputs/purchase-report.docx) | odoo-purchase-report → docx |
| 발주요청서 (docx) | [`outputs/reorder-request.docx`](outputs/reorder-request.docx) | odoo-reorder-request → docx |
| 조달 현황 대시보드 (Artifact) | https://claude.ai/code/artifact/6ad1355b-024a-447d-b3cf-dca5ba215ae5 | odoo-procurement-dashboard → dataviz + Artifact |
| 실제 발주 레코드 | Odoo `purchase.order` **P00002**(id=2, draft) + `purchase.order.line`(id=3) + chatter 메시지(id=941) | odoo-reorder-request (사람 승인 후 실행) |

이 표 자체가 시나리오 5의 "산출물 핸드오프" 패턴의 예시이기도 합니다 —
스킬이 만든 파일 경로를 대화 맥락 대신 문서/표로 남겨, 다음 세션이나
다른 사람이 그대로 이어받을 수 있게 합니다.
