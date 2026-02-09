"""Git 연산 래퍼 모듈."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from git import InvalidGitRepositoryError, Repo
from git.exc import GitCommandError


class GitOpsError(Exception):
    """Git 연산 중 발생하는 에러."""


@dataclass
class LogEntry:
    """Git 커밋 로그 항목."""

    sha: str
    message: str
    date: datetime
    files_changed: list[str] = field(default_factory=list)


class GitOps:
    """Git 저장소 연산을 관리한다."""

    def __init__(self, repo_dir: Path) -> None:
        self._repo_dir = repo_dir
        self._repo: Repo | None = None

    @property
    def repo(self) -> Repo:
        if self._repo is None:
            msg = "저장소가 초기화되지 않았습니다. init_repo()를 먼저 호출하세요."
            raise GitOpsError(msg)
        return self._repo

    def init_repo(self) -> bool:
        """Git 저장소를 초기화한다. 이미 존재하면 로드한다."""
        try:
            self._repo = Repo(self._repo_dir)
        except (InvalidGitRepositoryError, Exception):
            self._repo = Repo.init(self._repo_dir)
        return True

    def is_initialized(self) -> bool:
        """저장소가 초기화되었는지 확인한다."""
        try:
            Repo(self._repo_dir)
            return True
        except (InvalidGitRepositoryError, Exception):
            return False

    def add_and_commit(self, message: str | None = None) -> bool:
        """모든 변경 사항을 스테이징하고 커밋한다.

        Returns:
            커밋이 생성되면 True, 변경 사항이 없으면 False.
        """
        repo = self.repo
        repo.git.add(A=True)

        if not repo.is_dirty(index=True, working_tree=False, untracked_files=False):
            return False

        if message is None:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"claude-sync: auto-sync {ts}"

        repo.index.commit(message)
        return True

    def get_log(self, limit: int = 20) -> list[LogEntry]:
        """커밋 로그를 반환한다. 최신 순."""
        repo = self.repo
        try:
            repo.head.commit
        except ValueError:
            return []

        entries: list[LogEntry] = []
        for commit in repo.iter_commits(max_count=limit):
            files_changed: list[str] = []
            if commit.parents:
                diff = commit.parents[0].diff(commit)
                files_changed = [d.a_path or d.b_path for d in diff]
            else:
                files_changed = list(commit.stats.files.keys())

            entries.append(
                LogEntry(
                    sha=commit.hexsha,
                    message=commit.message.strip(),
                    date=commit.committed_datetime,
                    files_changed=files_changed,
                )
            )

        return entries

    def add_remote(self, url: str, name: str = "origin") -> None:
        """원격 저장소를 추가한다."""
        repo = self.repo
        if name in [r.name for r in repo.remotes]:
            repo.delete_remote(name)
        repo.create_remote(name, url)

    def has_remote(self, name: str = "origin") -> bool:
        """원격 저장소가 설정되어 있는지 확인한다."""
        return name in [r.name for r in self.repo.remotes]

    def get_remote_url(self, name: str = "origin") -> str | None:
        """원격 저장소 URL을 반환한다."""
        for remote in self.repo.remotes:
            if remote.name == name:
                return remote.url
        return None

    def push(self, remote: str = "origin", branch: str = "main") -> bool:
        """원격 저장소로 push한다.

        Returns:
            성공하면 True.
        """
        try:
            self.repo.remotes[remote].push(branch)
            return True
        except (GitCommandError, IndexError) as e:
            raise GitOpsError(f"Push 실패: {e}") from e

    def pull(self, remote: str = "origin", branch: str = "main") -> bool:
        """원격 저장소에서 pull한다. fast-forward only.

        Returns:
            성공하면 True.
        """
        try:
            self.repo.remotes[remote].pull(branch, ff_only=True)
            return True
        except (GitCommandError, IndexError) as e:
            raise GitOpsError(f"Pull 실패 (충돌 가능성): {e}") from e

    def restore_to(self, sha: str) -> None:
        """특정 커밋 시점으로 작업 트리를 복원한다.

        복원 전 현재 상태를 백업 커밋으로 저장한다.
        """
        repo = self.repo

        if self.has_changes():
            self.add_and_commit(f"backup before restore to {sha[:8]}")

        repo.git.checkout(sha, "--", ".")
        repo.git.add(A=True)

        if repo.is_dirty(index=True, working_tree=False, untracked_files=False):
            repo.index.commit(f"restore to {sha[:8]}")

    def has_changes(self) -> bool:
        """작업 트리에 변경 사항이 있는지 확인한다."""
        repo = self.repo
        return repo.is_dirty(working_tree=True, untracked_files=True)
