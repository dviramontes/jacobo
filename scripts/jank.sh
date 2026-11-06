#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v jank >/dev/null; then
  echo 'Missing jank. See https://book.jank-lang.org/installation.html' >&2
  exit 1
fi

# A prefix override supports non-Homebrew installations without hardcoded paths.
raylib_prefix="${RAYLIB_PREFIX:-}"
if [[ -z "$raylib_prefix" ]] && command -v brew >/dev/null; then
  raylib_prefix="$(brew --prefix raylib 2>/dev/null || true)"
fi
if [[ -z "$raylib_prefix" || ! -f "$raylib_prefix/include/raylib.h" ]]; then
  echo 'Missing raylib. Install with brew install raylib, or set RAYLIB_PREFIX.' >&2
  exit 1
fi

exec jank --module-path src \
  -I "$raylib_prefix/include" -L "$raylib_prefix/lib" -l raylib "$@"
