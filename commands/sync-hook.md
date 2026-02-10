---
description: Shell hook 설치/제거
argument-hint: <install|uninstall> [--shell bash|zsh|auto]
---

Shell 시작 시 자동으로 `claude-sync pull`을 실행하는 hook을 관리합니다.

사용자 요청에 따라:
- **install**: MCP 도구 `sync_hook_install` 호출
- **uninstall**: MCP 도구 `sync_hook_uninstall` 호출

`shell` 파라미터: "bash", "zsh", "auto" (기본값: "auto" — 사용 가능한 RC 파일 자동 감지)

결과를 보여주고, 적용된 RC 파일 경로를 안내하세요.
