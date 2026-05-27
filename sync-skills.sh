#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"

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

# --- Agents (different formats per tool) ---
CLAUDE_AGENTS="$HOME/.claude/agents"
CODEX_AGENTS="$HOME/.codex/agents"

mkdir -p "$CLAUDE_AGENTS" "$CODEX_AGENTS"

claude_agent_count=0
for f in "$DOTFILES/agents/claude"/*; do
  [ -f "$f" ] || continue
  ln -sfn "$f" "$CLAUDE_AGENTS/$(basename "$f")"
  claude_agent_count=$((claude_agent_count + 1))
done

codex_agent_count=0
for f in "$DOTFILES/agents/codex"/*; do
  [ -f "$f" ] || continue
  ln -sfn "$f" "$CODEX_AGENTS/$(basename "$f")"
  codex_agent_count=$((codex_agent_count + 1))
done

echo "  $claude_agent_count agents → Claude, $codex_agent_count agents → Codex"

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
