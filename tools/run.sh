#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

if command -v python3 &>/dev/null; then
    python3 launcher.py
elif command -v python &>/dev/null; then
    python launcher.py
else
    echo "[ERROR] Python 3 not found."
    exit 1
fi
