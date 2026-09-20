#!/usr/bin/env bash
# draft pre_llm_call injector — injects git status when inside harlanljones/draft.
set -euo pipefail
payload="$(cat)"
cwd="$(printf '%s' "$payload" | jq -r '.cwd // empty')"
[ -z "$cwd" ] && { echo '{}'; exit 0; }

inside=""
d="$cwd"
while [ "$d" != "/" ]; do
  [ -d "$d/.git" ] && git -C "$d" rev-parse --abbrev-ref HEAD >/dev/null 2>&1 && \
    [ "$(git -C "$d" remote get-url origin 2>/dev/null | grep -c 'harlanljones/draft' || true)" -ge 1 ] && { inside="$d"; break; }
  d="$(dirname "$d")"
done
[ -z "$inside" ] && { echo '{}'; exit 0; }

branch="$(git -C "$inside" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
status="$(git -C "$inside" status --porcelain 2>/dev/null | head -20)"
out="repo: $inside | branch: $branch"
[ -n "$status" ] && out="$out
dirty files:
$status" || out="$out | working tree clean"
jq -n --arg c "$out" '{context:$c}'
