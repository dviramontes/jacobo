#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v clj-kondo >/dev/null; then
  echo 'Missing clj-kondo. Install with brew install borkdude/brew/clj-kondo.' >&2
  exit 1
fi

# Directory scans skip .jank files; pass each path explicitly in one invocation
# so definitions and usages across namespaces are analyzed together.
sources=()
while IFS= read -r -d '' source; do
  sources+=("$source")
done < <(find src tests -type f -name '*.jank' -print0)
sources+=(hallo.jank)

exec clj-kondo --lang clj --lint "${sources[@]}"
