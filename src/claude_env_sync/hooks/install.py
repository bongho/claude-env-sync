"""Shell hook 설치/제거 모듈."""

from __future__ import annotations

from pathlib import Path

HOOK_MARKER = "# >>> claude-sync hook >>>"
HOOK_END_MARKER = "# <<< claude-sync hook <<<"

_HOOK_TEMPLATE = """\
{marker}
# Claude Env Sync: 자동 동기화 hook
# claude-sync가 설치되어 있으면 시작 시 자동 pull
if command -v claude-sync &> /dev/null; then
    claude-sync pull --quiet 2>/dev/null || true
fi
{end_marker}
"""


def generate_hook_script() -> str:
    """Shell hook 스크립트를 생성한다."""
    return _HOOK_TEMPLATE.format(
        marker=HOOK_MARKER,
        end_marker=HOOK_END_MARKER,
    )


def install_shell_hook(rc_file: Path) -> None:
    """Shell RC 파일에 claude-sync hook을 설치한다.

    이미 설치되어 있으면 아무것도 하지 않는다 (멱등성).
    """
    if is_hook_installed(rc_file):
        return

    existing = rc_file.read_text() if rc_file.exists() else ""
    hook_script = generate_hook_script()

    with rc_file.open("w") as f:
        f.write(existing)
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write("\n")
        f.write(hook_script)


def uninstall_shell_hook(rc_file: Path) -> None:
    """Shell RC 파일에서 claude-sync hook을 제거한다."""
    if not rc_file.exists():
        return

    content = rc_file.read_text()
    if HOOK_MARKER not in content:
        return

    lines = content.splitlines(keepends=True)
    result: list[str] = []
    skip = False

    for line in lines:
        if HOOK_MARKER in line:
            skip = True
            # 마커 직전 빈 줄도 제거
            while result and result[-1].strip() == "":
                result.pop()
            continue
        if HOOK_END_MARKER in line:
            skip = False
            continue
        if not skip:
            result.append(line)

    rc_file.write_text("".join(result))


def is_hook_installed(rc_file: Path) -> bool:
    """Shell RC 파일에 claude-sync hook이 설치되어 있는지 확인한다."""
    if not rc_file.exists():
        return False
    return HOOK_MARKER in rc_file.read_text()
