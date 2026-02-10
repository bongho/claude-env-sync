---
description: 특정 시점으로 설정 복원
argument-hint: <COMMIT_SHA>
---

특정 커밋 시점으로 설정을 복원합니다.

사용자가 커밋 SHA를 제공하지 않았다면, 먼저 `sync_history`를 호출하여 이력을 보여주고 복원할 시점을 선택하게 하세요.

SHA가 확정되면 MCP 도구 `sync_restore`를 `commit_sha` 파라미터와 함께 호출합니다.

복원 결과를 보여주고, 복원 전 상태가 자동 백업되었음을 안내하세요.
