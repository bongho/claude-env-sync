"""MCP 서버 도구 테스트."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from claude_sync_mcp.tools import (
    sync_history,
    sync_init,
    sync_pull,
    sync_push,
    sync_status,
)


@pytest.fixture
def temp_dirs(tmp_path: Path) -> tuple[Path, Path, Path]:
    claude_dir = tmp_path / ".claude"
    sync_repo = tmp_path / ".claude-sync-repo"
    backup_dir = tmp_path / ".claude-sync-backup"
    claude_dir.mkdir()
    return claude_dir, sync_repo, backup_dir


def _dir_args(dirs: tuple[Path, Path, Path]) -> dict[str, str]:
    return {
        "claude_dir": str(dirs[0]),
        "sync_repo": str(dirs[1]),
        "backup_dir": str(dirs[2]),
    }


class TestSyncInit:
    def test_init_creates_repo(self, temp_dirs: tuple[Path, Path, Path]) -> None:
        result = asyncio.run(sync_init(**_dir_args(temp_dirs)))
        assert result["success"] is True
        assert temp_dirs[1].exists()
        assert (temp_dirs[1] / ".git").exists()
        assert (temp_dirs[1] / ".gitignore").exists()

    def test_init_with_remote(self, temp_dirs: tuple[Path, Path, Path]) -> None:
        result = asyncio.run(
            sync_init(remote_url="https://github.com/test/repo.git", **_dir_args(temp_dirs))
        )
        assert result["success"] is True
        assert result["remote"] == "https://github.com/test/repo.git"


class TestSyncPush:
    def test_push_syncs_files(self, temp_dirs: tuple[Path, Path, Path]) -> None:
        # init
        asyncio.run(sync_init(**_dir_args(temp_dirs)))
        # create a file to sync
        (temp_dirs[0] / "CLAUDE.md").write_text("# Test")
        result = asyncio.run(sync_push(**_dir_args(temp_dirs)))
        assert result["files_synced"] >= 1
        assert result["committed"] is True
        assert result["secrets_found"] is False

    def test_push_blocks_secrets(self, temp_dirs: tuple[Path, Path, Path]) -> None:
        asyncio.run(sync_init(**_dir_args(temp_dirs)))
        # write a file with a secret pattern
        (temp_dirs[0] / "CLAUDE.md").write_text(
            "api_key = sk-ant-api03-AAAAAAAAAAAAAAAAAAAAAAAAA"
        )
        result = asyncio.run(sync_push(**_dir_args(temp_dirs)))
        assert result["secrets_found"] is True
        assert result["committed"] is False

    def test_push_no_changes(self, temp_dirs: tuple[Path, Path, Path]) -> None:
        asyncio.run(sync_init(**_dir_args(temp_dirs)))
        # first push commits .gitignore
        asyncio.run(sync_push(**_dir_args(temp_dirs)))
        # second push should have no changes
        result = asyncio.run(sync_push(**_dir_args(temp_dirs)))
        assert result["committed"] is False


class TestSyncStatus:
    def test_status_in_sync(self, temp_dirs: tuple[Path, Path, Path]) -> None:
        asyncio.run(sync_init(**_dir_args(temp_dirs)))
        result = asyncio.run(sync_status(**_dir_args(temp_dirs)))
        assert result["in_sync"] is True
        assert result["changed_files"] == []

    def test_status_detects_changes(self, temp_dirs: tuple[Path, Path, Path]) -> None:
        asyncio.run(sync_init(**_dir_args(temp_dirs)))
        (temp_dirs[0] / "CLAUDE.md").write_text("# New")
        result = asyncio.run(sync_status(**_dir_args(temp_dirs)))
        assert result["in_sync"] is False
        assert "CLAUDE.md" in result["changed_files"]


class TestSyncPull:
    def test_pull_restores_files(self, temp_dirs: tuple[Path, Path, Path]) -> None:
        asyncio.run(sync_init(**_dir_args(temp_dirs)))
        (temp_dirs[0] / "CLAUDE.md").write_text("# Original")
        asyncio.run(sync_push(**_dir_args(temp_dirs)))
        # modify local
        (temp_dirs[0] / "CLAUDE.md").write_text("# Modified")
        result = asyncio.run(sync_pull(**_dir_args(temp_dirs)))
        assert result["files_synced"] >= 1
        assert (temp_dirs[0] / "CLAUDE.md").read_text() == "# Original"


class TestSyncHistory:
    def test_history_returns_entries(self, temp_dirs: tuple[Path, Path, Path]) -> None:
        asyncio.run(sync_init(**_dir_args(temp_dirs)))
        (temp_dirs[0] / "CLAUDE.md").write_text("# v1")
        asyncio.run(sync_push(message="first push", **_dir_args(temp_dirs)))
        result = asyncio.run(sync_history(**_dir_args(temp_dirs)))
        assert result["count"] >= 1
        assert result["entries"][0]["message"] == "first push"

    def test_history_empty(self, temp_dirs: tuple[Path, Path, Path]) -> None:
        asyncio.run(sync_init(**_dir_args(temp_dirs)))
        result = asyncio.run(sync_history(**_dir_args(temp_dirs)))
        assert result["count"] == 0
