# 코딩 스타일 규칙 (Coding Style Rules)

## 공통 원칙
- **불변성 우선**: 가능하면 `const`, `final`, `readonly`, `frozen` 사용
- **순수 함수 선호**: 부수 효과 최소화, 같은 입력에 같은 출력
- **명시적 > 암시적**: 타입 힌트, 명확한 변수명, 매직 넘버 금지
- **주석**: 비직관적 로직에만 작성, "왜(Why)" 중심

## 파일/함수 크기 제한
- 파일: 200~800줄 (초과 시 모듈 분리 제안)
- 함수/메서드: 50줄 이내 (초과 시 추출 리팩토링)
- 클래스: 단일 책임 원칙 (SRP), 메서드 10개 이내 권장
- 중첩 깊이: 3단계 이내 (early return 패턴 사용)

## Python
- **스타일**: PEP8 준수, Black 포맷터 (line-length=88)
- **타입 힌트**: 함수 시그니처에 필수, `from __future__ import annotations`
- **임포트 순서**: stdlib → third-party → local (isort 사용)
- **문자열**: f-string 우선
- **예외 처리**: bare `except` 금지, 구체적 예외 타입 명시
- **데이터 클래스**: `dataclass` 또는 `pydantic.BaseModel` 사용
- **비동기**: I/O 바운드 작업에 `asyncio` 사용
- **네이밍**: snake_case (함수/변수), PascalCase (클래스), UPPER_CASE (상수)

## TypeScript
- **스타일**: Prettier 포맷터, ESLint strict 모드
- **타입**: `any` 사용 금지, strict TypeScript 설정
- **임포트**: 절대 경로 alias (`@/`) 사용
- **컴포넌트**: 함수형 컴포넌트 + hooks 패턴
- **상태 관리**: 불변 업데이트 패턴, spread operator 사용
- **에러 처리**: try-catch + 타입 가드, `unknown` 타입 사용
- **네이밍**: camelCase (함수/변수), PascalCase (컴포넌트/타입/인터페이스)

## Go
- **스타일**: `gofmt` + `golangci-lint`
- **에러 처리**: 에러는 반드시 처리, `_` 무시 금지
- **구조체**: 인터페이스 기반 설계, 작은 인터페이스 선호
- **고루틴**: context 기반 취소, goroutine leak 방지
- **네이밍**: exported는 PascalCase, unexported는 camelCase

## SQL (BigQuery/PostgreSQL)
- **포맷**: 키워드 대문자, 테이블/컬럼 snake_case
- **CTE 우선**: 서브쿼리보다 WITH 절 사용
- **SELECT ***: 프로덕션 코드에서 금지, 명시적 컬럼 나열
- **파티션/클러스터링**: BigQuery 테이블은 항상 고려
- **코스트 의식**: `LIMIT` 없는 탐색 쿼리 주의

## 새 라이브러리 도입
- 첫 줄에 버전 명시: `# requires: pandas>=2.0.0`
- 도입 사유와 대안 비교 간략 기술
- 라이선스 호환성 확인 (GPL 주의)

## 코드 구조
- 모듈화된 함수/클래스로 제안
- 순환 의존성 금지
- 레이어 분리: presentation → business logic → data access
