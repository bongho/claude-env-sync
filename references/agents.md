# 에이전트 규칙 (Agent Orchestration Rules)

## 위임 트리거
다음 조건에서 전문 에이전트에게 위임:

### 자동 위임 조건
- **복잡한 기능 요청** → `planner` + `architect` 순차 호출
- **보안 관련 변경** → `security-reviewer` 리뷰 요청
- **빌드/컴파일 에러** → `build-error-resolver` 위임
- **E2E 테스트 필요** → `e2e-runner` 위임
- **리팩토링 요청** → `refactor-cleaner` 위임
- **문서-코드 불일치** → `doc-updater` 위임

### DS/ML 위임 조건
- **데이터 품질 이슈** → `data-quality-reviewer` 위임
- **모델 성능 평가** → `model-evaluator` 위임
- **실험 추적** → `experiment-tracker` 위임
- **통계 분석** → `data-scientist` 위임
- **BQ 쿼리 최적화** → `bq-specialist` 위임
- **MLOps 파이프라인** → `mlops-engineer` 위임

### 전략/아키텍처 위임
- **AI 전략/교육** → `ai-pm` 위임
- **LLM 앱 개발** → `ai-product-engineer` 위임
- **AWS 설계** → `aws-solution-architect` 위임
- **백엔드 아키텍처** → `backend-architect` 위임

## 오케스트레이션 파이프라인

### 표준 파이프라인: RESEARCH → PLAN → IMPLEMENT → REVIEW → VERIFY
1. **RESEARCH**: 코드베이스 탐색, 요구사항 분석 (Explore agent)
2. **PLAN**: 구현 계획 수립, 파일/함수 식별 (planner agent)
3. **IMPLEMENT**: 코드 작성, TDD 적용 (직접 또는 tdd-guide)
4. **REVIEW**: 보안/품질 검토 (security-reviewer, code-reviewer skill)
5. **VERIFY**: 테스트 실행, 빌드 확인 (Bash)

### DS/ML 파이프라인: DATA → EXPERIMENT → EVALUATE → DEPLOY
1. **DATA**: 데이터 프로파일링, 품질 검증 (data-quality-reviewer)
2. **EXPERIMENT**: 모델 학습, 하이퍼파라미터 튜닝 (experiment-tracker)
3. **EVALUATE**: 성능 평가, 편향성 검증 (model-evaluator)
4. **DEPLOY**: 배포 전략, 모니터링 설정 (mlops-engineer)

## 모델 배정 전략

**기본 원칙**: 정적 사전 배정보다 **Advisor 패턴(동적 에스컬레이션)** 우선

| 전략 | 언제 | 구성 |
|------|------|------|
| Advisor 패턴 | 판단 품질이 중요한 복잡한 작업 | Sonnet executor + Opus advisor (max_uses=2~3) |
| Sonnet 단독 | 코드 구현, 테스트, 데이터 분석 | Sonnet |
| Haiku 단독 | 단순 조회, 포맷팅, 링크 검증 | Haiku |

**Advisor 패턴 적용 기준** (하나라도 해당하면 Sonnet + Opus advisor):
- 결과가 잘못되면 되돌리기 어려운 작업 (아키텍처 결정, 보안 분석)
- 연구 맥락 연결 판단이 필요한 작업 (학술 논문, Deep Reading)
- 여러 해석이 가능한 오픈엔드 전략 수립

**에이전트 위임 시 Haiku vs Sonnet 선택 휴리스틱**:
- 단순 조회 (파일 목록, 태그 통계, 링크 검사) → Haiku
- 내용 생성·판단 포함 작업 → Sonnet (필요시 advisor 추가)

## 도구 범위 규칙
- **읽기 전용 에이전트** (planner, architect, security-reviewer, data-quality-reviewer): 코드 수정 금지
- **수정 가능 에이전트** (tdd-guide, build-error-resolver, refactor-cleaner 등): Write/Edit 허용
- **실행 가능 에이전트** (e2e-runner, build-error-resolver, model-evaluator): Bash 허용

## 병렬 실행
- 독립적인 에이전트 작업은 병렬 실행
- 의존관계가 있는 작업은 순차 실행
- 예: `security-reviewer` + `doc-updater` → 병렬 가능
- 예: `planner` → `architect` → `tdd-guide` → 순차 필수

## 스킬 complexity 필드 해석 규칙

스킬 `SKILL.md` frontmatter의 `complexity` 필드는 Advisor 패턴 활성화 여부를 결정한다.

| complexity | 전략 | 비고 |
|-----------|------|------|
| `high` | Sonnet executor + Opus advisor (advisor_max_uses 준수) | 판단 품질 중요 |
| `medium` | Sonnet 단독 | 필요 시 수동으로 advisor 추가 |
| `low` | Haiku 에이전트 우선 | 결정론적 작업 |

**high complexity 스킬 목록** (자동 advisor 활성화):
`academic-research-writer`, `scientific-critical-thinking`, `review-pr`, `plan-drafter`, `code-reviewer`, `reference-knowledge-sync`

**적용 방법**: `complexity: high` 스킬 호출 시 → 에이전트 프롬프트에 명시
```
"판단이 필요한 지점에서 Opus advisor를 max {advisor_max_uses}회 활용하라.
advisor는 도구 호출 없이 계획/수정안만 전달한다."
```

## 반복 예산 (Iteration Budget)

각 에이전트(부에이전트 포함)는 독립적인 반복 예산을 가지며, 무한 루프를 방지한다.

| 에이전트 유형 | 최대 반복 | 이유 |
|-------------|---------|------|
| 복잡한 구현 (tdd-guide, build-error-resolver) | 90회 | 기본값 |
| 탐색/조회 (Explore, doc-updater) | 20-30회 | 경량 작업 |
| 병렬 실행 에이전트 | 개별 독립 예산 | 한 에이전트 실패가 전체 차단 방지 |

- 30회 내 진전 없으면 → 분해 방식 변경 또는 수동 개입 (30분 룰과 동일)
- 에이전트 프롬프트에 명시: "N회 이내에 완료되지 않으면 현재까지의 진행 상황을 보고하라"

## 서브에이전트 강제 호출 패턴

### "use subagents" 키워드
사용자가 "use subagents" 명시 시 작업을 하위 작업으로 분해하여 병렬 실행

### 강제 호출 조건
| 조건 | 호출 에이전트 | 이유 |
|------|--------------|------|
| 파일 10개+ 탐색 | `Explore` | 컨텍스트 절약 |
| 보안 민감 변경 | `security-reviewer` | 필수 검토 |
| 복잡한 리팩토링 | `planner` → `architect` | 설계 우선 |
| 멀티 디렉토리 분석 | 병렬 `Explore` | 속도 향상 |

### 병렬 탐색 패턴 예시
```
// 단일 메시지에서 여러 Task 동시 호출
Task(explore, "src/api/ 구조 분석")
Task(explore, "src/models/ 스키마 분석")
Task(explore, "tests/ 커버리지 분석")
```

### 에이전트 호출 금지 조건
다음 경우에는 에이전트 없이 직접 처리:
- 단순 파일 읽기/쓰기 (1-3개 파일)
- 1-5줄 버그 수정
- 타이포/오타 수정
- 단순 rename/move
- 명확한 단일 작업

## 에이전트 협력 원칙 (Agent Collaboration Principles)

### 결과물 직접 수정 금지
- 에이전트 결과가 불만족 → **에이전트/skill/프롬프트를 수정** 후 재실행
- 직접 수정 → 피드백 루프 단절, 같은 실수 반복
- 비판적 리뷰도 에이전트 스스로 하게 구성

### 에이전트 프레이밍
Claude 모델은 방어적으로 설계됨 — 프레이밍이 응답 품질을 좌우:

| 피해야 할 표현 | 권장 표현 |
|--------------|---------|
| "네가 잊어버릴 수 있으니까" | "다른 에이전트들에게 줄 데이터" |
| "너를 고치려는 것" | "같이 일할 다른 역할을 위한 것" |

### 단계적 컨텍스트 빌딩
한 번에 최종 목표를 지시하지 않고 단계적으로 접근:
1. **탐색** — "이 주제에 대해 조사하고 알려주세요"
2. **구조화** — "필요한 것들을 MD에 정리해 주세요"
3. **도구 설계** — "이걸 자동화할 도구를 제안해 주세요"
4. **구현** — "정확한 포맷으로 만들어 주세요"
5. **갈구기** — 비판적 자기 리뷰 반복

> "만들라고 시키지 않고, 아이디어를 먼저 달라고 한다"

### 파일 기반 메모리 패턴
- 서브에이전트는 **파일시스템에 직접 출력** → 리드 에이전트에 경량 참조만 전달
- "전화 게임(game of telephone)" 방지: 대규모 출력이 대화 기록 통해 복사되는 토큰 오버헤드 제거
- 구조화된 상태는 **JSON > Markdown** (모델이 임의 수정할 가능성 낮음)

### 스크립트 > 커스텀 도구 원칙
- 결정론적 작업(API 호출, 포맷 변환, 린트, 검증)은 bash 스크립트로 처리
- Vercel 사례: 도구 80% 제거 → Bash+SQL 2개만으로 성공률 80%→100%, 속도 3.5x, 토큰 37% 절감
- 핵심: "모델이 자체 처리 가능한 문제를 커스텀 도구로 해결하고 있었다" — 도구 추가보다 제거가 성능 개선

### 입력 최적화
- 한국어 입력: 품질 차이 미미, 타이핑 병목이면 한국어가 빠름
- Mac 음성 입력: 키보드보다 빠름
- skill/command는 영어: 토큰 절약
- Reference 캐싱: 웹 조사 결과를 `references/`에 저장 → 재조사 방지

## 에이전트 작업 위임 시 DoD (Definition of Done)

에이전트에게 작업 위임 시 프롬프트에 DoD 섹션을 포함하여 "완료" 기준을 명시한다.

### DoD 템플릿
```
## DoD (완료 기준)
- [ ] 기존 테스트 전체 통과 (수정 금지)
- [ ] 새 기능에 대한 테스트 추가
- [ ] `return nil`, `// TODO`, 스텁 코드 없음
- [ ] 변경 파일 목록 + 변경 사유 리포트 제출
- [ ] 3-5개 파일 이내 변경 (초과 시 분할)
```

### 사용 시점
| 상황 | DoD 필수 여부 |
|------|-------------|
| 단순 버그 수정 (1-3줄) | 불필요 |
| 기능 추가/변경 | 필수 |
| 리팩토링 | 필수 |
| 병렬 에이전트 실행 | 필수 (충돌 방지) |

### 스텁 방지 가드레일
- `return nil`, `pass`, `// stub`, `TODO` 금지 명시
- 30분 체크포인트: 중간 진행 보고 요구
- 기존 테스트 수정/삭제 금지 명시

## 예광탄 전략 (Tracer Bullet)

대규모 변경 전 단일 파일/화면에서 먼저 검증 후 확대한다.

### 프로세스
1. **단일 대상 선정**: 가장 대표적인 파일/화면 1개 선택
2. **예광탄 실행**: 해당 대상에만 변경 적용 + 테스트
3. **블루프린트 확보**: 성공 패턴을 문서화
4. **확대 적용**: 나머지 대상에 동일 패턴 적용

### 적용 기준
- 5개+ 파일에 동일 패턴 변경 시
- 새로운 라이브러리/프레임워크 도입 시
- UI 전체 스타일 변경 시

## 에이전트 실패 복구 힌트

에이전트가 실패하거나 진전이 없을 때, 아래 4가지 힌트로 복구 전략을 결정한다.

| 힌트 | 조건 | 액션 |
|------|------|------|
| `retryable` | 일시적 오류 (타임아웃, 네트워크) | 동일 프롬프트로 재시도 |
| `should_compress` | 컨텍스트 오버플로우, 느린 응답 | `/compact` 후 재시도 |
| `should_fallback` | 에이전트 역량 초과, 반복 실패 | 더 강력한 모델(Opus)로 전환 또는 수동 처리 |
| `decompose` | 30분 이상 진전 없음 | 작업을 더 작은 단위로 분해 후 재위임 |

> KNOWN_ISSUES.md와 연계: 동일 에이전트에서 동일 힌트가 3회 반복되면 프롬프트/가드레일 수정 필요

## 세션 간 상태 관리

### 보조 상태 파일 (프로젝트별)
| 파일 | 역할 | 갱신 시점 |
|------|------|----------|
| `PROGRESS.md` | 어디까지 진행됐는지 | 세션 종료 시 |
| `PLAN.md` | 무슨 일을 해야 하는지 | 세션 시작/변경 시 |

새 세션 시작 시 두 파일을 읽어 컨텍스트를 복원한다.
