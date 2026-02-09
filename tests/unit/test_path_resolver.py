"""path_resolver 모듈 테스트."""

from pathlib import Path

from claude_env_sync.core.path_resolver import PathResolver


class TestPathResolver:
    """Claude 설정 경로 탐지 테스트."""

    def test_default_claude_dir_returns_path(self):
        """기본 Claude 디렉토리 경로를 반환해야 한다."""
        resolver = PathResolver()
        result = resolver.claude_dir
        assert isinstance(result, Path)

    def test_claude_dir_is_dot_claude_in_home(self):
        """~/.claude 경로를 반환해야 한다."""
        resolver = PathResolver()
        expected = Path.home() / ".claude"
        assert resolver.claude_dir == expected

    def test_custom_claude_dir(self):
        """사용자 지정 경로를 사용할 수 있어야 한다."""
        custom = Path("/tmp/test-claude")
        resolver = PathResolver(claude_dir=custom)
        assert resolver.claude_dir == custom

    def test_sync_repo_dir_default(self):
        """기본 동기화 저장소 경로를 반환해야 한다."""
        resolver = PathResolver()
        expected = Path.home() / ".claude-sync-repo"
        assert resolver.sync_repo_dir == expected

    def test_custom_sync_repo_dir(self):
        """사용자 지정 동기화 저장소 경로를 사용할 수 있어야 한다."""
        custom = Path("/tmp/test-sync-repo")
        resolver = PathResolver(sync_repo_dir=custom)
        assert resolver.sync_repo_dir == custom

    def test_config_file_path(self):
        """설정 파일 경로를 반환해야 한다."""
        resolver = PathResolver()
        expected = Path.home() / ".claude-sync.toml"
        assert resolver.config_file == expected

    def test_backup_dir(self):
        """백업 디렉토리 경로를 반환해야 한다."""
        resolver = PathResolver()
        expected = Path.home() / ".claude-sync-backup"
        assert resolver.backup_dir == expected

    def test_claude_dir_exists_returns_true(self, tmp_path):
        """Claude 디렉토리가 존재하면 True를 반환해야 한다."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        resolver = PathResolver(claude_dir=claude_dir)
        assert resolver.claude_dir_exists() is True

    def test_claude_dir_exists_returns_false(self, tmp_path):
        """Claude 디렉토리가 없으면 False를 반환해야 한다."""
        claude_dir = tmp_path / ".claude"
        resolver = PathResolver(claude_dir=claude_dir)
        assert resolver.claude_dir_exists() is False

    def test_resolve_file_path(self, tmp_path):
        """Claude 디렉토리 내 파일 경로를 해석해야 한다."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        resolver = PathResolver(claude_dir=claude_dir)
        result = resolver.resolve("CLAUDE.md")
        assert result == claude_dir / "CLAUDE.md"

    def test_resolve_nested_path(self, tmp_path):
        """중첩 경로도 해석해야 한다."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        resolver = PathResolver(claude_dir=claude_dir)
        result = resolver.resolve("agents/my-agent.md")
        assert result == claude_dir / "agents" / "my-agent.md"

    def test_list_existing_files(self, tmp_path):
        """존재하는 파일 목록을 반환해야 한다."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "CLAUDE.md").write_text("# Test")
        (claude_dir / "settings.json").write_text("{}")
        agents_dir = claude_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "test.md").write_text("agent")

        resolver = PathResolver(claude_dir=claude_dir)
        files = resolver.list_syncable_files(["CLAUDE.md", "settings.json", "agents/"])
        assert claude_dir / "CLAUDE.md" in files
        assert claude_dir / "settings.json" in files
        assert claude_dir / "agents" / "test.md" in files

    def test_list_existing_files_skips_missing(self, tmp_path):
        """존재하지 않는 파일은 건너뛰어야 한다."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "CLAUDE.md").write_text("# Test")

        resolver = PathResolver(claude_dir=claude_dir)
        files = resolver.list_syncable_files(["CLAUDE.md", "nonexistent.json"])
        assert claude_dir / "CLAUDE.md" in files
        assert len([f for f in files if f.name == "nonexistent.json"]) == 0

    def test_list_directory_recursively(self, tmp_path):
        """디렉토리는 재귀적으로 파일을 수집해야 한다."""
        claude_dir = tmp_path / ".claude"
        skills_dir = claude_dir / "skills" / "sub"
        skills_dir.mkdir(parents=True)
        (claude_dir / "skills" / "a.md").write_text("a")
        (skills_dir / "b.md").write_text("b")

        resolver = PathResolver(claude_dir=claude_dir)
        files = resolver.list_syncable_files(["skills/"])
        assert claude_dir / "skills" / "a.md" in files
        assert claude_dir / "skills" / "sub" / "b.md" in files
