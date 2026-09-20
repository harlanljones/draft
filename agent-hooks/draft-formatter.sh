#!/usr/bin/env bash
# draft formatter — post_tool_call on write_file|patch.
# Formats edited Python files with ruff. Guarded no-op until the repo's
# .venv provides ruff.
set -euo pipefail
payload="$(cat)"
file="$(printf '%s' "$payload" | jq -r '.tool_input.path // .tool_input.file_path // empty')"
[ -z "$file" ] || [ ! -f "$file" ] && { echo '{}'; exit 0; }

case "$file" in
  *.py) ;;
  *) echo '{}'; exit 0 ;;
esac

# Find the repo root upward from the file (marker: pyproject.toml + .venv).
d="$(dirname "$file")"
app=""
while [ "$d" != "/" ]; do
  [ -f "$d/pyproject.toml" ] && [ -d "$d/.venv" ] && { app="$d"; break; }
  d="$(dirname "$d")"
done
[ -z "$app" ] && { echo '{}'; exit 0; }

if [ -x "$app/.venv/bin/ruff" ]; then
  (cd "$app" && .venv/bin/ruff format --quiet "$file" >/dev/null 2>&1) || true
  (cd "$app" && .venv/bin/ruff check --fix --quiet "$file" >/dev/null 2>&1) || true
fi
echo '{}'
