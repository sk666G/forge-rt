#!/bin/bash
# forge-rt installer
set -e

REPO="${FORGE_REPO:-https://github.com/sk666G/forge-rt.git}"
DIR="${FORGE_DIR:-$HOME/.forge-src}"

echo
echo "  forge-rt installer"
echo "  ──────────────────"
echo

command -v python3 >/dev/null || { echo "  error: need python3"; exit 1; }

if ! command -v pipx >/dev/null; then
    echo "  installing pipx…"
    sudo apt update -qq && sudo apt install -y pipx
    pipx ensurepath
fi

if [ -d "$DIR/.git" ]; then
    echo "  updating $DIR"
    git -C "$DIR" pull --quiet
else
    echo "  cloning into $DIR"
    git clone --depth 1 "$REPO" "$DIR"
fi

echo "  installing forge…"
pipx install -e "$DIR" --force

echo
echo "  ✓ forge installed"
echo
echo "  next: forge setup"
echo
