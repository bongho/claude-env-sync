"""Claude Code 설정 경로 탐지 모듈."""

from __future__ import annotations

from pathlib import Path


class PathResolver:
    """Claude Code 관련 디렉토리 및 파일 경로를 해석한다."""

    def __init__(
        self,
        claude_dir: Path | None = None,
        sync_repo_dir: Path | None = None,
        config_file: Path | None = None,
        backup_dir: Path | None = None,
    ) -> None:
        home = Path.home()
        self._claude_dir = claude_dir or home / ".claude"
        self._sync_repo_dir = sync_repo_dir or home / ".claude-sync-repo"
        self._config_file = config_file or home / ".claude-sync.toml"
        self._backup_dir = backup_dir or home / ".claude-sync-backup"

    @property
    def claude_dir(self) -> Path:
        return self._claude_dir

    @property
    def sync_repo_dir(self) -> Path:
        return self._sync_repo_dir

    @property
    def config_file(self) -> Path:
        return self._config_file

    @property
    def backup_dir(self) -> Path:
        return self._backup_dir

    def claude_dir_exists(self) -> bool:
        return self._claude_dir.is_dir()

    def resolve(self, relative_path: str) -> Path:
        """Claude 디렉토리 기준으로 상대 경로를 절대 경로로 변환한다."""
        return self._claude_dir / relative_path

    def list_syncable_files(self, patterns: list[str]) -> list[Path]:
        """동기화 대상 패턴에 해당하는 실제 존재하는 파일 목록을 반환한다.

        Args:
            patterns: 동기화 대상 패턴 목록 (예: ["CLAUDE.md", "agents/"])
                     '/'로 끝나면 디렉토리로 간주하여 재귀 탐색.

        Returns:
            존재하는 파일의 절대 경로 목록.
        """
        files: list[Path] = []
        for pattern in patterns:
            target = self._claude_dir / pattern
            if pattern.endswith("/"):
                dir_path = self._claude_dir / pattern.rstrip("/")
                if dir_path.is_dir():
                    files.extend(
                        f for f in dir_path.rglob("*") if f.is_file()
                    )
            elif target.is_file():
                files.append(target)
        return files
