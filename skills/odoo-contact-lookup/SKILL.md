---
name: odoo-contact-lookup
description: >
  Odoo ERP(odoo MCP)에 등록된 거래처/고객/협력사 연락처를 조회할 때 사용.
  "거래처 연락처 찾아줘", "고객 정보 조회", "협력사 연락처", "이 회사 담당자
  이메일 알려줘", "메일/전화 등록 안 된 거래처", "res.partner 조회" 같은
  표현이 있을 때 트리거. 조회 전용(read-only) — 데이터를 만들거나 바꾸지
  않는다. 대량 등록이 필요하면 odoo-bulk-partner-import 스킬로 넘긴다.
---

# Odoo 거래처 연락처 조회 (odoo-contact-lookup)

## 역할

`mcp__odoo__search_records`를 `res.partner` 모델에 대해 호출해, 이름/이메일/
전화/휴대폰을 **항상 같은 필드 조합**으로 조회하고 표로 정리한다. 이 스킬의
값어치는 새로운 기능이 아니라, "매번 어떤 필드를 요청할지"를 사람마다 다르게
정하지 않도록 고정하는 데 있다.

## 절차

1. 사용자의 자연어 조건을 Odoo domain 필터로 변환한다.
   - "이름에 OO 들어간 거래처" → `[["name", "ilike", "OO"]]`
   - "이메일 등록 안 된 거래처" → `[["email", "=", false]]`
   - "회사(법인)만" → `[["is_company", "=", true]]`
   - 조건이 여러 개면 리스트를 이어 붙인다 (Odoo domain은 기본 AND).

2. 다음 파라미터로 `mcp__odoo__search_records`를 호출한다.
   ```
   model="res.partner"
   domain=<1에서 만든 domain>
   fields=["name", "email", "phone", "is_company"]
   limit=사용자가 명시하지 않으면 20
   ```
   > 실측 노트: `mobile` 필드는 이 odoo MCP 서버에서
   > `Invalid field 'mobile' in request` 에러로 거부된다(2026-08-01 확인).
   > 휴대폰 번호가 꼭 필요하면 `fields=["__all__"]`로 전체 필드를 받아
   > 실제로 존재하는 키인지 먼저 확인한 뒤 좁혀 쓴다.

3. 결과를 표로 정리해서 보여준다. 회사(`is_company=true`)와 개인 담당자를
   구분해서 보여주면 더 읽기 좋다. `email`/`phone`이 `false`(미등록)인 경우
   "미등록"으로 표시한다.

4. 결과가 0건이면 domain을 그대로 보여주고 조건을 완화할지 물어본다
   (오탈자·부분일치 문제인 경우가 많다).

## 하지 않는 것

- 레코드 생성/수정/삭제 — 이건 이 스킬의 책임이 아니다. 여러 건을 새로
  등록해야 하면 `odoo-bulk-partner-import` 스킬을 쓰라고 안내한다.
- 집계(합계/건수) — `odoo-purchase-report`처럼 `aggregate_records`가
  필요한 요청이면 해당 스킬로 넘긴다.
