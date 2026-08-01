---
name: odoo-purchase-report
description: >
  Odoo ERP(odoo MCP)의 발주(purchase.order) 현황을 거래처별/기간별로
  집계해서 워드(docx) 문서 보고서로 만들 때 사용. "발주 현황 보고서 만들어줘",
  "구매 실적 문서로 뽑아줘", "거래처별 발주 집계", "발주요청서 만들어줘"
  같은 표현이 있을 때 트리거. 이 스킬은 데이터 집계까지만 담당하고, 문서
  포맷팅은 반드시 docx 스킬에 위임한다 — 이 스킬 안에 워드 서식 코드를
  직접 넣지 않는다.
---

# Odoo 발주 현황 리포트 (odoo-purchase-report)

## 역할

`purchase.order`를 집계해서 표를 만들고, **표현(문서 생성)은 docx 스킬에
위임**한다. 도메인 로직(무엇을 집계할지)과 표현 로직(어떻게 문서로 보여줄지)을
분리하는 것이 이 스킬의 핵심 교육 포인트다.

## 절차

1. **데이터 집계** — `mcp__odoo__aggregate_records`를 호출한다.
   ```
   model="purchase.order"
   groupby=["partner_id"]
   aggregates=["amount_total:sum", "__count"]
   domain=사용자가 기간을 지정하면 [["date_order", ">=", "..."], ["date_order", "<=", "..."]] 추가
   ```
   결과를 "거래처 | 발주 건수 | 발주 합계"표로 정리한다.

2. (선택) 품목 단위 상세가 필요하면 `mcp__odoo__search_records`를
   `purchase.order.line`에 대해 `fields=["order_id","product_id","product_qty","price_subtotal"]`로
   조회해 붙인다.

3. **문서 생성은 docx 스킬에 위임한다.** 이 스킬은 표 데이터를 준비만 하고,
   실제 워드 문서 조립(제목/표/스타일)은 `Skill(docx)`를 호출해 맡긴다.
   전달할 내용:
   - 문서 제목: "발주 현황 보고서" (또는 사용자가 "발주요청서"를 요청했으면
     그 이름과 목적에 맞는 제목·문구로)
   - 표: 1에서 만든 집계 결과 (+ 2의 상세, 있으면)
   - 생성 일자, 대상 기간

4. 결과 파일 경로를 사용자에게 알려주고, 이어서 실제 발주 등록/승인까지
   필요하면 `odoo-reorder-request` 스킬로 넘길 수 있다고 안내한다.

## 하지 않는 것

- 워드 문서의 스타일/표 서식을 이 스킬 안에서 직접 코딩하지 않는다 — 항상
  docx 스킬에 위임한다 (pptx 요청이 오면 pptx 스킬에, 이 환경에 pptx 스킬이
  없으면 사용자에게 `find-skills`로 설치를 안내하거나 docx로 대체할지 물어본다).
- 발주 레코드를 만들거나 바꾸지 않는다 (읽기 전용 집계) — 실제 발주 생성은
  `odoo-reorder-request`의 책임이다.
