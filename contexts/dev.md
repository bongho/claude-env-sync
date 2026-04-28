# 개발 모드 (Development Mode)

## 우선순위
1. **작동** (Make it work) — 기능 구현 최우선
2. **올바름** (Make it right) — 엣지 케이스, 에러 처리
3. **깨끗함** (Make it clean) — 리팩토링, 네이밍 개선

## 행동 지침
- 코드 우선 출력 (설명은 최소화)
- 실행 가능한 코드 제공 (pseudo-code 지양)
- 변경 시 관련 테스트 함께 작성
- 빌드/테스트 통과 확인 후 완료 선언
- Tidy First: 수정할 코드 주변 정리 먼저 제안

## 에이전트 활용
- 복잡한 기능: `planner` → `architect` → 직접 구현
- 빌드 에러: `build-error-resolver` 위임
- 리팩토링 필요: `refactor-cleaner` 위임
- 보안 민감: `security-reviewer` 검토 요청

## 금지 사항
- 미검증 코드 제출 금지
- WIP 상태 방치 금지
- 기존 테스트 깨뜨리는 변경 금지
