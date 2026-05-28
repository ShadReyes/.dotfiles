#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$DOTFILES/scripts/agentize-repo"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  ✓ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ✗ $1"; }

assert_file() { [ -f "$1" ] && pass "$2" || fail "$2"; }
assert_dir() { [ -d "$1" ] && [ ! -L "$1" ] && pass "$2" || fail "$2"; }
assert_link() { [ -L "$1" ] && pass "$2" || fail "$2"; }
assert_missing() { [ ! -e "$1" ] && [ ! -L "$1" ] && pass "$2" || fail "$2"; }
assert_contains() { grep -q "$2" "$1" 2>/dev/null && pass "$3" || fail "$3"; }
assert_target() {
  local target
  if command -v readlink >/dev/null 2>&1; then
    target="$(readlink "$1")"
  else
    target="$(stat -f '%Y' "$1")"
  fi
  [ "$target" = "$2" ] && pass "$3" || fail "$3: expected $2, got $target"
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "Claude-first repo"
repo="$tmp/claude-first"
mkdir -p "$repo/.claude/skills/devcontainer" "$repo/.claude/agents/reviewer"
printf '# CLAUDE.md\n\nRepo guidance\n' > "$repo/CLAUDE.md"
printf 'skill\n' > "$repo/.claude/skills/devcontainer/SKILL.md"
printf 'agent\n' > "$repo/.claude/agents/reviewer/README.md"

"$SCRIPT" "$repo" > /dev/null

assert_file "$repo/AGENTS.md" "AGENTS.md created"
assert_contains "$repo/AGENTS.md" "Repo guidance" "AGENTS.md preserves content"
assert_link "$repo/CLAUDE.md" "CLAUDE.md compatibility symlink"
assert_target "$repo/CLAUDE.md" "AGENTS.md" "CLAUDE.md points at AGENTS.md"
assert_dir "$repo/.agents/skills" ".agents/skills is canonical directory"
assert_file "$repo/.agents/skills/devcontainer/SKILL.md" "skill moved to .agents"
assert_link "$repo/.claude/skills" ".claude/skills compatibility symlink"
assert_target "$repo/.claude/skills" "../.agents/skills" ".claude/skills points at .agents/skills"
assert_dir "$repo/.agents/agents" ".agents/agents is canonical directory"
assert_link "$repo/.claude/agents" ".claude/agents compatibility symlink"

echo ""
echo "Idempotency"
"$SCRIPT" "$repo" > /dev/null
assert_file "$repo/AGENTS.md" "re-run keeps AGENTS.md"
assert_link "$repo/CLAUDE.md" "re-run keeps CLAUDE.md symlink"
assert_link "$repo/.claude/skills" "re-run keeps skills symlink"

echo ""
echo "Legacy nested Claude doc"
legacy="$tmp/legacy"
mkdir -p "$legacy/.claude/skills/rails" "$legacy/.agents"
printf '# Legacy\n' > "$legacy/.claude/CLAUDE.md"
ln -s .claude/CLAUDE.md "$legacy/AGENTS.md"
ln -s ../.claude/skills "$legacy/.agents/skills"
printf 'rails\n' > "$legacy/.claude/skills/rails/SKILL.md"

"$SCRIPT" "$legacy" > /dev/null

assert_file "$legacy/AGENTS.md" "legacy AGENTS.md became real file"
assert_contains "$legacy/AGENTS.md" "Legacy" "legacy content preserved"
assert_link "$legacy/.claude/CLAUDE.md" "nested CLAUDE.md compatibility symlink"
assert_target "$legacy/.claude/CLAUDE.md" "../AGENTS.md" "nested CLAUDE.md points at AGENTS.md"
assert_dir "$legacy/.agents/skills" "legacy .agents/skills became canonical directory"
assert_file "$legacy/.agents/skills/rails/SKILL.md" "legacy skill moved to .agents"
assert_link "$legacy/.claude/skills" "legacy .claude/skills compatibility symlink"

echo ""
echo "Conflict handling"
conflict_repo="$tmp/conflict"
mkdir -p "$conflict_repo"
printf 'agents\n' > "$conflict_repo/AGENTS.md"
printf 'claude\n' > "$conflict_repo/CLAUDE.md"

if "$SCRIPT" "$conflict_repo" > "$tmp/conflict.out" 2> "$tmp/conflict.err"; then
  fail "conflicting docs return non-zero"
else
  pass "conflicting docs return non-zero"
fi
assert_file "$conflict_repo/AGENTS.md" "conflict keeps AGENTS.md"
assert_file "$conflict_repo/CLAUDE.md" "conflict keeps CLAUDE.md"
assert_contains "$tmp/conflict.err" "different CLAUDE.md" "conflict explains mismatch"

echo ""
echo "Recursive mode"
root="$tmp/workspace"
mkdir -p "$root/a" "$root/b/.claude/skills/demo" "$root/node_modules/ignored"
printf 'A\n' > "$root/a/CLAUDE.md"
printf 'B\n' > "$root/b/CLAUDE.md"
printf 'ignored\n' > "$root/node_modules/ignored/CLAUDE.md"
printf 'demo\n' > "$root/b/.claude/skills/demo/SKILL.md"

"$SCRIPT" --recursive "$root" > /dev/null

assert_file "$root/a/AGENTS.md" "recursive creates a/AGENTS.md"
assert_link "$root/a/CLAUDE.md" "recursive links a/CLAUDE.md"
assert_file "$root/b/AGENTS.md" "recursive creates b/AGENTS.md"
assert_file "$root/b/.agents/skills/demo/SKILL.md" "recursive migrates b skills"
assert_missing "$root/node_modules/ignored/AGENTS.md" "recursive skips node_modules"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  $PASS passed, $FAIL failed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

[ "$FAIL" -eq 0 ] || exit 1
