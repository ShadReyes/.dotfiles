#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  ✓ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ✗ $1"; }
assert_link() { [ -L "$1" ] && pass "$2" || fail "$2: not a symlink"; }
assert_file() { [ -f "$1" ] && pass "$2" || fail "$2: not found"; }
assert_executable() { [ -x "$1" ] && pass "$2" || fail "$2: not executable"; }
assert_contains() { grep -q "$2" "$1" 2>/dev/null && pass "$3" || fail "$3"; }
assert_count() {
  local actual
  actual=$(find "$1" -mindepth 1 -maxdepth 1 -name "$2" | wc -l | tr -d ' ')
  [ "$actual" -eq "$3" ] && pass "$4 ($actual)" || fail "$4: expected $3, got $actual"
}
assert_unique_skill_names() {
  local output

  if output=$(python3 - "$DOTFILES/skills" <<'PY'
from collections import defaultdict
from pathlib import Path
import re
import sys

skills_dir = Path(sys.argv[1])
locations = defaultdict(list)

for skill_file in sorted(skills_dir.rglob("SKILL.md")):
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        continue

    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.fullmatch(r"name:\s*['\"]?([a-z0-9-]+)['\"]?\s*", line)
        if match:
            locations[match.group(1)].append(skill_file.relative_to(skills_dir))
            break

duplicates = {name: paths for name, paths in locations.items() if len(paths) > 1}
if duplicates:
    for name, paths in sorted(duplicates.items()):
        print(f'duplicate skill name "{name}":')
        for path in paths:
            print(f"  skills/{path}")
    raise SystemExit(1)
PY
  ); then
    pass "skill frontmatter names are globally unique"
  else
    fail "skill frontmatter names must be globally unique"
    printf '%s\n' "$output" | sed 's/^/    /'
  fi
}

# --- Setup: run sync in a temp HOME to avoid touching real config ---
TEMP_HOME="$(mktemp -d)"
trap 'rm -rf "$TEMP_HOME"' EXIT
EXPECTED_SKILL_COUNT=$(find "$DOTFILES/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')

mkdir -p "$TEMP_HOME/.claude" "$TEMP_HOME/.codex" "$TEMP_HOME/.agents"
HOME="$TEMP_HOME" "$DOTFILES/sync-skills.sh" > /dev/null

echo "Skills"
assert_unique_skill_names
assert_count "$TEMP_HOME/.claude/skills" '*' "$EXPECTED_SKILL_COUNT" "$EXPECTED_SKILL_COUNT skills synced to Claude"
assert_count "$TEMP_HOME/.agents/skills" '*' "$EXPECTED_SKILL_COUNT" "$EXPECTED_SKILL_COUNT skills synced to Codex"

assert_link "$TEMP_HOME/.claude/skills/orchestrator" "Claude skill: orchestrator is symlink"
assert_link "$TEMP_HOME/.agents/skills/orchestrator" "Codex skill: orchestrator is symlink"
assert_file "$TEMP_HOME/.claude/skills/orchestrator/SKILL.md" "Claude skill: orchestrator/SKILL.md readable"
assert_file "$TEMP_HOME/.agents/skills/orchestrator/SKILL.md" "Codex skill: orchestrator/SKILL.md readable"
assert_file "$TEMP_HOME/.agents/skills/orchestrator/agents/openai.yaml" "Codex skill: orchestrator has UI metadata"
assert_file "$TEMP_HOME/.agents/skills/write-ste100/SKILL.md" "Codex skill: write-ste100/SKILL.md readable"
assert_file "$TEMP_HOME/.agents/skills/write-ste100/agents/openai.yaml" "Codex skill: write-ste100 has UI metadata"
assert_file "$TEMP_HOME/.agents/skills/write-ste100/references/glossary-schema.md" "Codex skill: write-ste100 glossary schema readable"
assert_file "$TEMP_HOME/.agents/skills/write-ste100/scripts/ste100.lock" "Codex skill: write-ste100 script lock readable"
assert_executable "$TEMP_HOME/.agents/skills/write-ste100/scripts/ste100" "Codex skill: write-ste100 CLI is executable"

for skill in agent-config bug-to-plan grilling solving-linear-issues rust-best-practices patchtree present-plan present-issue; do
  assert_link "$TEMP_HOME/.claude/skills/$skill" "Claude skill: $skill is symlink"
  assert_link "$TEMP_HOME/.agents/skills/$skill" "Codex skill: $skill is symlink"
  assert_file "$TEMP_HOME/.claude/skills/$skill/SKILL.md" "Claude skill: $skill/SKILL.md readable"
  assert_file "$TEMP_HOME/.agents/skills/$skill/SKILL.md" "Codex skill: $skill/SKILL.md readable"
  assert_file "$TEMP_HOME/.agents/skills/$skill/agents/openai.yaml" "Codex skill: $skill has UI metadata"
done

for plugin in blowmage brando matt fluid herdr dotfiles vercel; do
  assert_link "$TEMP_HOME/.claude/skills/$plugin" "Claude plugin: $plugin is symlink"
  assert_link "$TEMP_HOME/.agents/skills/$plugin" "Codex plugin: $plugin is symlink"
  assert_file "$TEMP_HOME/.agents/skills/$plugin/.claude-plugin/plugin.json" "Plugin: $plugin has manifest"
done

assert_file "$TEMP_HOME/.agents/skills/herdr/skills/herdr/SKILL.md" "herdr:herdr readable"
assert_file "$TEMP_HOME/.agents/skills/dotfiles/skills/manage-skills/SKILL.md" "dotfiles:manage-skills readable"
assert_file "$TEMP_HOME/.agents/skills/fluid/skills/posthog/SKILL.md" "fluid:posthog readable"
assert_file "$TEMP_HOME/.agents/skills/fluid/skills/posthog/agents/openai.yaml" "fluid:posthog UI metadata readable"
assert_file "$TEMP_HOME/.agents/skills/blowmage/skills/assess-me/SKILL.md" "blowmage:assess-me readable"
assert_file "$TEMP_HOME/.agents/skills/blowmage/skills/assess-me/references/assessment-format.md" "blowmage:assess-me format reference readable"
assert_file "$TEMP_HOME/.agents/skills/blowmage/skills/assess-me/references/transcript-sources.md" "blowmage:assess-me transcript reference readable"
assert_file "$TEMP_HOME/.agents/skills/blowmage/skills/assess-me/scripts/collect.py" "blowmage:assess-me collector readable"
assert_file "$TEMP_HOME/.agents/skills/blowmage/skills/assess-me/scripts/extract_prompts.py" "blowmage:assess-me prompt extractor readable"
assert_file "$TEMP_HOME/.agents/skills/blowmage/skills/assess-me/scripts/git_stats.py" "blowmage:assess-me git miner readable"
assert_file "$TEMP_HOME/.agents/skills/blowmage/skills/tdd/SKILL.md" "blowmage:tdd readable"
assert_file "$TEMP_HOME/.agents/skills/blowmage/skills/tdd/references/classicist-testing.md" "blowmage:tdd classicist reference readable"
assert_file "$TEMP_HOME/.agents/skills/blowmage/skills/tdd/references/worked-example.md" "blowmage:tdd worked example readable"
assert_file "$TEMP_HOME/.agents/skills/vercel/skills/ai-sdk/SKILL.md" "vercel:ai-sdk readable"
assert_file "$TEMP_HOME/.agents/skills/vercel/skills/vercel-cli/SKILL.md" "vercel:vercel-cli readable"

for skill in react-doctor typescript-doctor turborepo prd-to-plan improve-codebase-architecture validate-startup-idea find-skills; do
  assert_file "$TEMP_HOME/.agents/skills/brando/skills/$skill/SKILL.md" "brando:$skill readable"
done

for skill in writing-great-skills grill-me teach matt-tdd matt-to-prd grill-with-docs; do
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
assert_count "$TEMP_HOME/.claude/skills" '*' "$EXPECTED_SKILL_COUNT" "Re-run: still $EXPECTED_SKILL_COUNT skills"
assert_count "$TEMP_HOME/.agents/skills" '*' "$EXPECTED_SKILL_COUNT" "Re-run: still $EXPECTED_SKILL_COUNT Codex skills"
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
