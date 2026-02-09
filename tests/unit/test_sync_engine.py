"""sync_engine 모듈 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from claude_env_sync.core.sync_engine import SyncEngine, SyncResult


def _create_mock_claude_dir(base: Path) -> Path:
    """테스트용 mock Claude 디렉토리를 생성한다."""
    claude_dir = base / ".claude"
    claude_dir.mkdir()
    (claude_dir / "CLAUDE.md").write_text("# My Config")
    (claude_dir / "settings.json").write_text('{"theme": "dark"}')

    agents_dir = claude_dir / "agents"
    agents_dir.mkdir()
    (agents_dir / "coder.md").write_text("agent config")

    plugins_dir = claude_dir / "plugins"
    plugins_dir.mkdir()
    (plugins_dir / "installed_plugins.json").write_text("[]")

    skills_dir = claude_dir / "skills"
    skills_dir.mkdir()
    (skills_dir / "commit.md").write_text("skill config")

    (claude_dir / "history.jsonl").write_text('{"cmd": "test"}\n')

    # 제외 대상
    debug_dir = claude_dir / "debug"
    debug_dir.mkdir()
    (debug_dir / "log.txt").write_text("debug log")

    cache_dir = claude_dir / "cache"
    cache_dir.mkdir()
    (cache_dir / "data.bin").write_text("cache")

    return claude_dir


@pytest.fixture
def mock_env(tmp_path: Path):
    """테스트 환경: claude_dir + sync_repo_dir."""
    claude_dir = _create_mock_claude_dir(tmp_path)
    sync_repo_dir = tmp_path / "sync-repo"
    sync_repo_dir.mkdir()
    backup_dir = tmp_path / "backup"
    return claude_dir, sync_repo_dir, backup_dir


@pytest.fixture
def engine(mock_env) -> SyncEngine:
    claude_dir, sync_repo_dir, backup_dir = mock_env
    return SyncEngine(
        claude_dir=claude_dir,
        sync_repo_dir=sync_repo_dir,
        backup_dir=backup_dir,
    )


class TestSyncEngineInit:
    """SyncEngine 초기화 테스트."""

    def test_initialize_creates_git_repo(self, engine: SyncEngine, mock_env):
        """초기화하면 동기화 저장소에 Git repo가 생성되어야 한다."""
        _, sync_repo_dir, _ = mock_env
        engine.initialize()
        assert (sync_repo_dir / ".git").is_dir()

    def test_initialize_creates_gitignore(self, engine: SyncEngine, mock_env):
        """초기화하면 .gitignore가 생성되어야 한다."""
        _, sync_repo_dir, _ = mock_env
        engine.initialize()
        assert (sync_repo_dir / ".gitignore").is_file()

    def test_initialize_with_remote(self, engine: SyncEngine, mock_env):
        """원격 URL을 지정하여 초기화할 수 있어야 한다."""
        engine.initialize(remote_url="https://github.com/test/repo.git")
        assert engine.git_ops.has_remote()


class TestSyncEnginePush:
    """Push 동기화 테스트."""

    def test_push_copies_tier1_files(self, engine: SyncEngine, mock_env):
        """push는 Tier 1 파일을 동기화 저장소로 복사해야 한다."""
        claude_dir, sync_repo_dir, _ = mock_env
        engine.initialize()
        engine.push()
        assert (sync_repo_dir / "CLAUDE.md").is_file()
        assert (sync_repo_dir / "settings.json").is_file()
        assert (sync_repo_dir / "agents" / "coder.md").is_file()

    def test_push_copies_tier2_files(self, engine: SyncEngine, mock_env):
        """push는 Tier 2 파일도 복사해야 한다."""
        _, sync_repo_dir, _ = mock_env
        engine.initialize()
        engine.push()
        assert (sync_repo_dir / "skills" / "commit.md").is_file()
        assert (sync_repo_dir / "history.jsonl").is_file()

    def test_push_excludes_debug(self, engine: SyncEngine, mock_env):
        """push는 debug 디렉토리를 제외해야 한다."""
        _, sync_repo_dir, _ = mock_env
        engine.initialize()
        engine.push()
        assert not (sync_repo_dir / "debug").exists()

    def test_push_excludes_cache(self, engine: SyncEngine, mock_env):
        """push는 cache 디렉토리를 제외해야 한다."""
        _, sync_repo_dir, _ = mock_env
        engine.initialize()
        engine.push()
        assert not (sync_repo_dir / "cache").exists()

    def test_push_creates_commit(self, engine: SyncEngine, mock_env):
        """push는 Git 커밋을 생성해야 한다."""
        engine.initialize()
        result = engine.push()
        assert result.committed is True
        log = engine.git_ops.get_log(limit=1)
        assert len(log) == 1

    def test_push_returns_sync_result(self, engine: SyncEngine, mock_env):
        """push는 SyncResult를 반환해야 한다."""
        engine.initialize()
        result = engine.push()
        assert isinstance(result, SyncResult)
        assert result.files_synced > 0

    def test_push_preserves_content(self, engine: SyncEngine, mock_env):
        """push된 파일 내용이 원본과 동일해야 한다."""
        claude_dir, sync_repo_dir, _ = mock_env
        engine.initialize()
        engine.push()
        assert (sync_repo_dir / "CLAUDE.md").read_text() == "# My Config"
        assert (sync_repo_dir / "settings.json").read_text() == '{"theme": "dark"}'

    def test_push_no_commit_when_unchanged(self, engine: SyncEngine, mock_env):
        """변경 사항이 없으면 커밋하지 않아야 한다."""
        engine.initialize()
        engine.push()
        result = engine.push()
        assert result.committed is False


class TestSyncEnginePull:
    """Pull 동기화 테스트."""

    def test_pull_restores_files(self, engine: SyncEngine, mock_env):
        """pull은 동기화 저장소의 파일을 Claude 디렉토리로 복사해야 한다."""
        claude_dir, sync_repo_dir, _ = mock_env
        engine.initialize()
        engine.push()

        # Claude 디렉토리의 파일을 수정
        (claude_dir / "CLAUDE.md").write_text("# Modified")

        engine.pull()
        assert (claude_dir / "CLAUDE.md").read_text() == "# My Config"

    def test_pull_creates_backup(self, engine: SyncEngine, mock_env):
        """pull 전에 현재 상태를 백업해야 한다."""
        claude_dir, _, backup_dir = mock_env
        engine.initialize()
        engine.push()

        (claude_dir / "CLAUDE.md").write_text("# Modified")
        engine.pull()
        assert backup_dir.exists()

    def test_pull_returns_sync_result(self, engine: SyncEngine, mock_env):
        """pull은 SyncResult를 반환해야 한다."""
        engine.initialize()
        engine.push()
        result = engine.pull()
        assert isinstance(result, SyncResult)


class TestSyncEngineStatus:
    """상태 조회 테스트."""

    def test_status_after_push(self, engine: SyncEngine, mock_env):
        """push 후 status는 in_sync를 반환해야 한다."""
        engine.initialize()
        engine.push()
        status = engine.status()
        assert status.in_sync is True

    def test_status_after_local_change(self, engine: SyncEngine, mock_env):
        """로컬 변경 후 status는 not_in_sync를 반환해야 한다."""
        claude_dir, _, _ = mock_env
        engine.initialize()
        engine.push()
        (claude_dir / "CLAUDE.md").write_text("# Changed!")
        status = engine.status()
        assert status.in_sync is False

    def test_status_has_changed_files(self, engine: SyncEngine, mock_env):
        """status는 변경된 파일 목록을 포함해야 한다."""
        claude_dir, _, _ = mock_env
        engine.initialize()
        engine.push()
        (claude_dir / "CLAUDE.md").write_text("# Changed!")
        status = engine.status()
        assert len(status.changed_files) > 0


class TestSyncEngineSecurityCheck:
    """보안 검사 테스트."""

    def test_push_blocks_on_secrets(self, mock_env):
        """시크릿이 감지되면 push를 차단해야 한다."""
        claude_dir, sync_repo_dir, backup_dir = mock_env
        (claude_dir / "settings.json").write_text(
            '{"api_key": "sk-ant-api03-abcdefghij1234567890klmnopqrstuvwxyz"}'
        )
        eng = SyncEngine(
            claude_dir=claude_dir,
            sync_repo_dir=sync_repo_dir,
            backup_dir=backup_dir,
        )
        eng.initialize()
        result = eng.push()
        assert result.secrets_found is True
        assert result.committed is False


class TestSyncEngineExclude:
    """제외 패턴 테스트."""

    def test_is_excluded_dir_pattern(self, mock_env):
        """디렉토리 제외 패턴이 동작해야 한다."""
        claude_dir, sync_repo_dir, backup_dir = mock_env
        engine = SyncEngine(
            claude_dir=claude_dir,
            sync_repo_dir=sync_repo_dir,
            backup_dir=backup_dir,
        )
        assert engine._is_excluded("debug/log.txt") is True
        assert engine._is_excluded("cache/data.bin") is True

    def test_is_excluded_file_pattern(self, mock_env):
        """파일명 제외 패턴이 동작해야 한다."""
        claude_dir, sync_repo_dir, backup_dir = mock_env
        engine = SyncEngine(
            claude_dir=claude_dir,
            sync_repo_dir=sync_repo_dir,
            backup_dir=backup_dir,
        )
        assert engine._is_excluded("statusline.log") is True

    def test_is_excluded_returns_false_for_valid(self, mock_env):
        """동기화 대상 파일은 제외되지 않아야 한다."""
        claude_dir, sync_repo_dir, backup_dir = mock_env
        engine = SyncEngine(
            claude_dir=claude_dir,
            sync_repo_dir=sync_repo_dir,
            backup_dir=backup_dir,
        )
        assert engine._is_excluded("CLAUDE.md") is False

    def test_status_detects_new_unsynced_file(self, mock_env):
        """동기화 저장소에 없는 새 파일을 감지해야 한다."""
        claude_dir, sync_repo_dir, backup_dir = mock_env
        engine = SyncEngine(
            claude_dir=claude_dir,
            sync_repo_dir=sync_repo_dir,
            backup_dir=backup_dir,
        )
        engine.initialize()
        engine.push()

        # 새 파일 추가
        (claude_dir / "agents" / "new_agent.md").write_text("new agent")
        status = engine.status()
        assert status.in_sync is False
        assert any("new_agent" in f for f in status.changed_files)


class TestSyncEnginePullDetails:
    """Pull 상세 동작 테스트."""

    def test_pull_skips_gitignore(self, mock_env):
        """.gitignore는 Claude 디렉토리로 복사하지 않아야 한다."""
        claude_dir, sync_repo_dir, backup_dir = mock_env
        engine = SyncEngine(
            claude_dir=claude_dir,
            sync_repo_dir=sync_repo_dir,
            backup_dir=backup_dir,
        )
        engine.initialize()
        engine.push()
        engine.pull()
        assert not (claude_dir / ".gitignore").exists()

    def test_pull_clears_existing_backup(self, mock_env):
        """기존 백업 디렉토리가 있으면 삭제 후 재생성해야 한다."""
        claude_dir, sync_repo_dir, backup_dir = mock_env
        engine = SyncEngine(
            claude_dir=claude_dir,
            sync_repo_dir=sync_repo_dir,
            backup_dir=backup_dir,
        )
        engine.initialize()
        engine.push()

        # 기존 백업 생성
        backup_dir.mkdir(parents=True, exist_ok=True)
        (backup_dir / "old_file.txt").write_text("old")

        engine.pull()
        assert backup_dir.exists()
        assert not (backup_dir / "old_file.txt").exists()

    def test_pull_skips_subdirectory_gitignore(self, mock_env):
        """서브디렉토리의 .gitignore도 복사하지 않아야 한다."""
        claude_dir, sync_repo_dir, backup_dir = mock_env
        engine = SyncEngine(
            claude_dir=claude_dir,
            sync_repo_dir=sync_repo_dir,
            backup_dir=backup_dir,
        )
        engine.initialize()
        engine.push()

        # 서브디렉토리에 .gitignore 생성
        sub_dir = sync_repo_dir / "agents"
        sub_dir.mkdir(exist_ok=True)
        (sub_dir / ".gitignore").write_text("*.tmp")

        engine.pull()
        assert not (claude_dir / "agents" / ".gitignore").exists()

    def test_push_excludes_file_in_synced_dir(self, mock_env):
        """동기화 디렉토리 내 제외 파일은 복사하지 않아야 한다."""
        claude_dir, sync_repo_dir, backup_dir = mock_env
        # agents/ 디렉토리 안에 제외 대상 파일 추가
        (claude_dir / "agents" / "stats-cache.json").write_text("{}")
        engine = SyncEngine(
            claude_dir=claude_dir,
            sync_repo_dir=sync_repo_dir,
            backup_dir=backup_dir,
        )
        engine.initialize()
        engine.push()
        assert not (sync_repo_dir / "agents" / "stats-cache.json").exists()

    def test_status_excludes_file_in_diff(self, mock_env):
        """상태 조회 시 제외 파일은 변경 목록에 포함하지 않아야 한다."""
        claude_dir, sync_repo_dir, backup_dir = mock_env
        engine = SyncEngine(
            claude_dir=claude_dir,
            sync_repo_dir=sync_repo_dir,
            backup_dir=backup_dir,
        )
        engine.initialize()
        engine.push()

        # 제외 대상 파일을 agents 안에 추가
        (claude_dir / "agents" / "stats-cache.json").write_text("{}")
        status = engine.status()
        assert all(
            "stats-cache.json" not in f for f in status.changed_files
        )
