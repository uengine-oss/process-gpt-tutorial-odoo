---
name: odoo-procurement-dashboard
description: >
  Odoo ERP(odoo MCP)의 재고 부족 품목·발주 현황·협력사 현황을 한 번에 모아
  조달(구매) 현황 대시보드를 만들 때 사용. "조달 현황 대시보드 만들어줘",
  "재고랑 발주 현황 같이 보여줘", "구매 현황 보고 자료", "재고 부족 품목
  대시보드" 같은 표현이 있을 때 트리거. 여러 Odoo 모델을 조회한 뒤 차트는
  dataviz 스킬에, 슬라이드/문서 조립은 pptx 스킬(있으면) 또는 docx
  스킬/Artifact에 위임한다.
---

# Odoo 조달 현황 대시보드 (odoo-procurement-dashboard)

## 역할

서로 다른 3~4개 모델을 조회해 하나의 대시보드로 합성하는 **팬아웃(fan-out)**
스킬이다. 이 스킬 자체는 숫자를 모으고 판정 기준을 적용할 뿐, 시각화와
문서 조립은 각각 전문 스킬에 위임한다.

## 절차

1. **재고 부족 품목 판정**
   ```
   mcp__odoo__search_records(model="stock.warehouse.orderpoint",
     fields=["product_id","product_min_qty","product_max_qty","warehouse_id"])
   mcp__odoo__search_records(model="product.product",
     fields=["name","default_code","qty_available"])
   ```
   두 결과를 `product_id`로 조인해서 `qty_available < product_min_qty`인
   품목을 "부족"으로, 부족 수량은 `product_max_qty - qty_available`로 계산한다.
   (이 비교 로직은 반드시 이 스킬이 고정한 기준대로 계산한다 — 매번 다른
   기준으로 판단하지 않는다.)

2. **발주 현황**
   ```
   mcp__odoo__aggregate_records(model="purchase.order",
     groupby=["partner_id"], aggregates=["amount_total:sum", "__count"])
   ```

3. **협력사 현황**
   ```
   mcp__odoo__search_records(model="res.partner",
     domain=[["supplier_rank", ">", 0]], fields=["name","email","phone"])
   ```

4. **시각화는 dataviz 스킬에 위임한다.** 1~3의 표를 넘기고, 최소
   "재고 부족 품목 막대그래프", "거래처별 발주 합계 막대그래프"를 요청한다.

5. **최종 산출물 조립**
   - pptx 스킬이 설치되어 있으면 그것에 위임해 슬라이드로 만든다.
   - 없으면(이 프로젝트 환경처럼) 사용자에게 알리고, 대안으로
     (a) docx 스킬로 문서 보고서를 만들거나
     (b) Artifact(HTML)로 대시보드 페이지를 만드는 것 중 선택하게 한다.
     둘 다 1~4에서 준비한 데이터/차트를 그대로 재사용한다.

## 하지 않는 것

- 차트를 이 스킬이 직접 그리지 않는다 (dataviz 스킬에 위임).
- 재고 부족 판정 기준을 사용자가 명시적으로 바꾸지 않는 한 임의로 다른
  기준(예: 안전재고 별도 계산)을 쓰지 않는다 — 기준이 바뀌면 이 SKILL.md를
  고쳐서 팀 전체에 반영해야 한다.
