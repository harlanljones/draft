#!/usr/bin/env bash
# draft git-guard — pre_tool_call on terminal|execute_code, fail_closed.
# Blocks mutating git commands; read-only git (status/diff/log/show/branch) passes.
set -euo pipefail
payload="$(cat)"
cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty')"
[ -z "$cmd" ] && { echo '{}'; exit 0; }

if printf '%s' "$cmd" | grep -qE '^\s*git(\s|$)' && \
   printf '%s' "$cmd" | grep -qE '\b(push|pull|fetch|commit|merge|rebase|reset|clean|checkout|switch|restore|tag|cherry-pick|revert|am|apply|stash|rm|mv|remote|branch( -D|-d| --delete)|worktree|submodule|filter-branch|gc|prune)\b'; then
  echo '{"action":"block","message":"git-guard: mutating git command blocked. Run it yourself or ask the user to approve."}' >&2
  exit 2
fi
echo '{}'
