# 하네스 레이어별 용도 구분 가이드

> Skill vs Command vs Hook vs Plugin — 언제 무엇을 쓰는가

---

## 0. 핵심 4가지 빠른 비교

| | **Command** | **Skill** | **Hook** | **Plugin** |
|---|---|---|---|---|
| **트리거** | `/name` 호출 | `/name` 호출 | 도구 이벤트 자동 | 설치 후 상시 |
| **작성자** | 나 (로컬) | 나 또는 플러그인 | 나 (settings.json) | 외부 팀 |
| **복잡도** | 단순 (단일 목적) | 복잡 (다단계 워크플로우) | 스크립트 (bash) | 패키지 (Skill+도구 묶음) |
| **인간 개입** | 매번 직접 호출 | 매번 직접 호출 | 없음 (완전 자동) | 설치/삭제만 |
| **저장 위치** | `~/.claude/commands/` | `~/.claude/skills/` | `settings.json` | `~/.claude/plugins/` |
| **주요 용도** | 단순 반복 지시 | 도메인 워크플로우 | 품질 강제·가드레일 | Claude 기능 확장 |

### 한 줄 정의

- **Command**: "이것 해줘" — 단순하고 자주 쓰는 지시를 `/name`으로 단축
- **Skill**: "이 복잡한 워크플로우 실행해줘" — 전문 도메인 지식 + 다단계 절차 캡슐화
- **Hook**: "도구 쓸 때마다 자동으로 이것도 해줘" — 사람 없이 항상 실행되는 가드레일
- **Plugin**: "이 기능 세트를 Claude에 추가해줘" — Command/Skill을 패키지로 배포

### Command vs Skill 선택 기준

```
단순한 프롬프트 지시 하나? → Command
  예) /fix-types: "타입 에러 수정해줘"
  예) /korean: "한국어로 번역해줘"

다단계 절차 + 도메인 전문성? → Skill
  예) /bq: 쿼리 작성→비용 추정→실행→결과 포맷팅
  예) /ghost-blog: 노트 변환→미리보기→발행→태그 설정
```

---

## 1. 레이어 한눈에 보기

| 레이어 | 트리거 | 지속성 | 인간 개입 | 주요 목적 |
|--------|--------|--------|-----------|-----------|
| **CLAUDE.md** | 항상 로드 | 영구 | 직접 편집 | 역할·원칙·맥락 정의 |
| **Context** | 수동 (`--system-prompt`) | 세션 단위 | 모드 선택 | 작업 유형별 프레임 전환 |
| **Agent** | 자동/수동 위임 | 태스크 단위 | 위임 승인 | 전문 영역 독립 처리 |
| **Skill** | `/command` 호출 | 요청 단위 | 직접 호출 | 복잡한 워크플로우 캡슐화 |
| **Hook** | 도구 이벤트 자동 | 이벤트 단위 | 없음 | 품질 강제·가드레일 |
| **MCP** | 도구 호출 시 | 연결 유지 | 없음 | 외부 시스템 실시간 접근 |
| **Plugin** | 설치 후 상시 | 영구 | 설치/삭제 | Claude 기능 자체 확장 |
| **Rule** | CLAUDE.md 참조 | 영구 | 직접 편집 | 코딩 스타일·보안 강제 |
| **Permission** | 도구 실행 시 | 영구 | 설정 편집 | 실행 안전 경계 |

---

## 2. 결정 트리 — 무엇을 새로 추가할 때

```
새 자동화/기능을 추가하고 싶다
│
├─ 도구 실행 전후에 자동으로 실행되어야 하는가?
│   └─ YES → Hook (PreToolUse / PostToolUse / Stop / SessionStart)
│
├─ 외부 시스템 (DB, Slack, Calendar)에 Claude가 직접 접근해야 하는가?
│   └─ YES → MCP Server
│
├─ 유저가 명령어로 직접 호출하는 복잡한 워크플로우인가?
│   └─ YES → Skill (/command)
│              │
│              └─ 특정 도메인 전문 지식이 핵심인가?
│                  ├─ YES → 전문 Agent 정의 + Skill에서 위임
│                  └─ NO  → Skill 단독
│
├─ 독립적으로 실행되는 전문 역할인가? (보안 검토, ML 평가 등)
│   └─ YES → Agent
│
├─ 특정 작업 유형(코드/연구/데이터)에서만 다른 행동이 필요한가?
│   └─ YES → Context 모드
│
├─ Claude 자체 기능을 확장하는가? (새 도구, 새 명령 체계)
│   └─ YES → Plugin
│
└─ 역할·원칙·맥락을 영구적으로 정의하는가?
    └─ YES → CLAUDE.md
```

---

## 3. 레이어별 상세

### 3.1 CLAUDE.md

**역할**: Claude가 모든 세션에서 항상 읽는 "역할 헌법"

**담아야 하는 것:**
- 나는 누구인가 (DS 리더 / AI PM)
- Claude는 어떤 파트너인가 (증강 코딩, H 커플링)
- 핵심 원칙 (Think First, 최소 변경, 푸시백)
- 에이전트·스킬·컨텍스트 인덱스 (포인터만)

**담지 말아야 하는 것:**
- 도메인별 상세 구현 지식 (→ references/)
- 특정 기술 스택 상세 (→ rules/)
- 워크플로우 절차 (→ Skill)

**수정 빈도**: 드물게 (원칙 변경 시)

---

### 3.2 Context (작업 모드)

**역할**: 세션 시작 시 작업 유형에 맞게 Claude 행동을 조정

**현재 7개 모드:**
```
dev          코드 우선 (작동→올바름→깨끗)
research     탐색·가설 검증, 출처 명시
data-analysis  프로파일링→EDA→인사이트 순서 강제
experiment   ML 실험 (Baseline→단일변수→기록)
review       읽기 전용, 심각도 분류 (MUST/SHOULD/NIT)
deploy       안전성·비용·모니터링·롤백 필수 점검
learning     개념 이해, 시각적 설명, 간격 반복
```

**사용법**: `claude --system-prompt "$(cat ~/.claude/contexts/dev.md)"`

**Tip**: Hook의 `SessionStart`로 프로젝트 디렉토리 기반 자동 감지 구현 가능

---

### 3.3 Agent (서브에이전트)

**역할**: 독립적으로 실행 가능한 전문 역할을 분리·위임

**언제 Agent를 만드는가:**
- 특정 도메인 전문 지식이 핵심인 반복 작업 (보안 분석, BQ 최적화)
- 메인 컨텍스트를 오염시키지 않고 싶은 대규모 탐색
- 병렬 실행이 필요한 독립 작업

**언제 Agent가 아닌가:**
- 1회성 작업 → 직접 처리
- CLAUDE.md 지침으로 충분한 것 → Agent 오버킬
- 유저 인터랙션이 필요한 것 → Skill

**모델 배정 전략:**
| 모델 | 에이전트 유형 |
|------|---------------|
| Opus | 아키텍처 설계, 보안 분석, 전략 수립 (판단 중심) |
| Sonnet | 코드 구현, 데이터 분석, 테스트 (실행 중심) |
| Haiku | 문서 포맷팅, 단순 조회, 링크 검증 (속도 중심) |

---

### 3.4 Command

**역할**: 단순하고 자주 쓰는 지시를 `/name` 단축키로 저장

**저장 위치**: `~/.claude/commands/<name>.md`

**언제 Command를 만드는가:**
- 프롬프트 한 문장으로 표현 가능한 반복 작업
- 특정 파일/프로젝트 없이 즉시 실행 가능한 것
- 매개변수 없이 고정된 지시

**예시:**
```markdown
# fix-types.md
현재 파일의 TypeScript 타입 에러를 모두 수정해줘.
strict 모드 기준으로, any 사용 금지.
```
→ `/fix-types`로 호출

**Command vs Skill:**
| 항목 | Command | Skill |
|------|---------|-------|
| 절차 수 | 1단계 | 3단계 이상 |
| 외부 도구 | 없음 | 있음 (API, MCP 등) |
| 도메인 지식 | 최소 | 핵심 |
| 파일 길이 | 10~30줄 | 100~500줄 |

---

### 3.6 Skill (/command)

**역할**: 유저가 명시적으로 호출하는 복잡한 워크플로우 캡슐화

**언제 Skill을 만드는가:**
- 3단계 이상의 절차가 반복되는 작업
- 특정 형식·포맷의 출력이 필요한 작업
- 외부 도구(Ghost, Zotero, Akiflow) 연동이 핵심인 작업

**Skill vs Agent 선택 기준:**

| 기준 | Skill 선택 | Agent 선택 |
|------|-----------|-----------|
| 트리거 | 유저 명시 호출 | 자동 위임 / 필요시 호출 |
| 컨텍스트 | 메인 대화 내에서 실행 | 독립 컨텍스트로 분리 |
| 병렬 실행 | 불가 (순차) | 가능 (동시 실행) |
| 인터랙션 | 유저와 직접 대화 가능 | 독립 실행 후 결과 반환 |
| 전문성 | 워크플로우 절차 중심 | 도메인 지식 중심 |

**현재 운영 중인 Skill 범주:**
- 코드/분석: `bq`, `code-reviewer`, `techdebt`, `test-generator`
- 문서/콘텐츠: `academic-research-writer`, `ghost-blog`, `humanizer`, `gmail`
- 인프라/연동: `atlassian-skills`, `gworkspace`, `devonthink`
- 시스템: `session-wrap`, `context_management`, `km-audit`

---

### 3.7 Hook

**역할**: 도구 이벤트에 자동으로 반응하는 가드레일·자동화

**6가지 Hook 이벤트:**
```
PreToolUse    도구 실행 전 (차단 가능, 위험 작업 확인)
PostToolUse   도구 실행 후 (포맷팅, 타입 체크, 감사)
SessionStart  세션 시작 (환경 초기화, 상태 로드)
Stop          세션 종료 (상태 저장, 요약 출력)
PreCompact    /compact 전 (핵심 컨텍스트 보존)
Notification  알림 이벤트 처리
```

**현재 활성 Hook:**
```bash
# PostToolUse (파일 편집 후)
python → black --check, mypy --strict
typescript → prettier --check, tsc --noEmit
go → gofmt -l

# PreToolUse (Bash 실행 전)
git push → "변경사항 검토했나요?" 알림

# Stop (세션 종료)
git status → staged/modified/new 파일 요약
```

**추천 미구현 Hook:**
```bash
# PostToolUse — 의존성 감사
pip-audit / npm audit --audit-level=high

# PostToolUse — 시크릿 스캔
grep -rE "(api_key|secret|password|token)\s*=" --include="*.py"

# PostToolUse — 파일 크기 경고
wc -l "$file" | awk '{if($1>800) print "경고: 800줄 초과 → 모듈 분리 고려"}'

# PostToolUse — BQ 비용 경고
# BigQuery DML 실행 후 예상 비용 1TB 초과 시 경고
```

**Hook vs CLAUDE.md 지시 차이:**
| 항목 | Hook | CLAUDE.md 지시 |
|------|------|---------------|
| 실행 주체 | 시스템 (자동) | Claude (LLM 판단) |
| 실행 보장 | 100% (무조건) | Claude가 무시할 수 있음 |
| 적합한 용도 | 포맷팅·보안·감사 | 원칙·스타일·우선순위 |

---

### 3.8 MCP (Model Context Protocol)

**역할**: Claude가 외부 시스템에 도구로 직접 접근

**현재 운영 중 (6개):**
```
bigquery    로컬 toolbox → ax-data-service 프로젝트
atlassian   claude.ai OAuth → Jira, Confluence
google-drive  claude.ai OAuth → Drive 파일
google-cal    claude.ai OAuth → 일정
slack       claude.ai OAuth → 메시지
datadog     claude.ai OAuth → 메트릭, 로그
```

**MCP vs Bash 도구 선택 기준:**
| 기준 | MCP 선택 | Bash 선택 |
|------|----------|-----------|
| 인증 방식 | OAuth, API 키 관리 필요 | 로컬 CLI로 충분 |
| 응답 구조 | 구조화된 데이터 (JSON) | 텍스트 출력 |
| 외부 서비스 | SaaS API (Jira, Slack) | 로컬 또는 CLI 툴 |
| 실시간성 | 필요 | 배치 처리 가능 |

**주의:**
- 활성 MCP는 10개 이내 유지 (컨텍스트 오염 방지)
- claude.ai MCP는 OAuth 만료 시 재인증 필요
- 로컬 MCP는 `.mcp.json` 또는 `settings.json` 에 등록

---

### 3.9 Plugin

**역할**: Claude Code 자체의 기능을 확장 (새 도구 타입, 새 Skill 체계 등)

**현재 설치 (8개):**
| 플러그인 | 제공하는 것 |
|---------|-------------|
| `beads` | Markdown 기반 이슈 트래킹 + 관련 Skill 세트 |
| `session-wrap` | 세션 마무리 자동화 Skill 세트 |
| `youtube-digest` | YouTube 분석 Skill |
| `playwright-skill` | 브라우저 자동화 Skill |
| `claude-hud` | 상태 표시줄 (토큰, 모델, 컨텍스트) |
| `telegram` | Telegram 연동 |
| `skills-cleaner` | 중복 Skill 탐지·정리 |
| `vercel-plugin` | Vercel 배포 연동 |

**Plugin vs Skill vs MCP:**
- Plugin = Skill + 고유 도구 타입을 패키지로 묶어 배포
- Skill = 단일 워크플로우 마크다운 파일
- MCP = 외부 API 접근 프로토콜

---

### 3.10 Rules

**역할**: 코드 품질·보안 기준을 문서화해 CLAUDE.md에서 on-demand 로드

**3개 파일:**
- `coding-style.md`: 언어별 스타일, 파일/함수 크기 제한
- `git-workflow.md`: Conventional Commits, PR 프로세스
- `security.md`: OWASP Top 10, PII, 시크릿 관리

**Rule vs Hook:**
- Rule = "해야 한다"는 지침 (Claude가 참고)
- Hook = "반드시 실행된다"는 강제 (시스템이 실행)
→ 중요한 품질 기준은 Rule + Hook 모두 적용

---

### 3.11 Permission

**역할**: 특정 도구 실행을 사전에 허용하여 반복 승인 프롬프트 제거

**설정 위치:** `settings.local.json` → `allowedTools`

**현재 허용 항목 (~50개):**
- Bash: `rm -rf ./`, `python3 *`, `pip *`, `brew *`, `curl *`, `find *` 등
- WebFetch: `arxiv.org`, `github.com`, `sciencedirect.com` 등 학술·개발 도메인
- MCP 스킬: Confluence, Obsidian 접근

**Permission 설계 원칙:**
- 반복적으로 차단되는 안전한 명령 → `settings.local.json`에 추가
- 파괴적 작업 (`git push`, `rm` without scope) → 명시적 허용 않고 매번 확인
- 공유 프로젝트 권한 → `settings.json` (팀 공유), 개인 확장 → `settings.local.json`

---

## 4. 중복·혼동 케이스 정리

### "자동으로 코드 포맷하고 싶다"
- → **Hook** (PostToolUse, 파일 편집 후 자동 실행)
- ~~Skill (유저가 매번 호출해야 함)~~
- ~~CLAUDE.md 지시 (Claude가 무시할 수 있음)~~

### "BQ 쿼리를 최적화해주는 기능을 만들고 싶다"
- → **Skill** (`/bq` 호출) + **Agent** (`bq-specialist`) 조합
- Skill이 사용자 인터페이스, Agent가 실제 전문 처리
- MCP는 실제 쿼리 실행에만 사용

### "Jira 티켓 생성을 자동화하고 싶다"
- → **MCP** (Atlassian) + **Skill** (`/atlassian-skills`)
- MCP가 API 접근, Skill이 워크플로우 절차 정의

### "보안 취약점 검토를 받고 싶다"
- → **Agent** (`security-reviewer`, opus 모델)
- Hook이 아닌 이유: 판단·분석이 필요한 작업 → LLM 필요
- Skill이 아닌 이유: 독립 컨텍스트에서 코드베이스 전체 탐색 필요

### "매 세션 시작마다 현재 작업 상태를 로드하고 싶다"
- → **Hook** (SessionStart) + 상태 파일 읽기
- Context는 작업 유형 프레임이지 상태 로드가 아님

---

## 5. 현재 환경 gap (개선 권장)

| 항목 | 현황 | 권장 조치 |
|------|------|-----------|
| 의존성 감사 | 미구현 | PostToolUse Hook으로 `pip-audit` 추가 |
| 시크릿 스캔 | 미구현 | PostToolUse Hook으로 regex 검사 추가 |
| Context 자동 전환 | 수동 | SessionStart Hook에 디렉토리 기반 자동 감지 |
| Datadog API 키 | settings.json 평문 | 환경변수 파일 분리 또는 macOS Keychain 참조 |
| MCP 인증 상태 | 주기적 만료 | 만료 감지 Hook 또는 정기 재인증 리마인더 |

---

## 6. Thin Harness Fat Skills 원칙

```
Harness (CLAUDE.md + Hooks + Settings)
  → 최소화: 역할 정의, 안전 경계, 이벤트 트리거만

Skills (Skill + Agent + Context)
  → 두텁게: 도메인 지식, 워크플로우, 전문 판단

MCP / Plugin
  → 필요할 때만: 외부 연결, 기능 확장
```

레이어 간 책임이 명확히 분리될수록:
- 개별 레이어를 독립적으로 업그레이드 가능
- 하네스 변경 없이 Skill·Agent 추가 가능
- 디버깅 시 어느 레이어 문제인지 즉시 식별 가능

---

*관련: `hooks-guide.md` | `agents.md` | `performance.md`*  
*Obsidian 노트: [[20260424 - 나의 Claude Code 환경 분석]]*
