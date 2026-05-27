#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"

# Convert a TOML agent file to Claude Code markdown (YAML frontmatter + body).
# Reads top-level name, description, developer_instructions, and [claude] table.
toml2claude() {
  local input="$1" output="$2"
  local name description model color instructions

  name=$(grep '^name' "$input" | head -1 | sed 's/^name *= *"\(.*\)"/\1/')
  description=$(grep '^description' "$input" | head -1 | sed 's/^description *= *"\(.*\)"/\1/')
  model=$(sed -n 's/^# claude:model *= *//p' "$input")
  color=$(sed -n 's/^# claude:color *= *//p' "$input")
  instructions=$(sed -n '/^developer_instructions *= *"""/,/^"""/{ /^developer_instructions/d; /^"""/d; p; }' "$input")

  {
    echo "---"
    echo "name: $name"
    echo "description: $description"
    [ -n "$model" ] && echo "model: $model"
    [ -n "$color" ] && echo "color: $color"
    echo "---"
    echo ""
    echo "$instructions"
  } > "$output"
}

# --- Skills (shared SKILL.md format — both Claude and Codex read it) ---
CLAUDE_SKILLS="$HOME/.claude/skills"
CODEX_SKILLS="$HOME/.agents/skills"

mkdir -p "$CLAUDE_SKILLS" "$CODEX_SKILLS"

skill_count=0
for skill_dir in "$DOTFILES/skills"/*/; do
  [ -d "$skill_dir" ] || continue
  name="$(basename "$skill_dir")"
  ln -sfn "$skill_dir" "$CLAUDE_SKILLS/$name"
  ln -sfn "$skill_dir" "$CODEX_SKILLS/$name"
  skill_count=$((skill_count + 1))
done

echo "  $skill_count skills → Claude + Codex"

# --- Agents (canonical TOML → symlink to Codex, generate markdown for Claude) ---
CLAUDE_AGENTS="$HOME/.claude/agents"
CODEX_AGENTS="$HOME/.codex/agents"

mkdir -p "$CLAUDE_AGENTS" "$CODEX_AGENTS"

agent_count=0
for f in "$DOTFILES/agents"/*.toml; do
  [ -f "$f" ] || continue
  name="$(basename "$f" .toml)"
  ln -sfn "$f" "$CODEX_AGENTS/$name.toml"
  toml2claude "$f" "$CLAUDE_AGENTS/$name.md"
  agent_count=$((agent_count + 1))
done

echo "  $agent_count agents → Claude (generated) + Codex (symlinked)"

# --- Commands (Claude only — Codex uses $skill-name invocation) ---
CLAUDE_COMMANDS="$HOME/.claude/commands"
mkdir -p "$CLAUDE_COMMANDS"

cmd_count=0
for f in "$DOTFILES/commands"/*; do
  [ -f "$f" ] || continue
  ln -sfn "$f" "$CLAUDE_COMMANDS/$(basename "$f")"
  cmd_count=$((cmd_count + 1))
done

echo "  $cmd_count commands → Claude"
