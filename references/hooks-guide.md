# Hook 가이드 (Hooks Guide)

## Hook 타입 개요

### 1. PreToolUse
- **시점**: 도구 실행 전
- **용도**: 위험한 작업 차단/경고, 승인 프로세스
- **반환**: `approve` (허용), `block` (차단 + 메시지), 미반환 (기본 동작)
- **예시**: git push 전 리뷰 리마인더, 프로덕션 DB 쿼리 경고

### 2. PostToolUse
- **시점**: 도구 실행 후
- **용도**: 자동 포맷팅, 타입 체크, 린트 경고
- **반환**: stdout 내용이 사용자에게 표시
- **예시**: Python 파일 저장 후 Black 포맷 체크, TypeScript 저장 후 tsc 체크

### 3. SessionStart
- **시점**: 세션 시작 시
- **용도**: 환경 초기화, 이전 세션 상태 로드
- **예시**: 최근 작업 내역 로드, 환경 변수 확인

### 4. SessionEnd (Stop)
- **시점**: 세션 종료 시
- **용도**: 상태 저장, 정리 작업, 변경 파일 요약
- **예시**: 변경 파일 목록 출력, 세션 요약 저장

### 5. PreCompact
- **시점**: /compact 실행 전
- **용도**: 중요 컨텍스트 보존
- **예시**: 핵심 결정사항, 실험 결과 별도 저장

### 6. Notification
- **시점**: 알림 이벤트 발생 시
- **용도**: 외부 시스템 알림
- **예시**: Slack 알림, 이메일 알림

## 현재 활성화된 Hook

### PostToolUse: 코드 포맷 경고
- Python (`.py`): Black 포맷 체크 (`black --check`)
- TypeScript (`.ts`, `.tsx`): Prettier 체크 (`prettier --check`)
- Go (`.go`): gofmt 체크 (`gofmt -l`)

### PostToolUse: 타입 체크 경고
- Python: mypy 체크 (변경 파일만)
- TypeScript: tsc --noEmit (변경 파일만)

### PreToolUse: Git Push 리뷰 리마인더
- `git push` 전 변경사항 리뷰 완료 확인 리마인더

### Stop: 변경 파일 요약
- 세션 종료 시 변경된 파일 목록 출력

## Hook 설정 위치
- `~/.claude/settings.json`의 `hooks` 섹션
- 프로젝트별: `.claude/settings.json`의 `hooks` 섹션

## Hook 스크립트 위치
- 전역 스크립트: `~/.claude/scripts/hooks/`
- 프로젝트별: `.claude/scripts/hooks/`

## Hook 작성 규칙
- 실행 시간 **5초 이내** (타임아웃 방지)
- 실패 시 graceful fallback (세션 중단 방지)
- 사이드 이펙트 최소화
- 로그는 stderr로 출력 (stdout은 사용자에게 표시)

## 고급 Hook 패턴

### 패턴 1: 위험 명령 경고 (PreToolUse)
| 트리거 | 감지 패턴 | 동작 |
|--------|----------|------|
| 파괴적 명령 | `sudo`, `rm -rf`, `chmod 777` | 경고 + 확인 요청 |
| DB 위험 | `DROP TABLE`, `TRUNCATE`, `DELETE FROM` (WHERE 없음) | 차단 + 대안 제시 |
| Git 위험 | `git push -f`, `git reset --hard` | 경고 + 백업 권장 |
| 프로덕션 | 프로덕션 DB/API 접근 패턴 | 경고 + security-reviewer 제안 |

### 패턴 2: Plan 모드 자동 진입 제안 (PreToolUse)
| 트리거 키워드 | 제안 |
|--------------|------|
| "구현", "implement", "build" | `planner` 에이전트 호출 제안 |
| "리팩토링", "refactor", "restructure" | `architect` 에이전트 호출 제안 |
| "마이그레이션", "migrate" | 계획 수립 + 롤백 전략 제안 |

### 패턴 3: 자동 컨텍스트 전환 제안
| 감지 키워드 | 제안 모드 |
|------------|----------|
| "분석", "EDA", "데이터" | `data-analysis` 모드 |
| "배포", "deploy", "release" | `deploy` 모드 |
| "실험", "A/B", "하이퍼파라미터" | `experiment` 모드 |
| "배우고 싶어", "설명해줘", "이해가" | `learning` 모드 |

## 권장 Hook 구현 목록

### 높은 우선순위
| Hook | 설명 | 구현 상태 |
|------|------|----------|
| 의존성 감사 | 새 패키지 추가 시 npm audit/pip-audit | 미구현 |
| 시크릿 스캔 | 커밋 전 크레덴셜 패턴 검사 | 미구현 |
| 테스트 강제 | 코드 변경 후 관련 테스트 실행 제안 | 미구현 |

### 중간 우선순위
| Hook | 설명 | 구현 상태 |
|------|------|----------|
| BQ 비용 경고 | 예상 스캔량 1TB 초과 시 경고 | 미구현 |
| 파일 크기 경고 | 800줄 초과 파일 생성 시 분할 제안 | 미구현 |
| 문서 동기화 | API 변경 시 README 업데이트 리마인더 | 미구현 |

### 낮은 우선순위
| Hook | 설명 | 구현 상태 |
|------|------|----------|
| 커밋 메시지 검증 | Conventional Commits 형식 체크 | 미구현 |
| 브랜치명 검증 | 네이밍 컨벤션 체크 | 미구현 |
