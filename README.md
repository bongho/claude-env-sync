# claude-env-sync

> Sync your Claude Code settings across machines — like chezmoi, but for AI tools.

Claude Code의 설정(CLAUDE.md, settings.json, agents, skills 등)을 Git으로 동기화하는 CLI 도구입니다. 여러 기기에서 동일한 Claude 환경을 유지하세요.

## 주요 기능

- **Git 기반 동기화** — 설정 파일을 Git 저장소로 관리
- **시크릿 보호** — API 키, 토큰 등을 자동으로 감지하여 push 차단
- **Time-Travel** — 이전 설정 상태로 복원 가능 (`history`, `restore`)
- **Tier 기반 동기화** — 필수/선택 파일을 구분하여 관리
- **자동 Hook** — Shell 시작 시 자동 동기화

## 동기화 대상

| Tier | 파일 | 설명 |
|------|------|------|
| Tier 1 | `CLAUDE.md` | 메인 설정 |
| Tier 1 | `settings.json` | Claude Code 설정 |
| Tier 1 | `agents/` | 에이전트 정의 |
| Tier 1 | `plugins/installed_plugins.json` | 플러그인 목록 |
| Tier 2 | `skills/` | 스킬 정의 |
| Tier 2 | `history.jsonl` | 명령 히스토리 |

자동 제외: `debug/`, `cache/`, `session-env/`, API 키 등

## 설치

```bash
# pipx 사용 (권장)
pipx install claude-env-sync

# 또는 pip
pip install claude-env-sync

# 또는 원커맨드 설치
curl -sSL https://raw.githubusercontent.com/bono/claude-env-sync/main/scripts/install.sh | bash
```

## 사용법

### 초기 설정

```bash
# 동기화 저장소 초기화 (원격 Git 저장소 연결)
claude-sync init --remote git@github.com:username/claude-config.git
```

### 기본 워크플로우

```bash
# 현재 Claude 설정을 동기화 저장소로 push
claude-sync push

# 다른 기기에서 설정 가져오기
claude-sync pull

# 동기화 상태 확인
claude-sync status
```

### Time-Travel (킬러 피처)

```bash
# 변경 이력 조회
claude-sync history

# 특정 시점으로 복원
claude-sync restore <commit-sha>
```

### 자동 동기화 Hook

```bash
# Shell 시작 시 자동 pull hook 설치
claude-sync hook install

# Hook 제거
claude-sync hook uninstall
```

## 개발

```bash
# 저장소 클론
git clone https://github.com/bono/claude-env-sync.git
cd claude-env-sync

# 가상환경 생성 및 의존성 설치
python -m venv .venv
source .venv/bin/activate
pip install -e "."
pip install pytest pytest-cov ruff

# 테스트 실행
pytest tests/ -v --cov=claude_env_sync --cov-report=term-missing

# 린트
ruff check src/ tests/
```

## 프로젝트 구조

```
src/claude_env_sync/
├── cli.py                    # Click CLI (init, push, pull, status, history, restore, hook)
├── core/
│   ├── sync_engine.py        # 핵심 동기화 로직
│   ├── git_ops.py            # Git 연산 래퍼
│   └── path_resolver.py      # Claude 설정 경로 탐지
├── models/
│   └── sync_rules.py         # Tier 정의 및 동기화 규칙
├── hooks/
│   └── install.py            # Shell RC hook 설치/제거
└── utils/
    └── security.py           # .gitignore 생성, 시크릿 탐지
```

## 라이선스

MIT
