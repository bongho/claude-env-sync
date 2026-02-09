"""hooks 모듈 테스트."""

from __future__ import annotations

from pathlib import Path

from claude_env_sync.hooks.install import (
    HOOK_MARKER,
    generate_hook_script,
    install_shell_hook,
    is_hook_installed,
    uninstall_shell_hook,
)


class TestGenerateHookScript:
    """Hook 스크립트 생성 테스트."""

    def test_returns_string(self):
        script = generate_hook_script()
        assert isinstance(script, str)

    def test_contains_claude_sync_command(self):
        script = generate_hook_script()
        assert "claude-sync" in script

    def test_contains_marker(self):
        script = generate_hook_script()
        assert HOOK_MARKER in script

    def test_contains_pull_on_start(self):
        script = generate_hook_script()
        assert "pull" in script


class TestInstallShellHook:
    """Shell hook 설치 테스트."""

    def test_install_to_bashrc(self, tmp_path: Path):
        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("# existing config\n")
        install_shell_hook(rc_file)
        content = rc_file.read_text()
        assert HOOK_MARKER in content
        assert "claude-sync" in content

    def test_install_to_zshrc(self, tmp_path: Path):
        rc_file = tmp_path / ".zshrc"
        rc_file.write_text("# existing config\n")
        install_shell_hook(rc_file)
        assert HOOK_MARKER in rc_file.read_text()

    def test_install_preserves_existing_content(self, tmp_path: Path):
        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("export PATH=/usr/bin:$PATH\n")
        install_shell_hook(rc_file)
        content = rc_file.read_text()
        assert "export PATH=/usr/bin:$PATH" in content

    def test_install_idempotent(self, tmp_path: Path):
        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("")
        install_shell_hook(rc_file)
        first = rc_file.read_text()
        install_shell_hook(rc_file)
        second = rc_file.read_text()
        assert first == second

    def test_install_creates_file_if_missing(self, tmp_path: Path):
        rc_file = tmp_path / ".bashrc"
        install_shell_hook(rc_file)
        assert rc_file.exists()
        assert HOOK_MARKER in rc_file.read_text()


class TestUninstallShellHook:
    """Shell hook 제거 테스트."""

    def test_uninstall_removes_hook(self, tmp_path: Path):
        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("# existing\n")
        install_shell_hook(rc_file)
        assert HOOK_MARKER in rc_file.read_text()

        uninstall_shell_hook(rc_file)
        assert HOOK_MARKER not in rc_file.read_text()

    def test_uninstall_preserves_other_content(self, tmp_path: Path):
        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("export FOO=bar\n")
        install_shell_hook(rc_file)
        uninstall_shell_hook(rc_file)
        content = rc_file.read_text()
        assert "export FOO=bar" in content

    def test_uninstall_noop_if_not_installed(self, tmp_path: Path):
        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("export FOO=bar\n")
        uninstall_shell_hook(rc_file)
        assert rc_file.read_text() == "export FOO=bar\n"


class TestIsHookInstalled:
    """Hook 설치 여부 확인 테스트."""

    def test_returns_true_when_installed(self, tmp_path: Path):
        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("")
        install_shell_hook(rc_file)
        assert is_hook_installed(rc_file) is True

    def test_returns_false_when_not_installed(self, tmp_path: Path):
        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("# nothing here\n")
        assert is_hook_installed(rc_file) is False

    def test_returns_false_for_missing_file(self, tmp_path: Path):
        rc_file = tmp_path / ".bashrc"
        assert is_hook_installed(rc_file) is False


class TestInstallHookEdgeCases:
    """Hook 설치 엣지 케이스 테스트."""

    def test_install_appends_newline_after_content_without_trailing_newline(
        self, tmp_path: Path
    ):
        """기존 콘텐츠 끝에 개행이 없으면 개행을 추가해야 한다."""
        rc_file = tmp_path / ".bashrc"
        rc_file.write_text("export PATH=/usr/bin")  # 개행 없음
        install_shell_hook(rc_file)
        content = rc_file.read_text()
        # 기존 콘텐츠 뒤에 개행이 있어야 한다
        assert "export PATH=/usr/bin\n" in content
        assert HOOK_MARKER in content

    def test_uninstall_missing_file_is_noop(self, tmp_path: Path):
        """존재하지 않는 파일에 uninstall을 호출해도 에러 없어야 한다."""
        rc_file = tmp_path / ".nonexistent"
        uninstall_shell_hook(rc_file)  # 예외 없이 종료
        assert not rc_file.exists()
