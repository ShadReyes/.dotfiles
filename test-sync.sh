#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  ✓ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ✗ $1"; }
assert_link() { [ -L "$1" ] && pass "$2" || fail "$2: not a symlink"; }
assert_file() { [ -f "$1" ] && pass "$2" || fail "$2: not found"; }
assert_contains() { grep -q "$2" "$1" 2>/dev/null && pass "$3" || fail "$3"; }
assert_count() {
  local actual
  actual=$(find "$1" -mindepth 1 -maxdepth 1 -name "$2" | wc -l | tr -d ' ')
  [ "$actual" -eq "$3" ] && pass "$4 ($actual)" || fail "$4: expected $3, got $actual"
}

# --- Setup: run sync in a temp HOME to avoid touching real config ---
TEMP_HOME="$(mktemp -d)"
trap 'rm -rf "$TEMP_HOME"' EXIT

mkdir -p "$TEMP_HOME/.claude" "$TEMP_HOME/.codex" "$TEMP_HOME/.agents"
HOME="$TEMP_HOME" "$DOTFILES/sync-skills.sh" > /dev/null

echo "Skills"
assert_count "$TEMP_HOME/.claude/skills" '*' 22 "22 skills synced to Claude"
assert_count "$TEMP_HOME/.agents/skills" '*' 22 "22 skills synced to Codex"

for skill in agent-config bug-to-plan code-search grilling manage-skills solving-linear-issues rust-best-practices patchtree present-plan present-issue; do
  assert_link "$TEMP_HOME/.claude/skills/$skill" "Claude skill: $skill is symlink"
  assert_link "$TEMP_HOME/.agents/skills/$skill" "Codex skill: $skill is symlink"
  assert_file "$TEMP_HOME/.claude/skills/$skill/SKILL.md" "Claude skill: $skill/SKILL.md readable"
  assert_file "$TEMP_HOME/.agents/skills/$skill/SKILL.md" "Codex skill: $skill/SKILL.md readable"
  assert_file "$TEMP_HOME/.agents/skills/$skill/agents/openai.yaml" "Codex skill: $skill has UI metadata"
done

for plugin in brando matt fluid; do
  assert_link "$TEMP_HOME/.claude/skills/$plugin" "Claude plugin: $plugin is symlink"
  assert_link "$TEMP_HOME/.agents/skills/$plugin" "Codex plugin: $plugin is symlink"
  assert_file "$TEMP_HOME/.agents/skills/$plugin/.claude-plugin/plugin.json" "Plugin: $plugin has manifest"
done

for skill in react-doctor typescript-doctor turborepo prd-to-plan improve-codebase-architecture validate-startup-idea find-skills; do
  assert_file "$TEMP_HOME/.agents/skills/brando/skills/$skill/SKILL.md" "brando:$skill readable"
done

for skill in writing-great-skills grill-me teach tdd to-prd grill-with-docs; do
  assert_file "$TEMP_HOME/.agents/skills/matt/skills/$skill/SKILL.md" "matt:$skill readable"
done

for doc in MISSION-FORMAT.md RESOURCES-FORMAT.md LEARNING-RECORD-FORMAT.md GLOSSARY-FORMAT.md; do
  assert_file "$TEMP_HOME/.agents/skills/matt/skills/teach/$doc" "Codex skill: matt:teach includes $doc"
done

echo ""
echo "Agents"
assert_count "$TEMP_HOME/.codex/agents" '*.toml' 2 "2 TOML agents synced to Codex"
assert_count "$TEMP_HOME/.claude/agents" '*.md' 2 "2 markdown agents generated for Claude"

for agent in bottom-sheet-specialist remote-dom-specialist; do
  assert_link "$TEMP_HOME/.codex/agents/$agent.toml" "Codex agent: $agent.toml is symlink"
  assert_file "$TEMP_HOME/.claude/agents/$agent.md" "Claude agent: $agent.md exists"

  # Verify generated markdown has correct YAML frontmatter
  assert_contains "$TEMP_HOME/.claude/agents/$agent.md" "^---" "Claude agent $agent: has frontmatter"
  assert_contains "$TEMP_HOME/.claude/agents/$agent.md" "^name: $agent" "Claude agent $agent: name matches"
  assert_contains "$TEMP_HOME/.claude/agents/$agent.md" "^model:" "Claude agent $agent: has model"
  assert_contains "$TEMP_HOME/.claude/agents/$agent.md" "^color:" "Claude agent $agent: has color"

  # Verify content survived conversion (spot check)
  assert_contains "$TEMP_HOME/.claude/agents/$agent.md" "## " "Claude agent $agent: has markdown headings"
done

echo ""
echo "Commands"
assert_count "$TEMP_HOME/.claude/commands" '*' 1 "1 command synced to Claude"
assert_link "$TEMP_HOME/.claude/commands/update-status.md" "Claude command: update-status.md is symlink"

echo ""
echo "TOML→Claude conversion"
# Verify the converter preserves developer_instructions content
bs_lines=$(wc -l < "$TEMP_HOME/.claude/agents/bottom-sheet-specialist.md" | tr -d ' ')
[ "$bs_lines" -gt 50 ] && pass "bottom-sheet-specialist.md has $bs_lines lines (content preserved)" \
                        || fail "bottom-sheet-specialist.md only has $bs_lines lines (content may be truncated)"

rd_lines=$(wc -l < "$TEMP_HOME/.claude/agents/remote-dom-specialist.md" | tr -d ' ')
[ "$rd_lines" -gt 100 ] && pass "remote-dom-specialist.md has $rd_lines lines (content preserved)" \
                         || fail "remote-dom-specialist.md only has $rd_lines lines (content may be truncated)"

echo ""
echo "Idempotency"
HOME="$TEMP_HOME" "$DOTFILES/sync-skills.sh" > /dev/null
assert_count "$TEMP_HOME/.claude/skills" '*' 22 "Re-run: still 22 skills"
assert_count "$TEMP_HOME/.agents/skills" '*' 22 "Re-run: still 22 Codex skills"
assert_count "$TEMP_HOME/.claude/agents" '*.md' 2 "Re-run: still 2 agents"
pass "sync-skills.sh is idempotent"

echo ""
echo "Symlink targets"
# Verify symlinks point back to the .dotfiles repo, not somewhere else
target=$(readlink "$TEMP_HOME/.claude/skills/matt")
[[ "$target" == "$DOTFILES/skills/matt/" ]] && pass "Skill plugin symlink points to .dotfiles repo" \
                                                 || fail "Skill symlink points to: $target"

target=$(readlink "$TEMP_HOME/.codex/agents/bottom-sheet-specialist.toml")
[[ "$target" == "$DOTFILES/agents/bottom-sheet-specialist.toml" ]] && pass "Agent symlink points to .dotfiles repo" \
                                                                    || fail "Agent symlink points to: $target"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  $PASS passed, $FAIL failed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

[ "$FAIL" -eq 0 ] || exit 1
