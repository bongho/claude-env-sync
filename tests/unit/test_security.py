"""security 모듈 테스트."""



from claude_env_sync.utils.security import (
    SECRET_PATTERNS,
    generate_gitignore,
    scan_for_secrets,
)


class TestGenerateGitignore:
    """.gitignore 생성 테스트."""

    def test_returns_string(self):
        content = generate_gitignore()
        assert isinstance(content, str)

    def test_excludes_api_key_patterns(self):
        content = generate_gitignore()
        assert "**/api_key*" in content

    def test_excludes_token_patterns(self):
        content = generate_gitignore()
        assert "**/*token*" in content

    def test_excludes_secret_patterns(self):
        content = generate_gitignore()
        assert "**/*secret*" in content

    def test_excludes_credentials(self):
        content = generate_gitignore()
        assert "**/credentials*" in content

    def test_excludes_env_files(self):
        content = generate_gitignore()
        assert "**/.env" in content

    def test_excludes_debug_dir(self):
        content = generate_gitignore()
        assert "debug/" in content

    def test_excludes_cache_dir(self):
        content = generate_gitignore()
        assert "cache/" in content

    def test_excludes_session_env(self):
        content = generate_gitignore()
        assert "session-env/" in content

    def test_excludes_statusline_log(self):
        content = generate_gitignore()
        assert "statusline.log" in content

    def test_writes_to_file(self, tmp_path):
        target = tmp_path / ".gitignore"
        content = generate_gitignore()
        target.write_text(content)
        assert target.exists()
        assert "**/.env" in target.read_text()


class TestScanForSecrets:
    """시크릿 탐지 테스트."""

    def test_detects_anthropic_api_key(self, tmp_path):
        f = tmp_path / "config.json"
        f.write_text('{"api_key": "sk-ant-api03-abcdefghij1234567890klmnopqrst"}')
        findings = scan_for_secrets(tmp_path)
        assert len(findings) > 0
        assert any("sk-ant-" in finding.matched_text for finding in findings)

    def test_detects_openai_api_key(self, tmp_path):
        f = tmp_path / "settings.json"
        f.write_text('{"key": "sk-proj-abcdef1234567890abcdef"}')
        findings = scan_for_secrets(tmp_path)
        assert len(findings) > 0

    def test_no_false_positive_on_clean_file(self, tmp_path):
        f = tmp_path / "CLAUDE.md"
        f.write_text("# My Claude Config\n\nThis is a clean config file.")
        findings = scan_for_secrets(tmp_path)
        assert len(findings) == 0

    def test_detects_generic_token(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text('token = "ghp_abcdefghijklmnopqrstuvwxyz1234567890ABCD"')
        findings = scan_for_secrets(tmp_path)
        assert len(findings) > 0

    def test_scans_recursively(self, tmp_path):
        sub = tmp_path / "subdir"
        sub.mkdir()
        f = sub / "secret.json"
        f.write_text('{"api_key": "sk-ant-api03-hiddenvalue1234567890abcdef"}')
        findings = scan_for_secrets(tmp_path)
        assert len(findings) > 0

    def test_finding_contains_file_path(self, tmp_path):
        f = tmp_path / "config.json"
        f.write_text('{"key": "sk-ant-api03-testvalue1234567890abcdef"}')
        findings = scan_for_secrets(tmp_path)
        assert findings[0].file_path == f

    def test_finding_contains_line_number(self, tmp_path):
        f = tmp_path / "config.json"
        f.write_text('line1\n{"key": "sk-ant-api03-testvalue1234567890abcdef"}\nline3')
        findings = scan_for_secrets(tmp_path)
        assert findings[0].line_number == 2

    def test_skips_binary_files(self, tmp_path):
        f = tmp_path / "binary.bin"
        f.write_bytes(b"\x00\x01sk-ant-api03-test\x02\x03")
        findings = scan_for_secrets(tmp_path)
        assert len(findings) == 0

    def test_secret_patterns_is_nonempty(self):
        assert len(SECRET_PATTERNS) > 0

    def test_scan_skips_permission_error(self, tmp_path):
        """권한 없는 파일은 건너뛰어야 한다."""
        import os

        f = tmp_path / "secret.json"
        f.write_text('{"key": "sk-ant-api03-testvalue1234567890abcdef"}')

        restricted = tmp_path / "restricted.txt"
        restricted.write_text("sk-ant-api03-restrictedvalue12345678901234")
        os.chmod(restricted, 0o000)

        try:
            findings = scan_for_secrets(tmp_path)
            # 권한 있는 파일의 시크릿만 감지
            assert len(findings) >= 1
            assert all(f.file_path.name != "restricted.txt" for f in findings)
        finally:
            os.chmod(restricted, 0o644)
