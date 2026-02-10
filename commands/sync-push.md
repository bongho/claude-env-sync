---
allowed-tools: Bash(claude-sync push*)
description: Claude 설정을 동기화 저장소로 push
argument-hint: [--message TEXT]
---

`claude-sync push` 명령을 실행하세요.
사용자가 커밋 메시지를 제공하면 `--message` 옵션으로 전달합니다.

!`claude-sync push`

결과에 따라 안내하세요:
- **시크릿 감지 시**: 발견된 시크릿 상세를 보여주고, 해당 파일에서 시크릿을 제거하라고 안내
- **성공 시**: 동기화된 파일 수와 커밋 여부를 보여줌
- **변경 없음**: 이미 최신 상태임을 알림
