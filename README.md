# process-gpt-tutorial-odoo

Odoo ERP MCP × Claude Skill 실습 튜토리얼. [ProcessGPT](https://github.com/uengine-oss/process-gpt)
학습 자료의 일부로, `docs/tutorials/odoo` 위치에 git submodule로 연결됩니다.

"스킬이 뭔지" 처음 배우는 학생/실무자를 위해, Odoo MCP를 프롬프트로 직접
호출해보는 실습부터 시작해 그 절차를 실제 Claude Skill(SKILL.md)로 승격하는
전 과정을 다룹니다. 모든 예제는 실제 Odoo 샌드박스(`uengine.odoo.com`)에
대고 실행하고 검증했습니다 — 결과 로그는 [`odoo-skill-workbook.md`](odoo-skill-workbook.md)에
그대로 남아 있습니다.

**이 저장소는 단독으로 클론해도 바로 실습 가능하도록 구성되어 있습니다** —
`.claude/skills/`에 스킬 5종이 이미 놓여 있고, `.mcp.json`에 `odoo` MCP
서버 템플릿이 들어 있습니다. 실제 API 키만 채우면 됩니다(아래 "빠른 시작").

## 구성

| 경로 | 내용 |
|---|---|
| [`odoo-skill-workbook.md`](odoo-skill-workbook.md) | 실습 워크북 본문 — 난이도 ★~★★★★★ 5개 시나리오, 각 시나리오의 실제 실행 로그(✅ 실행 검증) 포함 |
| [`.claude/skills/`](.claude/skills/) | 워크북을 따라 만든 실제 Claude Skill 5종 (`SKILL.md`) — Claude Code가 이 경로를 자동으로 스캔합니다 |
| [`.mcp.json`](.mcp.json) | `odoo` MCP 서버 연결 템플릿 (플레이스홀더만 있고 실제 키는 없음) |
| [`outputs/`](outputs/) | 실습 중 실제로 생성된 산출물(docx 보고서 2건) |

## 스킬 5종

| # | 스킬 | 난이도 | 요약 |
|---|---|---|---|
| 1 | [`odoo-contact-lookup`](.claude/skills/odoo-contact-lookup/SKILL.md) | ★ | 거래처 연락처 조회 (읽기 전용) |
| 2 | [`odoo-bulk-partner-import`](.claude/skills/odoo-bulk-partner-import/SKILL.md) | ★★ | 엑셀 기반 거래처 대량 등록 (중복체크·부분실패 허용) |
| 3 | [`odoo-purchase-report`](.claude/skills/odoo-purchase-report/SKILL.md) | ★★★ | 발주 현황 집계 → docx 스킬에 위임해 보고서 생성 |
| 4 | [`odoo-procurement-dashboard`](.claude/skills/odoo-procurement-dashboard/SKILL.md) | ★★★★ | 재고·발주·협력사 현황을 모아 dataviz 스킬로 대시보드화 |
| 5 | [`odoo-reorder-request`](.claude/skills/odoo-reorder-request/SKILL.md) | ★★★★★ | 재고 부족 감지 → 문서화 → 사람 승인 → 실발주 등록까지, 앞의 스킬들을 재사용하는 오케스트레이터 |

## 빠른 시작 (이 저장소를 단독으로 클론했을 때)

```bash
git clone https://github.com/uengine-oss/process-gpt-tutorial-odoo.git
cd process-gpt-tutorial-odoo
```

1. **`.mcp.json`을 채운다.** 이미 파일이 있으니 플레이스홀더만 실제 값으로
   바꾸면 됩니다 (Odoo Settings → Developer Tools에서 API 키 발급):
   ```json
   {
     "mcpServers": {
       "odoo": {
         "env": {
           "ODOO_DB": "<your-odoo-db-name>",
           "ODOO_URL": "https://<your-instance>.odoo.com",
           "ODOO_USER": "<your-odoo-login-email>",
           "ODOO_API_KEY": "<your-odoo-api-key>",
           "ODOO_YOLO": "true",
           "ODOO_MCP_ENABLE_METHOD_CALLS": "true"
         },
         "args": ["mcp-server-odoo"],
         "command": "uvx",
         "enabled": true,
         "transport": "stdio"
       }
     }
   }
   ```
   - `ODOO_YOLO=true`는 이 워크북 실습을 위해 전체 모델에 read/write/create/
     unlink를 여는 설정입니다. **운영 인스턴스에는 쓰지 말고**, 실습 전용
     샌드박스에서만 사용하세요. 실제 값을 커밋하지 않도록 주의하세요
     (필요하면 `.mcp.json`을 로컬에서 `git update-index --skip-worktree`
     처리하거나, 개인 fork에서만 값을 채우세요).
   - `uvx`가 없다면 [uv](https://docs.astral.sh/uv/)를 먼저 설치해야 합니다.
2. **Claude Code로 이 폴더를 연다.** `.mcp.json`의 `odoo` 서버를 신뢰할지
   물으면 승인합니다 — 승인해야 MCP 툴이 붙습니다.
3. **스킬이 이미 붙어 있는지 확인.** `.claude/skills/`가 이 폴더 바로 아래에
   있으므로 Claude Code가 자동으로 5개 스킬을 인식합니다. "반도체부품
   공급업체 연락처 찾아줘"처럼 쳐서 `odoo-contact-lookup`이 바로 트리거되는지
   확인하세요.
4. **`odoo-skill-workbook.md`를 열고 시나리오 1부터 그대로 따라간다.**

## process-gpt(메인 저장소)의 submodule로 쓰는 경우

`docs/tutorials/odoo`에 이 저장소가 submodule로 연결되어 있습니다. 이
경로 아래의 `.claude/skills/`, `.mcp.json`은 **메인 저장소를 열었을 때는
자동으로 스캔되지 않습니다** (Claude Code는 프로젝트 루트의 `.claude/skills/`,
`.mcp.json`만 봅니다). 메인 저장소에서 이 스킬들을 바로 써보고 싶다면
`docs/tutorials/odoo/.claude/skills/odoo-*`를 프로젝트 루트
`.claude/skills/`로 복사하고, `.mcp.json`에 `odoo` 서버 블록을 병합하세요.

## 라이선스

이 저장소는 [uengine-oss/process-gpt](https://github.com/uengine-oss/process-gpt)의
학습 자료로 공개됩니다.
