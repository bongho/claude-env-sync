"""보안 유틸리티: .gitignore 생성 및 시크릿 탐지."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SECRET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"sk-ant-api\w{2}-[\w-]{20,}"),       # Anthropic API key
    re.compile(r"sk-proj-[\w-]{20,}"),                # OpenAI project key
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),               # Generic sk- key
    re.compile(r"ghp_[a-zA-Z0-9]{36,}"),              # GitHub personal token
    re.compile(r"gho_[a-zA-Z0-9]{36,}"),              # GitHub OAuth token
    re.compile(r"github_pat_[a-zA-Z0-9_]{20,}"),      # GitHub fine-grained PAT
    re.compile(r"xoxb-[\w-]{20,}"),                    # Slack bot token
    re.compile(r"xoxp-[\w-]{20,}"),                    # Slack user token
    re.compile(r"AIza[a-zA-Z0-9_-]{35}"),             # Google API key
]

_GITIGNORE_CONTENT = """\
# Secrets — 절대 동기화하면 안 되는 파일
**/api_key*
**/*token*
**/*secret*
**/credentials*
**/.env
**/.env.*

# Claude Code 비동기화 대상
debug/
cache/
paste-cache/
session-env/
statusline.log
stats-cache.json
statsig/
settings.local.json

# OS
.DS_Store
Thumbs.db
"""


@dataclass
class SecretFinding:
    """시크릿 탐지 결과."""

    file_path: Path
    line_number: int
    matched_text: str
    pattern_name: str


def generate_gitignore() -> str:
    """동기화 저장소용 .gitignore 콘텐츠를 생성한다."""
    return _GITIGNORE_CONTENT


def scan_for_secrets(directory: Path) -> list[SecretFinding]:
    """디렉토리 내 파일들에서 시크릿 패턴을 탐지한다.

    Args:
        directory: 스캔할 디렉토리 경로.

    Returns:
        탐지된 시크릿 목록.
    """
    findings: list[SecretFinding] = []

    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            for pattern in SECRET_PATTERNS:
                match = pattern.search(line)
                if match:
                    findings.append(
                        SecretFinding(
                            file_path=file_path,
                            line_number=line_number,
                            matched_text=match.group(),
                            pattern_name=pattern.pattern,
                        )
                    )

    return findings
