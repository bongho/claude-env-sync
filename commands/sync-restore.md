---
allowed-tools: Bash(claude-sync restore*), Bash(claude-sync history*)
description: 특정 시점으로 설정 복원
argument-hint: <COMMIT_SHA>
---

특정 커밋 시점으로 설정을 복원합니다.

사용자가 커밋 SHA를 제공하지 않았다면, 먼저 `claude-sync history`를 실행하여 이력을 보여주고 복원할 시점을 선택하게 하세요.

SHA가 확정되면 `claude-sync restore <SHA>`를 실행합니다.

!`claude-sync restore`

복원 결과를 보여주고, 복원 전 상태가 자동 백업되었음을 안내하세요.
