#!/usr/bin/env bash
#
# claude-env-sync 설치 스크립트
# 사용법: curl -sSL https://raw.githubusercontent.com/bono/claude-env-sync/main/scripts/install.sh | bash
#

set -euo pipefail

REPO="bono/claude-env-sync"
PACKAGE="claude-env-sync"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Python 3.9+ 확인
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON=python3
    elif command -v python &> /dev/null; then
        PYTHON=python
    else
        error "Python이 설치되어 있지 않습니다. Python 3.9 이상을 설치해주세요."
    fi

    version=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    major=$($PYTHON -c "import sys; print(sys.version_info.major)")
    minor=$($PYTHON -c "import sys; print(sys.version_info.minor)")

    if [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -lt 9 ]; }; then
        error "Python $version 감지. Python 3.9 이상이 필요합니다."
    fi

    info "Python $version 감지"
}

# pipx 또는 pip 설치
install_package() {
    if command -v pipx &> /dev/null; then
        info "pipx로 설치합니다..."
        pipx install "$PACKAGE" || pipx install "git+https://github.com/${REPO}.git"
    elif command -v pip3 &> /dev/null; then
        warn "pipx를 찾을 수 없어 pip3로 설치합니다. pipx 사용을 권장합니다."
        pip3 install --user "$PACKAGE" || pip3 install --user "git+https://github.com/${REPO}.git"
    elif command -v pip &> /dev/null; then
        warn "pipx를 찾을 수 없어 pip로 설치합니다."
        pip install --user "$PACKAGE" || pip install --user "git+https://github.com/${REPO}.git"
    else
        error "pip 또는 pipx를 찾을 수 없습니다."
    fi
}

# 설치 확인
verify_install() {
    if command -v claude-sync &> /dev/null; then
        version=$(claude-sync --version 2>&1)
        info "설치 완료! $version"
    else
        warn "claude-sync 명령을 찾을 수 없습니다."
        warn "PATH에 ~/.local/bin 이 포함되어 있는지 확인해주세요:"
        warn "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
}

main() {
    echo ""
    echo "╔══════════════════════════════════════╗"
    echo "║     Claude Env Sync 설치 스크립트      ║"
    echo "╚══════════════════════════════════════╝"
    echo ""

    check_python
    install_package
    verify_install

    echo ""
    info "시작하려면:"
    info "  claude-sync init --remote <your-git-repo-url>"
    info "  claude-sync push"
    echo ""
}

main
