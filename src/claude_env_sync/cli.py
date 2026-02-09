"""Claude Env Sync CLI."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from claude_env_sync import __version__
from claude_env_sync.core.git_ops import GitOps
from claude_env_sync.core.sync_engine import SyncEngine
from claude_env_sync.hooks.install import (
    install_shell_hook,
    is_hook_installed,
    uninstall_shell_hook,
)

console = Console()

_DEFAULT_CLAUDE_DIR = str(Path.home() / ".claude")
_DEFAULT_SYNC_REPO = str(Path.home() / ".claude-sync-repo")
_DEFAULT_BACKUP_DIR = str(Path.home() / ".claude-sync-backup")


def _common_options(f):
    """공통 옵션 데코레이터."""
    f = click.option(
        "--claude-dir", default=_DEFAULT_CLAUDE_DIR, type=click.Path(),
        help="Claude 설정 디렉토리 경로",
    )(f)
    f = click.option(
        "--sync-repo", default=_DEFAULT_SYNC_REPO, type=click.Path(),
        help="동기화 Git 저장소 경로",
    )(f)
    f = click.option(
        "--backup-dir", default=_DEFAULT_BACKUP_DIR, type=click.Path(),
        help="백업 디렉토리 경로",
    )(f)
    return f


def _make_engine(claude_dir: str, sync_repo: str, backup_dir: str) -> SyncEngine:
    return SyncEngine(
        claude_dir=Path(claude_dir),
        sync_repo_dir=Path(sync_repo),
        backup_dir=Path(backup_dir),
    )


@click.group()
@click.version_option(__version__, prog_name="claude-sync")
def main():
    """Claude Env Sync — Claude Code 설정을 Git으로 동기화합니다."""


@main.command()
@_common_options
@click.option("--remote", default=None, help="원격 Git 저장소 URL")
def init(claude_dir: str, sync_repo: str, backup_dir: str, remote: str | None):
    """동기화 환경을 초기화합니다."""
    engine = _make_engine(claude_dir, sync_repo, backup_dir)
    engine.initialize(remote_url=remote)

    console.print("[green]초기화 완료![/green]")
    console.print(f"  동기화 저장소: {sync_repo}")
    if remote:
        console.print(f"  원격 저장소: {remote}")


@main.command()
@_common_options
@click.option("--message", "-m", default=None, help="커밋 메시지")
def push(claude_dir: str, sync_repo: str, backup_dir: str, message: str | None):
    """현재 Claude 설정을 동기화 저장소로 push합니다."""
    engine = _make_engine(claude_dir, sync_repo, backup_dir)
    engine.initialize()
    result = engine.push(message=message)

    if result.secrets_found:
        console.print("[red]시크릿 감지! Push가 중단되었습니다.[/red]")
        for detail in result.secret_details:
            console.print(f"  [yellow]{detail}[/yellow]")
        return

    if result.committed:
        console.print(f"[green]동기화 완료![/green] {result.files_synced}개 파일")
    else:
        console.print("[dim]변경 사항 없음. 이미 최신 상태입니다.[/dim]")


@main.command()
@_common_options
def pull(claude_dir: str, sync_repo: str, backup_dir: str):
    """동기화 저장소에서 설정을 가져옵니다."""
    engine = _make_engine(claude_dir, sync_repo, backup_dir)
    engine.initialize()
    result = engine.pull()
    console.print(f"[green]복원 완료![/green] {result.files_synced}개 파일")
    console.print(f"  백업 위치: {backup_dir}")


@main.command()
@_common_options
def status(claude_dir: str, sync_repo: str, backup_dir: str):
    """현재 동기화 상태를 조회합니다."""
    engine = _make_engine(claude_dir, sync_repo, backup_dir)
    engine.initialize()
    sync_status = engine.status()

    if sync_status.in_sync:
        console.print("[green]동기화 상태: 최신[/green]")
    else:
        console.print("[yellow]동기화 필요[/yellow]")
        console.print("변경된 파일:")
        for f in sync_status.changed_files:
            console.print(f"  [yellow]M[/yellow] {f}")

    if sync_status.last_sync:
        console.print(f"  마지막 동기화: {sync_status.last_sync}")


@main.command()
@_common_options
@click.option("--limit", "-n", default=10, help="표시할 커밋 수")
def history(claude_dir: str, sync_repo: str, backup_dir: str, limit: int):
    """동기화 변경 이력을 조회합니다."""
    git_ops = GitOps(Path(sync_repo))
    git_ops.init_repo()
    log = git_ops.get_log(limit=limit)

    if not log:
        console.print("[dim]아직 동기화 이력이 없습니다.[/dim]")
        return

    table = Table(title="동기화 이력")
    table.add_column("SHA", style="cyan", width=8)
    table.add_column("메시지", style="white")
    table.add_column("날짜", style="green")
    table.add_column("파일", style="yellow")

    for entry in log:
        table.add_row(
            entry.sha[:8],
            entry.message,
            entry.date.strftime("%Y-%m-%d %H:%M"),
            ", ".join(entry.files_changed[:3])
            + ("..." if len(entry.files_changed) > 3 else ""),
        )

    console.print(table)


@main.command()
@_common_options
@click.argument("ref")
def restore(claude_dir: str, sync_repo: str, backup_dir: str, ref: str):
    """특정 시점으로 설정을 복원합니다."""
    git_ops = GitOps(Path(sync_repo))
    git_ops.init_repo()
    git_ops.restore_to(ref)

    engine = _make_engine(claude_dir, sync_repo, backup_dir)
    engine.initialize()
    engine.pull()

    console.print(f"[green]복원 완료![/green] {ref[:8]} 시점으로 되돌렸습니다.")


@main.group()
def hook():
    """자동 동기화 hook을 관리합니다."""


@hook.command("install")
@click.option(
    "--shell", type=click.Choice(["bash", "zsh", "auto"]),
    default="auto", help="Shell 종류",
)
def hook_install(shell: str):
    """Shell RC 파일에 자동 동기화 hook을 설치합니다."""
    rc_files = _resolve_rc_files(shell)
    for rc_file in rc_files:
        if is_hook_installed(rc_file):
            console.print(f"[dim]이미 설치됨: {rc_file}[/dim]")
        else:
            install_shell_hook(rc_file)
            console.print(f"[green]Hook 설치 완료: {rc_file}[/green]")


@hook.command("uninstall")
@click.option(
    "--shell", type=click.Choice(["bash", "zsh", "auto"]),
    default="auto", help="Shell 종류",
)
def hook_uninstall(shell: str):
    """Shell RC 파일에서 자동 동기화 hook을 제거합니다."""
    rc_files = _resolve_rc_files(shell)
    for rc_file in rc_files:
        if is_hook_installed(rc_file):
            uninstall_shell_hook(rc_file)
            console.print(f"[green]Hook 제거 완료: {rc_file}[/green]")
        else:
            console.print(f"[dim]설치되지 않음: {rc_file}[/dim]")


def _resolve_rc_files(shell: str) -> list[Path]:
    """Shell 종류에 따라 RC 파일 경로를 반환한다."""
    home = Path.home()
    if shell == "bash":
        return [home / ".bashrc"]
    elif shell == "zsh":
        return [home / ".zshrc"]
    else:
        candidates = []
        for name in [".zshrc", ".bashrc"]:
            rc = home / name
            if rc.exists():
                candidates.append(rc)
        return candidates if candidates else [home / ".bashrc"]


if __name__ == "__main__":  # pragma: no cover
    main()
