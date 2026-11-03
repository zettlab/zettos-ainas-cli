#!/usr/bin/env bash
set -euo pipefail
# Download first: Python reads its program from a file, leaving stdin available.
command -v python3 >/dev/null || { echo 'Python 3.9+ is required. See docs/INSTALL.md.' >&2; exit 1; }
command -v curl >/dev/null || { echo 'curl is required.' >&2; exit 1; }
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
curl --proto '=https' --proto-redir '=https' --tlsv1.2 -fsSL \
  https://raw.githubusercontent.com/zettlab/zettos-ainas-cli/main/scripts/installer.py \
  -o "$tmp/installer.py"
python3 "$tmp/installer.py" "$@"
