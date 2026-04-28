# 테스팅 규칙 (Testing Rules)

## TDD 원칙: RED → GREEN → IMPROVE
1. **RED**: 실패하는 테스트를 먼저 작성
2. **GREEN**: 테스트를 통과하는 최소한의 코드 작성
3. **IMPROVE**: 리팩토링 (테스트는 여전히 통과해야 함)

## 커버리지 기준
- 전체 코드 커버리지: **80% 이상** 목표
- 핵심 비즈니스 로직: **90% 이상**
- 유틸리티/헬퍼: **70% 이상**
- 커버리지 측정: `pytest-cov`, `istanbul/c8`, `go test -cover`

## 테스트 유형별 가이드

### 단위 테스트 (Unit Tests)
- 함수/메서드 단위로 격리 테스트
- 외부 의존성은 mock/stub 처리
- Given-When-Then 패턴 사용
- 테스트 함수명: `test_<기능>_<조건>_<결과>` 형식
- 경계값, 예외 케이스 포함

### 통합 테스트 (Integration Tests)
- 모듈 간 상호작용 검증
- DB, API 등 외부 시스템과의 연동 테스트
- 테스트 데이터 fixture 사용, 테스트 후 정리(cleanup)

### E2E 테스트
- 핵심 사용자 시나리오 커버
- Playwright/Cypress 사용
- CI/CD 파이프라인에 포함

## DS/ML 테스트 기준

### 데이터 테스트
- 스키마 검증: 컬럼 타입, nullable, 범위
- 분포 검증: 기대 분포와의 차이 (KS test, chi-square)
- 데이터 누수 검증: train/test 분할 시 시간 기반 확인
- 결측치 비율 임계치 설정

### 모델 테스트
- **회귀 테스트**: 새 모델 성능 ≥ 기존 모델 성능 (메트릭별)
- **일관성 테스트**: 동일 입력 → 동일 출력 (deterministic)
- **편향성 테스트**: 보호 속성(성별, 인종 등) 기반 성능 차이 검증
- **스트레스 테스트**: 극단값, 누락값, 대용량 입력 처리

### 파이프라인 테스트
- DAG 무결성 검증
- 중간 단계 출력 검증
- 재현성: random_seed 고정 후 결과 일치 확인

## 테스트 프레임워크
- Python: `pytest` + `pytest-cov` + `pytest-mock`
- TypeScript: `vitest` 또는 `jest`
- Go: `testing` + `testify`
- E2E: `playwright`

## CI/CD 통합
- PR 머지 전 모든 테스트 통과 필수
- 커버리지 리포트 자동 생성
- 성능 테스트: 응답 시간, 메모리 사용량 회귀 체크
