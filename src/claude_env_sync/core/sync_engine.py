"""핵심 동기화 엔진 모듈."""

from __future__ import annotations

import filecmp
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from claude_env_sync.core.git_ops import GitOps
from claude_env_sync.core.path_resolver import PathResolver
from claude_env_sync.models.sync_rules import (
    SyncTier,
    get_excluded_patterns,
    get_rules_by_tier,
)
from claude_env_sync.utils.security import generate_gitignore, scan_for_secrets


@dataclass
class SyncResult:
    """동기화 결과."""

    files_synced: int = 0
    committed: bool = False
    secrets_found: bool = False
    secret_details: list[str] = field(default_factory=list)
    message: str = ""


@dataclass
class SyncStatus:
    """동기화 상태."""

    in_sync: bool = True
    changed_files: list[str] = field(default_factory=list)
    last_sync: str | None = None


class SyncEngine:
    """Claude 설정 동기화 엔진."""

    def __init__(
        self,
        claude_dir: Path,
        sync_repo_dir: Path,
        backup_dir: Path,
        max_tier: SyncTier = SyncTier.TIER2,
    ) -> None:
        self._claude_dir = claude_dir
        self._sync_repo_dir = sync_repo_dir
        self._backup_dir = backup_dir
        self._max_tier = max_tier
        self._path_resolver = PathResolver(
            claude_dir=claude_dir,
            sync_repo_dir=sync_repo_dir,
            backup_dir=backup_dir,
        )
        self._git_ops = GitOps(sync_repo_dir)
        self._excluded = get_excluded_patterns()

    @property
    def git_ops(self) -> GitOps:
        return self._git_ops

    def initialize(self, remote_url: str | None = None) -> None:
        """동기화 환경을 초기화한다."""
        self._sync_repo_dir.mkdir(parents=True, exist_ok=True)
        self._git_ops.init_repo()

        gitignore_path = self._sync_repo_dir / ".gitignore"
        gitignore_path.write_text(generate_gitignore())

        if remote_url:
            self._git_ops.add_remote(remote_url)

    def push(self, message: str | None = None) -> SyncResult:
        """Claude 설정을 동기화 저장소로 push한다."""
        result = SyncResult()

        secrets = scan_for_secrets(self._claude_dir)
        if secrets:
            result.secrets_found = True
            result.secret_details = [
                f"{s.file_path.name}:{s.line_number} - {s.pattern_name}"
                for s in secrets
            ]
            result.message = f"시크릿 {len(secrets)}건 감지. Push를 중단합니다."
            return result

        files_copied = self._copy_to_sync_repo()
        result.files_synced = files_copied

        committed = self._git_ops.add_and_commit(message)
        result.committed = committed

        if committed:
            result.message = f"{files_copied}개 파일 동기화 완료."
        else:
            result.message = "변경 사항 없음."

        return result

    def pull(self) -> SyncResult:
        """동기화 저장소의 설정을 Claude 디렉토리로 복원한다."""
        result = SyncResult()

        self._create_backup()

        files_copied = self._copy_from_sync_repo()
        result.files_synced = files_copied
        result.message = f"{files_copied}개 파일 복원 완료."

        return result

    def status(self) -> SyncStatus:
        """현재 동기화 상태를 조회한다."""
        changed = self._find_changed_files()
        log = self._git_ops.get_log(limit=1)
        last_sync = log[0].date.isoformat() if log else None

        return SyncStatus(
            in_sync=len(changed) == 0,
            changed_files=changed,
            last_sync=last_sync,
        )

    def _get_sync_patterns(self) -> list[str]:
        """동기화 대상 패턴 목록을 반환한다."""
        rules = get_rules_by_tier(self._max_tier)
        return [r.pattern for r in rules]

    def _is_excluded(self, relative_path: str) -> bool:
        """제외 대상인지 확인한다."""
        for pattern in self._excluded:
            if pattern.endswith("/"):
                stripped = pattern.rstrip("/")
                if relative_path.startswith((pattern, stripped)):
                    return True
            elif relative_path == pattern or relative_path.endswith("/" + pattern):
                return True
        return False

    def _copy_to_sync_repo(self) -> int:
        """Claude 디렉토리의 파일을 동기화 저장소로 복사한다."""
        patterns = self._get_sync_patterns()
        files = self._path_resolver.list_syncable_files(patterns)
        count = 0

        for src in files:
            relative = src.relative_to(self._claude_dir)
            if self._is_excluded(str(relative)):
                continue
            dst = self._sync_repo_dir / relative
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            count += 1

        return count

    def _copy_from_sync_repo(self) -> int:
        """동기화 저장소의 파일을 Claude 디렉토리로 복사한다."""
        count = 0
        for src in self._sync_repo_dir.rglob("*"):
            if not src.is_file():
                continue
            relative = src.relative_to(self._sync_repo_dir)
            if str(relative).startswith(".git"):
                continue
            if relative.name == ".gitignore":
                continue

            dst = self._claude_dir / relative
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            count += 1

        return count

    def _create_backup(self) -> None:
        """현재 Claude 디렉토리를 백업한다."""
        if self._backup_dir.exists():
            shutil.rmtree(self._backup_dir)
        self._backup_dir.mkdir(parents=True)

        patterns = self._get_sync_patterns()
        files = self._path_resolver.list_syncable_files(patterns)

        for src in files:
            relative = src.relative_to(self._claude_dir)
            dst = self._backup_dir / relative
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    def _find_changed_files(self) -> list[str]:
        """Claude 디렉토리와 동기화 저장소 간 차이를 찾는다."""
        changed: list[str] = []
        patterns = self._get_sync_patterns()
        files = self._path_resolver.list_syncable_files(patterns)

        for src in files:
            relative = src.relative_to(self._claude_dir)
            if self._is_excluded(str(relative)):
                continue
            synced = self._sync_repo_dir / relative
            if not synced.exists():
                changed.append(str(relative))
            elif not filecmp.cmp(src, synced, shallow=False):
                changed.append(str(relative))

        return changed
