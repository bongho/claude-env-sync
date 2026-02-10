---
allowed-tools: Bash(claude-sync init*)
description: 동기화 환경 초기화 (Git 저장소 생성)
argument-hint: [--remote URL]
---

`claude-sync init` 명령을 실행하세요.
사용자가 원격 저장소 URL을 제공하면 `--remote <URL>` 옵션으로 전달합니다.

!`claude-sync init`

완료 후 결과를 사용자에게 보여주세요:
- 동기화 저장소 경로
- 원격 저장소 설정 여부
- 다음 단계 안내 (`/claude-env-sync:sync-push`로 첫 동기화)
