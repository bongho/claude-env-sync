# Git 워크플로우 규칙 (Git Workflow Rules)

## Conventional Commits
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Type 목록
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `refactor`: 기능 변경 없는 코드 개선
- `test`: 테스트 추가/수정
- `docs`: 문서 변경
- `chore`: 빌드, CI, 패키지 관리 등
- `perf`: 성능 개선
- `style`: 코드 포맷팅 (로직 변경 없음)
- `experiment`: ML 실험 관련 변경

### 커밋 메시지 규칙
- Subject: 50자 이내, 영문 소문자 시작, 마침표 없음
- Body: Why 중심 설명, 72자 줄바꿈
- Breaking change: footer에 `BREAKING CHANGE:` 명시

## 브랜치 전략

### 브랜치 네이밍
- `feature/<ticket-id>-<description>`: 기능 개발
- `fix/<ticket-id>-<description>`: 버그 수정
- `experiment/<experiment-name>`: ML 실험
- `refactor/<description>`: 리팩토링
- `docs/<description>`: 문서 작업

### ML 실험 브랜치
- `experiment/*` 브랜치는 자유로운 실험 허용
- 실험 결과는 `experiments/` 디렉토리에 기록
- 성공한 실험만 `feature/` 브랜치로 전환 후 PR

## PR 프로세스

### PR 작성
- 제목: Conventional Commit 형식
- 본문: Summary (1-3줄), Changes, Test Plan
- 관련 이슈 링크 포함
- 스크린샷/로그 첨부 (UI/성능 변경 시)

### 리뷰 기준
- 최소 1명 승인 필수 (핵심 모듈은 2명)
- CI 통과 필수
- 리뷰어: 도메인 전문가 + 코드 오너
- 리뷰 코멘트 분류: `must`, `should`, `nit`

### 머지 전략
- `squash merge` 기본 (깔끔한 히스토리)
- 대규모 feature는 `merge commit` 허용
- `rebase merge`는 선형 히스토리 필요 시

## 커밋 위생
- 작업 단위별 커밋 (atomic commits)
- WIP 커밋 금지 (squash 후 push)
- 바이너리 파일 커밋 금지 (LFS 또는 외부 저장소)
- `.gitignore` 최신 유지: IDE 설정, 빌드 아티팩트, 데이터 파일 제외
