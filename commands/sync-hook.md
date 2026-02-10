---
allowed-tools: Bash(claude-sync hook*)
description: Shell hook 설치/제거
argument-hint: <install|uninstall> [--shell bash|zsh|auto]
---

Shell 시작 시 자동으로 `claude-sync pull`을 실행하는 hook을 관리합니다.

사용자 요청에 따라:
- **install**: `claude-sync hook install` 실행
- **uninstall**: `claude-sync hook uninstall` 실행

`--shell` 옵션: "bash", "zsh", "auto" (기본값: "auto" — 사용 가능한 RC 파일 자동 감지)

!`claude-sync hook`

결과를 보여주고, 적용된 RC 파일 경로를 안내하세요.
