#!/usr/bin/env bash
# draft evidence recorder — post_tool_call on terminal.
# Appends a compact JSONL line per terminal command for later injection.
set -euo pipefail
payload="$(cat)"
printf '%s' "$payload" | jq -c '{ts:(now|todateiso8601),cmd:(.tool_input.command // ""),cwd:.cwd}' \
  >> "$HOME/.hermes/agent-hooks/draft-evidence.jsonl" 2>/dev/null || true
echo '{}'
