---
name: odoo-reorder-request
description: >
  Odoo ERP(odoo MCP)에서 재고 부족 품목을 자동 감지해 발주요청서를 만들고,
  사람 승인 후 실제 발주(purchase.order)를 등록하고 담당자에게 알릴 때
  사용. "재고 부족 발주 처리해줘", "부족 품목 발주요청서 만들어줘", "발주
  승인하고 등록해줘", "재주문 처리" 같은 표현이 있을 때 트리거. 이 스킬은
  ProcessGPT/BPMN을 호출하지 않는다 — odoo-purchase-report(문서화)와
  odoo-bulk-partner-import의 생성 패턴(중복확인 후 생성)을 재사용하는
  오케스트레이터 스킬이다.
---

# Odoo 재주문 요청 오케스트레이터 (odoo-reorder-request)

## 역할

"감지 → 문서화 → 사람 승인 → 실제 등록 → 알림" 5단계를 지휘하되, 각
단계의 실제 일은 가능하면 이미 있는 스킬/패턴에 위임한다. 오케스트레이터
스킬은 스스로 로직을 다 구현하지 않는다는 것이 이 스킬의 교육 포인트다.

## 절차

### 1. 진단 (감지)
```
mcp__odoo__search_records(model="stock.warehouse.orderpoint",
  fields=["product_id","product_min_qty","product_max_qty"])
mcp__odoo__search_records(model="product.product",
  fields=["name","default_code","qty_available"])
```
`qty_available < product_min_qty`인 품목을 부족으로 판정한다 (판정 기준은
`odoo-procurement-dashboard`와 동일하게 유지한다 — 기준이 스킬마다
다르면 안 된다).

### 2. 문서화 — odoo-purchase-report에 위임
부족 품목 목록을 "발주요청서" 제목으로 `Skill(odoo-purchase-report)`
(또는 그 스킬이 쓰는 것과 같은 docx 위임 절차)에 넘겨 문서를 만든다.
**이 스킬 안에서 새로 문서 서식을 짜지 않는다.**

### 3. 사람 승인 (필수 — 건너뛰지 않는다)
2에서 만든 목록을 사용자에게 제시하고, 어떤 품목을 몇 개, 어느 공급사에
발주할지 명시적으로 확인받는다 (AskUserQuestion 또는 자유 응답). **승인
없이는 4단계로 넘어가지 않는다.**

### 4. 실제 발주 등록 — odoo-bulk-partner-import의 생성 패턴을 재사용
`odoo-bulk-partner-import`에서 쓴 "생성 전 확인 → 생성 → 결과 기록" 패턴을
그대로 적용한다:
```
mcp__odoo__create_record(model="purchase.order",
  values={"partner_id": <승인된 공급사 id>, "date_order": <오늘>})
mcp__odoo__create_record(model="purchase.order.line",
  values={"order_id": <위에서 만든 id>, "product_id": <품목 id>,
          "product_qty": <승인된 수량>})
```
생성 결과(주문번호, id)를 사용자에게 확인시킨다.

### 5. 알림
```
mcp__odoo__post_message(model="purchase.order", res_id=<4에서 만든 id>,
  body="<발주 요약>. 담당자 확인 요청")
```

## 절대 하지 않는 것

- **승인(3단계) 없이 4단계(실제 발주 생성)로 자동으로 넘어가지 않는다.**
  재고 부족을 감지했다고 곧바로 발주가 나가면 안 된다.
- ProcessGPT/BPMN 프로세스를 호출하지 않는다 — 이 절차가 조직의 정식
  업무로 굳어지면 그때는 `bpmn-process-generation-skill`로 승격을
  검토하되, 그건 이 스킬의 책임 밖이다.
- 2단계에서 문서 서식을 새로 짜지 않는다 — 항상 `odoo-purchase-report`가
  쓰는 docx 위임 절차를 재사용한다.
