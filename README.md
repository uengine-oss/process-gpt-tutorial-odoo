# process-gpt-tutorial-odoo

Odoo ERP MCP × Claude Skill 실습 튜토리얼. [ProcessGPT](https://github.com/uengine-oss/process-gpt)
학습 자료의 일부로, `docs/tutorials/odoo` 위치에 git submodule로 연결됩니다.

"스킬이 뭔지" 처음 배우는 학생/실무자를 위해, Odoo MCP를 프롬프트로 직접
호출해보는 실습부터 시작해 그 절차를 **수강생이 직접** Claude Skill(SKILL.md)로
승격하는 전 과정을 다룹니다. 난이도 ★ ~ ★★★★★ 5개 시나리오를 순서대로 따라가면
스킬 5개가 만들어지고, 뒤로 갈수록 앞에서 만든 스킬을 부품처럼 다시 씁니다.

👉 **본문: [`odoo-skill-workbook.md`](odoo-skill-workbook.md)**

## 구성

| 경로 | 내용 |
|---|---|
| [`odoo-skill-workbook.md`](odoo-skill-workbook.md) | 실습 워크북 본문 — 시나리오 5개 + 실습 데이터 지도 + 강사용 진행 노트 |
| [`materials/신규협력사.xlsx`](materials/신규협력사.xlsx) | 시나리오 2 실습용 엑셀 (신규 4 / 중복 1 / 실패 1행) |
| [`materials/seed/seed_workshop_data.py`](materials/seed/seed_workshop_data.py) | Odoo 샌드박스에 실습 데이터를 심는 스크립트 (여러 번 실행해도 안전) |
| [`materials/output/skills/`](materials/output/skills/) | **정답지** — 워크북대로 만들었을 때 나오는 SKILL.md 5종 |
| [`materials/output/`](materials/output/) | 참고 산출물 (docx 보고서 2건) |
| [`.mcp.json`](.mcp.json) | `odoo` MCP 서버 연결 템플릿 (플레이스홀더만, 실제 키 없음) |

> 📁 `materials/output/skills/`는 **정답지**입니다. 수강생이 먼저 직접 만들어 본 뒤
> 비교하도록 일부러 `.claude/skills/`가 아닌 곳에 두었습니다 — 그 경로에 두면
> Claude Code가 자동으로 인식해 버려서 "직접 만들기" 실습이 성립하지 않습니다.

## 스킬 5종 (정답지)

| # | 스킬 | 난이도 | 요약 |
|:-:|---|:-:|---|
| 1 | [`odoo-contact-lookup`](materials/output/skills/odoo-contact-lookup/SKILL.md) | ★ | 거래처 연락처 조회 (읽기 전용) |
| 2 | [`odoo-bulk-partner-import`](materials/output/skills/odoo-bulk-partner-import/SKILL.md) | ★★ | 엑셀 기반 거래처 대량 등록 (중복체크·부분실패 허용) |
| 3 | [`odoo-purchase-report`](materials/output/skills/odoo-purchase-report/SKILL.md) | ★★★ | 발주 현황 집계 → docx 스킬에 위임해 보고서 생성 |
| 4 | [`odoo-procurement-dashboard`](materials/output/skills/odoo-procurement-dashboard/SKILL.md) | ★★★★ | 재고·발주·협력사 현황을 모아 dataviz 스킬로 대시보드화 |
| 5 | [`odoo-reorder-request`](materials/output/skills/odoo-reorder-request/SKILL.md) | ★★★★★ | 재고 부족 감지 → 문서화 → 사람 승인 → 실발주 등록까지, 앞의 스킬들을 재사용하는 오케스트레이터 |

## 빠른 시작

```bash
git clone https://github.com/uengine-oss/process-gpt-tutorial-odoo.git
cd process-gpt-tutorial-odoo
```

### 1. Odoo 샌드박스를 준비한다

[odoo.com](https://www.odoo.com)에서 무료 인스턴스를 만들고 **Purchase / Inventory 앱을
설치**합니다. Settings → Developer Tools에서 API 키를 발급받습니다.

> 검증 환경: Odoo SaaS 19.4 (purchase / stock / account / mail 설치, 통화 KRW)

### 2. `.mcp.json`을 채운다

플레이스홀더만 실제 값으로 바꾸면 됩니다.

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

- `ODOO_YOLO=true`는 실습을 위해 전체 모델에 read/write/create/unlink를 여는
  설정입니다. **운영 인스턴스에는 쓰지 말고** 실습 전용 샌드박스에서만 쓰세요.
- 실제 값을 커밋하지 않도록 주의하세요
  (`git update-index --skip-worktree .mcp.json` 또는 개인 fork 사용).
- `uvx`가 없다면 [uv](https://docs.astral.sh/uv/)를 먼저 설치하세요.

> ⚠️ 이미 개인 설정(user scope)에 `odoo` MCP 서버를 등록해 뒀다면 이 저장소의
> 프로젝트 설정과 충돌해 **둘 다 안 붙을 수 있습니다.** `claude mcp list`에
> `[Conflicting scopes]` 경고가 뜨면 `claude mcp remove odoo -s project` 또는
> `-s user`로 하나를 정리하세요.

### 3. 실습 데이터를 심는다

```powershell
$env:ODOO_URL="https://<instance>.odoo.com"; $env:ODOO_DB="<db>"
$env:ODOO_USER="<login-email>"; $env:ODOO_API_KEY="<api-key>"
python materials/seed/seed_workshop_data.py
```

거래처 16건(공급사 8 / 고객 2 / 담당자 6), 품목 10건(재주문 규칙 포함),
발주 14건(총 60,500,000원)이 만들어집니다. 여러 번 실행해도 안전합니다.

### 4. Claude Code로 이 폴더를 열고 워크북을 시작한다

`.mcp.json`의 `odoo` 서버를 신뢰할지 물으면 승인합니다. 그다음
[`odoo-skill-workbook.md`](odoo-skill-workbook.md)의 "0. 준비"부터 그대로 따라가세요.

## process-gpt(메인 저장소)의 submodule로 쓰는 경우

`docs/tutorials/odoo`에 이 저장소가 submodule로 연결되어 있습니다. 이 경로 아래의
`.mcp.json`은 **메인 저장소를 열었을 때는 자동으로 읽히지 않습니다** (Claude Code는
프로젝트 루트의 `.mcp.json`, `.claude/skills/`만 봅니다). 메인 저장소에서 실습하려면
`.mcp.json`에 `odoo` 서버 블록을 병합하세요.

## 라이선스

이 저장소는 [uengine-oss/process-gpt](https://github.com/uengine-oss/process-gpt)의
학습 자료로 공개됩니다.
