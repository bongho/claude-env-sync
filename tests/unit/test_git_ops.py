"""git_ops 모듈 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from claude_env_sync.core.git_ops import GitOps


@pytest.fixture
def git_dir(tmp_path: Path) -> Path:
    """임시 Git 저장소 경로를 제공한다."""
    repo_dir = tmp_path / "sync-repo"
    repo_dir.mkdir()
    return repo_dir


@pytest.fixture
def git_ops(git_dir: Path) -> GitOps:
    """초기화된 GitOps 인스턴스를 제공한다."""
    ops = GitOps(git_dir)
    ops.init_repo()
    return ops


class TestGitOpsInit:
    """Git 저장소 초기화 테스트."""

    def test_init_creates_git_dir(self, git_dir: Path):
        ops = GitOps(git_dir)
        ops.init_repo()
        assert (git_dir / ".git").is_dir()

    def test_init_returns_true(self, git_dir: Path):
        ops = GitOps(git_dir)
        result = ops.init_repo()
        assert result is True

    def test_init_idempotent(self, git_ops: GitOps, git_dir: Path):
        """이미 초기화된 저장소에서 다시 호출해도 에러 없어야 한다."""
        result = git_ops.init_repo()
        assert result is True
        assert (git_dir / ".git").is_dir()

    def test_is_initialized(self, git_ops: GitOps):
        assert git_ops.is_initialized() is True

    def test_not_initialized(self, git_dir: Path):
        ops = GitOps(git_dir)
        assert ops.is_initialized() is False


class TestGitOpsCommit:
    """Git commit 테스트."""

    def test_commit_files(self, git_ops: GitOps, git_dir: Path):
        """파일을 추가하고 커밋할 수 있어야 한다."""
        test_file = git_dir / "test.txt"
        test_file.write_text("hello")
        git_ops.add_and_commit("test commit")
        log = git_ops.get_log(limit=1)
        assert len(log) == 1
        assert "test commit" in log[0].message

    def test_commit_with_auto_message(self, git_ops: GitOps, git_dir: Path):
        """자동 메시지로 커밋할 수 있어야 한다."""
        test_file = git_dir / "test.txt"
        test_file.write_text("hello")
        git_ops.add_and_commit()
        log = git_ops.get_log(limit=1)
        assert len(log) == 1
        assert "claude-sync" in log[0].message.lower()

    def test_no_commit_when_nothing_changed(self, git_ops: GitOps, git_dir: Path):
        """변경 사항이 없으면 커밋하지 않아야 한다."""
        result = git_ops.add_and_commit("empty commit")
        assert result is False

    def test_multiple_commits(self, git_ops: GitOps, git_dir: Path):
        """여러 번 커밋할 수 있어야 한다."""
        (git_dir / "a.txt").write_text("a")
        git_ops.add_and_commit("first")
        (git_dir / "b.txt").write_text("b")
        git_ops.add_and_commit("second")
        log = git_ops.get_log(limit=10)
        assert len(log) == 2


class TestGitOpsLog:
    """Git log 테스트."""

    def test_log_empty_repo(self, git_ops: GitOps):
        """커밋이 없는 저장소에서도 빈 목록을 반환해야 한다."""
        log = git_ops.get_log()
        assert log == []

    def test_log_entry_has_fields(self, git_ops: GitOps, git_dir: Path):
        """로그 항목에 sha, message, date, files_changed가 있어야 한다."""
        (git_dir / "test.txt").write_text("data")
        git_ops.add_and_commit("test entry")
        log = git_ops.get_log(limit=1)
        entry = log[0]
        assert entry.sha is not None
        assert entry.message is not None
        assert entry.date is not None
        assert isinstance(entry.files_changed, list)

    def test_log_limit(self, git_ops: GitOps, git_dir: Path):
        """limit 파라미터가 동작해야 한다."""
        for i in range(5):
            (git_dir / f"file{i}.txt").write_text(f"content{i}")
            git_ops.add_and_commit(f"commit {i}")
        log = git_ops.get_log(limit=3)
        assert len(log) == 3

    def test_log_order_newest_first(self, git_ops: GitOps, git_dir: Path):
        """최신 커밋이 먼저 나와야 한다."""
        (git_dir / "first.txt").write_text("1")
        git_ops.add_and_commit("first commit")
        (git_dir / "second.txt").write_text("2")
        git_ops.add_and_commit("second commit")
        log = git_ops.get_log()
        assert "second" in log[0].message
        assert "first" in log[1].message


class TestGitOpsRemote:
    """원격 저장소 설정 테스트."""

    def test_add_remote(self, git_ops: GitOps):
        git_ops.add_remote("https://github.com/test/repo.git")
        assert git_ops.has_remote() is True

    def test_no_remote_initially(self, git_ops: GitOps):
        assert git_ops.has_remote() is False

    def test_get_remote_url(self, git_ops: GitOps):
        url = "https://github.com/test/repo.git"
        git_ops.add_remote(url)
        assert git_ops.get_remote_url() == url


class TestGitOpsRestore:
    """이전 상태 복원 테스트."""

    def test_restore_to_commit(self, git_ops: GitOps, git_dir: Path):
        """특정 커밋 시점으로 복원할 수 있어야 한다."""
        (git_dir / "test.txt").write_text("version1")
        git_ops.add_and_commit("v1")
        log_v1 = git_ops.get_log(limit=1)
        sha_v1 = log_v1[0].sha

        (git_dir / "test.txt").write_text("version2")
        git_ops.add_and_commit("v2")

        git_ops.restore_to(sha_v1)
        assert (git_dir / "test.txt").read_text() == "version1"

    def test_restore_creates_backup_commit(self, git_ops: GitOps, git_dir: Path):
        """복원 전 현재 상태를 백업 커밋으로 저장해야 한다."""
        (git_dir / "test.txt").write_text("v1")
        git_ops.add_and_commit("v1")
        sha_v1 = git_ops.get_log(limit=1)[0].sha

        (git_dir / "test.txt").write_text("v2")
        git_ops.add_and_commit("v2")

        git_ops.restore_to(sha_v1)
        log = git_ops.get_log()
        assert any(
            "restore" in entry.message.lower()
            or "backup" in entry.message.lower()
            for entry in log
        )


class TestGitOpsDiff:
    """변경 사항 비교 테스트."""

    def test_has_changes_true(self, git_ops: GitOps, git_dir: Path):
        """변경 사항이 있으면 True를 반환해야 한다."""
        (git_dir / "test.txt").write_text("v1")
        git_ops.add_and_commit("initial")
        (git_dir / "test.txt").write_text("v2")
        assert git_ops.has_changes() is True

    def test_has_changes_false(self, git_ops: GitOps, git_dir: Path):
        """변경 사항이 없으면 False를 반환해야 한다."""
        (git_dir / "test.txt").write_text("v1")
        git_ops.add_and_commit("initial")
        assert git_ops.has_changes() is False

    def test_has_changes_untracked(self, git_ops: GitOps, git_dir: Path):
        """추적되지 않는 새 파일도 변경으로 감지해야 한다."""
        (git_dir / "initial.txt").write_text("init")
        git_ops.add_and_commit("initial")
        (git_dir / "new_file.txt").write_text("new")
        assert git_ops.has_changes() is True


class TestGitOpsRepoProperty:
    """repo 프로퍼티 접근 테스트."""

    def test_repo_raises_when_not_initialized(self, git_dir: Path):
        """초기화 없이 repo에 접근하면 GitOpsError가 발생해야 한다."""
        from claude_env_sync.core.git_ops import GitOpsError

        ops = GitOps(git_dir)
        with pytest.raises(GitOpsError, match="초기화"):
            _ = ops.repo


class TestGitOpsRemoteAdvanced:
    """원격 저장소 고급 테스트."""

    def test_add_remote_replaces_existing(self, git_ops: GitOps):
        """기존 remote를 교체할 수 있어야 한다."""
        git_ops.add_remote("https://github.com/test/old.git")
        git_ops.add_remote("https://github.com/test/new.git")
        assert git_ops.get_remote_url() == "https://github.com/test/new.git"

    def test_get_remote_url_returns_none(self, git_ops: GitOps):
        """remote가 없으면 None을 반환해야 한다."""
        assert git_ops.get_remote_url() is None


class TestGitOpsPushPull:
    """push/pull 예외 처리 테스트."""

    def test_push_raises_on_no_remote(self, git_ops: GitOps, git_dir: Path):
        """remote 없이 push하면 GitOpsError가 발생해야 한다."""
        from claude_env_sync.core.git_ops import GitOpsError

        (git_dir / "test.txt").write_text("data")
        git_ops.add_and_commit("initial")
        with pytest.raises(GitOpsError, match="Push 실패"):
            git_ops.push()

    def test_pull_raises_on_no_remote(self, git_ops: GitOps, git_dir: Path):
        """remote 없이 pull하면 GitOpsError가 발생해야 한다."""
        from claude_env_sync.core.git_ops import GitOpsError

        (git_dir / "test.txt").write_text("data")
        git_ops.add_and_commit("initial")
        with pytest.raises(GitOpsError, match="Pull 실패"):
            git_ops.pull()

    def test_push_success_with_local_remote(self, tmp_path: Path):
        """로컬 bare repo를 remote로 설정하면 push가 성공해야 한다."""
        from git import Repo as GitRepo

        bare_dir = tmp_path / "bare.git"
        GitRepo.init(bare_dir, bare=True)

        repo_dir = tmp_path / "work"
        repo_dir.mkdir()
        ops = GitOps(repo_dir)
        ops.init_repo()

        (repo_dir / "test.txt").write_text("data")
        ops.add_and_commit("initial")

        # main 브랜치 이름 설정
        ops.repo.git.branch("-M", "main")
        ops.add_remote(str(bare_dir))
        result = ops.push()
        assert result is True

    def test_pull_success_with_local_remote(self, tmp_path: Path):
        """로컬 bare repo에서 pull이 성공해야 한다."""
        from git import Repo as GitRepo

        bare_dir = tmp_path / "bare.git"
        GitRepo.init(bare_dir, bare=True)

        # 첫 번째 repo에서 push
        repo1_dir = tmp_path / "repo1"
        repo1_dir.mkdir()
        ops1 = GitOps(repo1_dir)
        ops1.init_repo()
        (repo1_dir / "test.txt").write_text("v1")
        ops1.add_and_commit("initial")
        ops1.repo.git.branch("-M", "main")
        ops1.add_remote(str(bare_dir))
        ops1.push()

        # 두 번째 repo에서 clone 후 pull
        repo2_dir = tmp_path / "repo2"
        GitRepo.clone_from(str(bare_dir), str(repo2_dir))
        ops2 = GitOps(repo2_dir)
        ops2.init_repo()

        # repo1에서 새 커밋 push
        (repo1_dir / "test.txt").write_text("v2")
        ops1.add_and_commit("update")
        ops1.push()

        result = ops2.pull()
        assert result is True
        assert (repo2_dir / "test.txt").read_text() == "v2"


class TestGitOpsRestoreWithChanges:
    """변경 사항이 있는 상태에서 restore 테스트."""

    def test_restore_with_pending_changes(self, git_ops: GitOps, git_dir: Path):
        """미커밋 변경이 있는 상태에서 restore하면 백업 커밋을 생성해야 한다."""
        (git_dir / "test.txt").write_text("v1")
        git_ops.add_and_commit("v1")
        sha_v1 = git_ops.get_log(limit=1)[0].sha

        (git_dir / "test.txt").write_text("v2")
        git_ops.add_and_commit("v2")

        # 미커밋 변경 생성
        (git_dir / "test.txt").write_text("v3-uncommitted")
        git_ops.restore_to(sha_v1)

        log = git_ops.get_log()
        assert any("backup" in e.message.lower() for e in log)
        assert (git_dir / "test.txt").read_text() == "v1"
