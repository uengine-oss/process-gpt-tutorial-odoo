# process-gpt-tutorial-odoo

Odoo ERP MCP × Claude Skill 실습 튜토리얼. [ProcessGPT](https://github.com/uengine-oss/process-gpt)
학습 자료의 일부로, `docs/tutorials/odoo` 위치에 git submodule로 연결됩니다.

"스킬이 뭔지" 처음 배우는 학생/실무자를 위해, Odoo MCP를 프롬프트로 직접
호출해보는 실습부터 시작해 그 절차를 실제 Claude Skill(SKILL.md)로 승격하는
전 과정을 다룹니다. 모든 예제는 실제 Odoo 샌드박스(`uengine.odoo.com`)에
대고 실행하고 검증했습니다 — 결과 로그는 [`odoo-skill-workbook.md`](odoo-skill-workbook.md)에
그대로 남아 있습니다.

## 구성

| 경로 | 내용 |
|---|---|
| [`odoo-skill-workbook.md`](odoo-skill-workbook.md) | 실습 워크북 본문 — 난이도 ★~★★★★★ 5개 시나리오, 각 시나리오의 실제 실행 로그(✅ 실행 검증) 포함 |
| [`skills/`](skills/) | 워크북을 따라 만든 실제 Claude Skill 5종 (`SKILL.md`) |
| [`outputs/`](outputs/) | 실습 중 실제로 생성된 산출물(docx 보고서 2건) |

## 스킬 5종

| # | 스킬 | 난이도 | 요약 |
|---|---|---|---|
| 1 | [`odoo-contact-lookup`](skills/odoo-contact-lookup/SKILL.md) | ★ | 거래처 연락처 조회 (읽기 전용) |
| 2 | [`odoo-bulk-partner-import`](skills/odoo-bulk-partner-import/SKILL.md) | ★★ | 엑셀 기반 거래처 대량 등록 (중복체크·부분실패 허용) |
| 3 | [`odoo-purchase-report`](skills/odoo-purchase-report/SKILL.md) | ★★★ | 발주 현황 집계 → docx 스킬에 위임해 보고서 생성 |
| 4 | [`odoo-procurement-dashboard`](skills/odoo-procurement-dashboard/SKILL.md) | ★★★★ | 재고·발주·협력사 현황을 모아 dataviz 스킬로 대시보드화 |
| 5 | [`odoo-reorder-request`](skills/odoo-reorder-request/SKILL.md) | ★★★★★ | 재고 부족 감지 → 문서화 → 사람 승인 → 실발주 등록까지, 앞의 스킬들을 재사용하는 오케스트레이터 |

## 이 스킬을 내 프로젝트에서 써보려면

`skills/` 아래 원하는 폴더를 그대로 여러분 프로젝트의 `.claude/skills/`로
복사하세요. 전제는 프로젝트 `.mcp.json`에 `odoo` MCP 서버가 연결되어 있고,
`res.partner` / `product.product` / `stock.warehouse.orderpoint` /
`purchase.order` 모델에 접근 권한이 있어야 합니다.

```bash
cp -R skills/odoo-contact-lookup <your-project>/.claude/skills/
```

## 라이선스

이 저장소는 [uengine-oss/process-gpt](https://github.com/uengine-oss/process-gpt)의
학습 자료로 공개됩니다.
