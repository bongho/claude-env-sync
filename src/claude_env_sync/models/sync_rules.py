"""동기화 규칙 및 Tier 정의 모듈."""

from __future__ import annotations

from enum import IntEnum

from pydantic import BaseModel


class SyncTier(IntEnum):
    """동기화 우선순위 Tier.

    TIER1: 필수 동기화 (CLAUDE.md, settings.json, agents/, plugins)
    TIER2: 선택적 동기화 (skills/, history.jsonl)
    TIER3: 확장 동기화 (projects/, todos/) — Phase 3
    """

    TIER1 = 1
    TIER2 = 2
    TIER3 = 3


class SyncRule(BaseModel):
    """개별 동기화 규칙 정의."""

    pattern: str
    tier: SyncTier
    is_directory: bool
    description: str


def get_default_rules() -> list[SyncRule]:
    """기본 동기화 규칙 목록을 반환한다."""
    return [
        SyncRule(
            pattern="CLAUDE.md",
            tier=SyncTier.TIER1,
            is_directory=False,
            description="메인 Claude 설정 파일",
        ),
        SyncRule(
            pattern="settings.json",
            tier=SyncTier.TIER1,
            is_directory=False,
            description="Claude Code 설정",
        ),
        SyncRule(
            pattern="agents/",
            tier=SyncTier.TIER1,
            is_directory=True,
            description="사용자 에이전트 정의",
        ),
        SyncRule(
            pattern="plugins/installed_plugins.json",
            tier=SyncTier.TIER1,
            is_directory=False,
            description="설치된 플러그인 목록",
        ),
        SyncRule(
            pattern="skills/",
            tier=SyncTier.TIER2,
            is_directory=True,
            description="사용자 스킬 정의",
        ),
        SyncRule(
            pattern="history.jsonl",
            tier=SyncTier.TIER2,
            is_directory=False,
            description="명령 히스토리",
        ),
        SyncRule(
            pattern="projects/",
            tier=SyncTier.TIER3,
            is_directory=True,
            description="프로젝트별 세션 히스토리",
        ),
        SyncRule(
            pattern="todos/",
            tier=SyncTier.TIER3,
            is_directory=True,
            description="할일 목록",
        ),
    ]


def get_rules_by_tier(max_tier: SyncTier = SyncTier.TIER2) -> list[SyncRule]:
    """지정된 Tier 이하의 동기화 규칙만 반환한다."""
    return [r for r in get_default_rules() if r.tier.value <= max_tier.value]


def get_excluded_patterns() -> list[str]:
    """동기화에서 제외할 패턴 목록을 반환한다."""
    return [
        "debug/",
        "cache/",
        "paste-cache/",
        "session-env/",
        "statusline.log",
        "stats-cache.json",
        "statsig/",
        "settings.local.json",
    ]
