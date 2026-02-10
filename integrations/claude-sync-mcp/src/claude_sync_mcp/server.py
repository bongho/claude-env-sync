"""Claude Env Sync MCP Server."""

from __future__ import annotations

import logging
import sys
from typing import Any

from fastmcp import FastMCP

from claude_sync_mcp.tools import (
    sync_history,
    sync_hook_install,
    sync_hook_uninstall,
    sync_init,
    sync_pull,
    sync_push,
    sync_restore,
    sync_status,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

mcp = FastMCP(
    name="claude-env-sync",
    instructions=(
        "Claude Code 설정을 Git으로 동기화합니다.\n"
        "sync_status로 현재 상태를 확인하고, "
        "sync_push/sync_pull로 설정을 동기화하세요."
    ),
)


@mcp.tool(
    name="sync_init",
    description="동기화 환경을 초기화합니다. Git 저장소를 생성하고 선택적으로 원격 저장소를 설정합니다.",
)
async def tool_sync_init(
    remote_url: str | None = None,
    claude_dir: str | None = None,
    sync_repo: str | None = None,
    backup_dir: str | None = None,
) -> dict[str, Any]:
    return await sync_init(
        remote_url=remote_url,
        claude_dir=claude_dir,
        sync_repo=sync_repo,
        backup_dir=backup_dir,
    )


@mcp.tool(
    name="sync_push",
    description="Claude Code 설정 파일을 동기화 저장소로 push합니다. 시크릿이 감지되면 push를 중단합니다.",
)
async def tool_sync_push(
    message: str | None = None,
    claude_dir: str | None = None,
    sync_repo: str | None = None,
    backup_dir: str | None = None,
) -> dict[str, Any]:
    return await sync_push(
        message=message,
        claude_dir=claude_dir,
        sync_repo=sync_repo,
        backup_dir=backup_dir,
    )


@mcp.tool(
    name="sync_pull",
    description="동기화 저장소의 설정을 Claude 디렉토리로 복원합니다. 기존 설정은 자동 백업됩니다.",
)
async def tool_sync_pull(
    claude_dir: str | None = None,
    sync_repo: str | None = None,
    backup_dir: str | None = None,
) -> dict[str, Any]:
    return await sync_pull(
        claude_dir=claude_dir,
        sync_repo=sync_repo,
        backup_dir=backup_dir,
    )


@mcp.tool(
    name="sync_status",
    description="현재 동기화 상태를 조회합니다. 변경된 파일 목록과 마지막 동기화 시간을 반환합니다.",
)
async def tool_sync_status(
    claude_dir: str | None = None,
    sync_repo: str | None = None,
    backup_dir: str | None = None,
) -> dict[str, Any]:
    return await sync_status(
        claude_dir=claude_dir,
        sync_repo=sync_repo,
        backup_dir=backup_dir,
    )


@mcp.tool(
    name="sync_history",
    description="동기화 이력(커밋 로그)을 조회합니다.",
)
async def tool_sync_history(
    limit: int = 20,
    claude_dir: str | None = None,
    sync_repo: str | None = None,
    backup_dir: str | None = None,
) -> dict[str, Any]:
    return await sync_history(
        limit=limit,
        claude_dir=claude_dir,
        sync_repo=sync_repo,
        backup_dir=backup_dir,
    )


@mcp.tool(
    name="sync_restore",
    description="특정 커밋 시점으로 설정을 복원합니다. 복원 전 현재 상태가 자동 백업됩니다.",
)
async def tool_sync_restore(
    commit_sha: str,
    claude_dir: str | None = None,
    sync_repo: str | None = None,
    backup_dir: str | None = None,
) -> dict[str, Any]:
    return await sync_restore(
        commit_sha=commit_sha,
        claude_dir=claude_dir,
        sync_repo=sync_repo,
        backup_dir=backup_dir,
    )


@mcp.tool(
    name="sync_hook_install",
    description="Shell 시작 시 자동으로 claude-sync pull을 실행하는 hook을 설치합니다.",
)
async def tool_sync_hook_install(
    shell: str = "auto",
) -> dict[str, Any]:
    return await sync_hook_install(shell=shell)


@mcp.tool(
    name="sync_hook_uninstall",
    description="Shell hook을 제거합니다.",
)
async def tool_sync_hook_uninstall(
    shell: str = "auto",
) -> dict[str, Any]:
    return await sync_hook_uninstall(shell=shell)


def main() -> None:
    """MCP 서버를 실행한다."""
    logger.info("claude-sync-mcp v0.1.0 starting...")
    mcp.run()
