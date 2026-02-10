"""SyncEngine/GitOps를 MCP 도구로 래핑하는 함수들."""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from pathlib import Path
from typing import Any

from claude_env_sync.core.git_ops import GitOps, GitOpsError
from claude_env_sync.core.sync_engine import SyncEngine
from claude_env_sync.hooks.install import (
    install_shell_hook,
    is_hook_installed,
    uninstall_shell_hook,
)


def _default_dirs() -> tuple[Path, Path, Path]:
    claude_dir = Path.home() / ".claude"
    sync_repo_dir = Path.home() / ".claude-sync-repo"
    backup_dir = Path.home() / ".claude-sync-backup"
    return claude_dir, sync_repo_dir, backup_dir


def _make_engine(
    claude_dir: str | None = None,
    sync_repo: str | None = None,
    backup_dir: str | None = None,
    auto_init: bool = True,
) -> SyncEngine:
    defaults = _default_dirs()
    repo_path = Path(sync_repo) if sync_repo else defaults[1]
    engine = SyncEngine(
        claude_dir=Path(claude_dir) if claude_dir else defaults[0],
        sync_repo_dir=repo_path,
        backup_dir=Path(backup_dir) if backup_dir else defaults[2],
    )
    if auto_init and engine.git_ops.is_initialized():
        engine.git_ops.init_repo()
    return engine


async def sync_init(
    remote_url: str | None = None,
    claude_dir: str | None = None,
    sync_repo: str | None = None,
    backup_dir: str | None = None,
) -> dict[str, Any]:
    """동기화 환경을 초기화한다."""
    engine = _make_engine(claude_dir, sync_repo, backup_dir, auto_init=False)

    def _run() -> dict[str, Any]:
        engine.initialize(remote_url=remote_url)
        return {
            "success": True,
            "message": "동기화 환경 초기화 완료.",
            "sync_repo": str(engine._sync_repo_dir),
            "remote": remote_url,
        }

    return await asyncio.to_thread(_run)


async def sync_push(
    message: str | None = None,
    claude_dir: str | None = None,
    sync_repo: str | None = None,
    backup_dir: str | None = None,
) -> dict[str, Any]:
    """Claude 설정을 동기화 저장소로 push한다."""
    engine = _make_engine(claude_dir, sync_repo, backup_dir)

    def _run() -> dict[str, Any]:
        result = engine.push(message=message)
        return asdict(result)

    return await asyncio.to_thread(_run)


async def sync_pull(
    claude_dir: str | None = None,
    sync_repo: str | None = None,
    backup_dir: str | None = None,
) -> dict[str, Any]:
    """동기화 저장소의 설정을 Claude 디렉토리로 복원한다."""
    engine = _make_engine(claude_dir, sync_repo, backup_dir)

    def _run() -> dict[str, Any]:
        result = engine.pull()
        return asdict(result)

    return await asyncio.to_thread(_run)


async def sync_status(
    claude_dir: str | None = None,
    sync_repo: str | None = None,
    backup_dir: str | None = None,
) -> dict[str, Any]:
    """현재 동기화 상태를 조회한다."""
    engine = _make_engine(claude_dir, sync_repo, backup_dir)

    def _run() -> dict[str, Any]:
        status = engine.status()
        return asdict(status)

    return await asyncio.to_thread(_run)


async def sync_history(
    limit: int = 20,
    claude_dir: str | None = None,
    sync_repo: str | None = None,
    backup_dir: str | None = None,
) -> dict[str, Any]:
    """동기화 이력을 조회한다."""
    engine = _make_engine(claude_dir, sync_repo, backup_dir)

    def _run() -> dict[str, Any]:
        entries = engine.git_ops.get_log(limit=limit)
        return {
            "entries": [
                {
                    "sha": e.sha[:8],
                    "message": e.message,
                    "date": e.date.isoformat(),
                    "files_changed": e.files_changed,
                }
                for e in entries
            ],
            "count": len(entries),
        }

    return await asyncio.to_thread(_run)


async def sync_restore(
    commit_sha: str,
    claude_dir: str | None = None,
    sync_repo: str | None = None,
    backup_dir: str | None = None,
) -> dict[str, Any]:
    """특정 커밋 시점으로 복원한다."""
    engine = _make_engine(claude_dir, sync_repo, backup_dir)

    def _run() -> dict[str, Any]:
        try:
            engine.git_ops.restore_to(commit_sha)
            return {
                "success": True,
                "message": f"커밋 {commit_sha[:8]}로 복원 완료.",
                "restored_sha": commit_sha,
            }
        except GitOpsError as e:
            return {"success": False, "error": str(e)}

    return await asyncio.to_thread(_run)


async def sync_hook_install(
    shell: str = "auto",
) -> dict[str, Any]:
    """Shell hook을 설치한다."""

    def _run() -> dict[str, Any]:
        rc_files = _resolve_rc_files(shell)
        installed: list[str] = []
        for rc in rc_files:
            if not is_hook_installed(rc):
                install_shell_hook(rc)
                installed.append(str(rc))
        if installed:
            return {
                "success": True,
                "message": f"Hook 설치 완료: {', '.join(installed)}",
                "files": installed,
            }
        return {"success": True, "message": "Hook이 이미 설치되어 있습니다."}

    return await asyncio.to_thread(_run)


async def sync_hook_uninstall(
    shell: str = "auto",
) -> dict[str, Any]:
    """Shell hook을 제거한다."""

    def _run() -> dict[str, Any]:
        rc_files = _resolve_rc_files(shell)
        removed: list[str] = []
        for rc in rc_files:
            if is_hook_installed(rc):
                uninstall_shell_hook(rc)
                removed.append(str(rc))
        if removed:
            return {
                "success": True,
                "message": f"Hook 제거 완료: {', '.join(removed)}",
                "files": removed,
            }
        return {"success": True, "message": "설치된 Hook이 없습니다."}

    return await asyncio.to_thread(_run)


def _resolve_rc_files(shell: str) -> list[Path]:
    home = Path.home()
    if shell == "bash":
        return [home / ".bashrc"]
    if shell == "zsh":
        return [home / ".zshrc"]
    # auto: detect available shells
    candidates = []
    for name in [".zshrc", ".bashrc"]:
        rc = home / name
        if rc.exists():
            candidates.append(rc)
    return candidates if candidates else [home / ".zshrc"]
