"""CLI 모듈 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from claude_env_sync.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_claude_env(tmp_path: Path):
    """mock Claude 환경을 생성한다."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "CLAUDE.md").write_text("# Test Config")
    (claude_dir / "settings.json").write_text("{}")

    agents_dir = claude_dir / "agents"
    agents_dir.mkdir()
    (agents_dir / "test.md").write_text("agent")

    plugins_dir = claude_dir / "plugins"
    plugins_dir.mkdir()
    (plugins_dir / "installed_plugins.json").write_text("[]")

    skills_dir = claude_dir / "skills"
    skills_dir.mkdir()
    (skills_dir / "test.md").write_text("skill")

    (claude_dir / "history.jsonl").write_text("{}\n")

    sync_repo = tmp_path / "sync-repo"
    backup_dir = tmp_path / "backup"

    return claude_dir, sync_repo, backup_dir


class TestCliVersion:
    """버전 표시 테스트."""

    def test_version_flag(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestCliInit:
    """init 명령어 테스트."""

    def test_init_creates_sync_repo(self, runner, mock_claude_env):
        claude_dir, sync_repo, backup_dir = mock_claude_env
        result = runner.invoke(main, [
            "init",
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
        ])
        assert result.exit_code == 0
        assert (sync_repo / ".git").is_dir()

    def test_init_with_remote(self, runner, mock_claude_env):
        claude_dir, sync_repo, backup_dir = mock_claude_env
        result = runner.invoke(main, [
            "init",
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
            "--remote", "https://github.com/test/repo.git",
        ])
        assert result.exit_code == 0

    def test_init_shows_success_message(self, runner, mock_claude_env):
        claude_dir, sync_repo, backup_dir = mock_claude_env
        result = runner.invoke(main, [
            "init",
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
        ])
        assert "초기화" in result.output or "init" in result.output.lower()


class TestCliPush:
    """push 명령어 테스트."""

    def test_push_syncs_files(self, runner, mock_claude_env):
        claude_dir, sync_repo, backup_dir = mock_claude_env
        common_args = [
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
        ]
        runner.invoke(main, ["init"] + common_args)
        result = runner.invoke(main, ["push"] + common_args)
        assert result.exit_code == 0
        assert (sync_repo / "CLAUDE.md").is_file()

    def test_push_shows_result(self, runner, mock_claude_env):
        claude_dir, sync_repo, backup_dir = mock_claude_env
        common_args = [
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
        ]
        runner.invoke(main, ["init"] + common_args)
        result = runner.invoke(main, ["push"] + common_args)
        assert "동기화" in result.output or "sync" in result.output.lower()


class TestCliPull:
    """pull 명령어 테스트."""

    def test_pull_restores_files(self, runner, mock_claude_env):
        claude_dir, sync_repo, backup_dir = mock_claude_env
        common_args = [
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
        ]
        runner.invoke(main, ["init"] + common_args)
        runner.invoke(main, ["push"] + common_args)

        (claude_dir / "CLAUDE.md").write_text("# Modified")
        result = runner.invoke(main, ["pull"] + common_args)
        assert result.exit_code == 0
        assert (claude_dir / "CLAUDE.md").read_text() == "# Test Config"


class TestCliStatus:
    """status 명령어 테스트."""

    def test_status_in_sync(self, runner, mock_claude_env):
        claude_dir, sync_repo, backup_dir = mock_claude_env
        common_args = [
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
        ]
        runner.invoke(main, ["init"] + common_args)
        runner.invoke(main, ["push"] + common_args)
        result = runner.invoke(main, ["status"] + common_args)
        assert result.exit_code == 0

    def test_status_shows_changes(self, runner, mock_claude_env):
        claude_dir, sync_repo, backup_dir = mock_claude_env
        common_args = [
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
        ]
        runner.invoke(main, ["init"] + common_args)
        runner.invoke(main, ["push"] + common_args)
        (claude_dir / "CLAUDE.md").write_text("# Changed!")
        result = runner.invoke(main, ["status"] + common_args)
        assert "CLAUDE.md" in result.output


class TestCliHistory:
    """history 명령어 테스트."""

    def test_history_shows_commits(self, runner, mock_claude_env):
        claude_dir, sync_repo, backup_dir = mock_claude_env
        common_args = [
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
        ]
        runner.invoke(main, ["init"] + common_args)
        runner.invoke(main, ["push"] + common_args)
        result = runner.invoke(main, ["history"] + common_args)
        assert result.exit_code == 0

    def test_history_limit(self, runner, mock_claude_env):
        claude_dir, sync_repo, backup_dir = mock_claude_env
        common_args = [
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
        ]
        runner.invoke(main, ["init"] + common_args)
        runner.invoke(main, ["push"] + common_args)
        result = runner.invoke(main, ["history", "--limit", "5"] + common_args)
        assert result.exit_code == 0


class TestCliPushSecrets:
    """push 시크릿 감지 테스트."""

    def test_push_blocks_secrets_shows_message(self, runner, mock_claude_env):
        """시크릿 감지 시 CLI가 경고 메시지를 출력해야 한다."""
        claude_dir, sync_repo, backup_dir = mock_claude_env
        (claude_dir / "settings.json").write_text(
            '{"key": "sk-ant-api03-abcdefghij1234567890klmnopqrstuvwxyz"}'
        )
        common_args = [
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
        ]
        runner.invoke(main, ["init"] + common_args)
        result = runner.invoke(main, ["push"] + common_args)
        assert result.exit_code == 0
        assert "시크릿" in result.output or "secret" in result.output.lower()

    def test_push_no_changes_shows_message(self, runner, mock_claude_env):
        """변경 없을 때 메시지를 표시해야 한다."""
        claude_dir, sync_repo, backup_dir = mock_claude_env
        common_args = [
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
        ]
        runner.invoke(main, ["init"] + common_args)
        runner.invoke(main, ["push"] + common_args)
        result = runner.invoke(main, ["push"] + common_args)
        assert result.exit_code == 0
        assert "변경" in result.output or "없음" in result.output


class TestCliHistoryEmpty:
    """빈 이력 테스트."""

    def test_history_empty_shows_message(self, runner, mock_claude_env):
        """커밋 이력이 없으면 메시지를 표시해야 한다."""
        claude_dir, sync_repo, backup_dir = mock_claude_env
        common_args = [
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
        ]
        runner.invoke(main, ["init"] + common_args)
        result = runner.invoke(main, ["history"] + common_args)
        assert result.exit_code == 0
        assert "이력" in result.output or "없습니다" in result.output


class TestCliHookInstall:
    """hook install/uninstall CLI 테스트."""

    def test_hook_install_fresh(self, runner, tmp_path):
        """hook install이 동작해야 한다."""
        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("# existing\n")
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("claude_env_sync.cli._resolve_rc_files", lambda s: [rc_file])
            result = runner.invoke(main, ["hook", "install"])
        assert result.exit_code == 0
        assert "설치" in result.output or "Hook" in result.output

    def test_hook_install_already_installed(self, runner, tmp_path):
        """이미 설치되어 있으면 해당 메시지를 표시해야 한다."""
        from claude_env_sync.hooks.install import install_shell_hook

        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("")
        install_shell_hook(rc_file)

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("claude_env_sync.cli._resolve_rc_files", lambda s: [rc_file])
            result = runner.invoke(main, ["hook", "install"])
        assert result.exit_code == 0
        assert "이미" in result.output

    def test_hook_uninstall_installed(self, runner, tmp_path):
        """hook uninstall이 동작해야 한다."""
        from claude_env_sync.hooks.install import install_shell_hook

        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("")
        install_shell_hook(rc_file)

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("claude_env_sync.cli._resolve_rc_files", lambda s: [rc_file])
            result = runner.invoke(main, ["hook", "uninstall"])
        assert result.exit_code == 0
        assert "제거" in result.output

    def test_hook_uninstall_not_installed(self, runner, tmp_path):
        """설치되지 않은 상태에서 uninstall 시 메시지를 표시해야 한다."""
        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("# nothing\n")

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("claude_env_sync.cli._resolve_rc_files", lambda s: [rc_file])
            result = runner.invoke(main, ["hook", "uninstall"])
        assert result.exit_code == 0
        assert "설치되지" in result.output


class TestResolveRcFiles:
    """_resolve_rc_files 함수 테스트."""

    def test_bash_shell(self):
        from claude_env_sync.cli import _resolve_rc_files

        result = _resolve_rc_files("bash")
        assert len(result) == 1
        assert result[0].name == ".bashrc"

    def test_zsh_shell(self):
        from claude_env_sync.cli import _resolve_rc_files

        result = _resolve_rc_files("zsh")
        assert len(result) == 1
        assert result[0].name == ".zshrc"

    def test_auto_shell_returns_list(self):
        from claude_env_sync.cli import _resolve_rc_files

        result = _resolve_rc_files("auto")
        assert isinstance(result, list)
        assert len(result) >= 1


class TestCliRestore:
    """restore 명령어 테스트."""

    def test_restore_reverts_to_previous(self, runner, mock_claude_env):
        claude_dir, sync_repo, backup_dir = mock_claude_env
        common_args = [
            "--claude-dir", str(claude_dir),
            "--sync-repo", str(sync_repo),
            "--backup-dir", str(backup_dir),
        ]
        runner.invoke(main, ["init"] + common_args)
        runner.invoke(main, ["push"] + common_args)

        (claude_dir / "CLAUDE.md").write_text("# Version 2")
        runner.invoke(main, ["push"] + common_args)

        # 첫 번째 커밋 SHA 가져오기
        from claude_env_sync.core.git_ops import GitOps

        git_ops = GitOps(sync_repo)
        git_ops.init_repo()
        log = git_ops.get_log(limit=10)
        first_sha = log[-1].sha

        result = runner.invoke(main, ["restore", first_sha] + common_args)
        assert result.exit_code == 0
