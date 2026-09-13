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
AGENT_SKILLS="$HOME/.agents/skills"
SKILL_INDEX="$HOME/.agents/skills-index"

mkdir -p "$CLAUDE_SKILLS" "$AGENT_SKILLS" "$SKILL_INDEX"

prune_dead_skill_links() {
  local dir="$1" link target

  for link in "$dir"/*; do
    [ -L "$link" ] || continue
    target="$(readlink "$link")"
    [[ "$target" == "$DOTFILES/skills/"* ]] || continue
    [ -e "$target" ] && continue
    rm -f "$link"
  done
}

prune_dead_skill_links "$CLAUDE_SKILLS"
prune_dead_skill_links "$AGENT_SKILLS"

skill_count=0
for skill_dir in "$DOTFILES/skills"/*/; do
  [ -d "$skill_dir" ] || continue
  name="$(basename "$skill_dir")"
  ln -sfn "$skill_dir" "$CLAUDE_SKILLS/$name"
  ln -sfn "$skill_dir" "$AGENT_SKILLS/$name"
  skill_count=$((skill_count + 1))
done

echo "  $skill_count skills → Claude + Codex"

# Some clients inspect only direct children of a skill root. Build a flat
# index without changing the canonical skill and plugin layout.
skill_dirs=()
skill_names=()
while IFS= read -r skill_file; do
  skill_dir="$(dirname "$skill_file")"
  name="$(basename "$skill_dir")"
  index_link="$SKILL_INDEX/$name"

  if [ -L "$index_link" ]; then
    target="$(readlink "$index_link")"
    case "$target" in
      "$DOTFILES/skills"|"$DOTFILES/skills/"*) ;;
      *)
        echo "Cannot index skill $name: $index_link is not managed by this repo" >&2
        exit 1
        ;;
    esac
  elif [ -e "$index_link" ]; then
    echo "Cannot index skill $name: $index_link exists and is not a symlink" >&2
    exit 1
  fi

  skill_dirs+=("$skill_dir")
  skill_names+=("$name")
done < <(find "$DOTFILES/skills" -name SKILL.md -type f | sort)

for link in "$SKILL_INDEX"/*; do
  [ -L "$link" ] || continue
  target="$(readlink "$link")"
  case "$target" in
    "$DOTFILES/skills"|"$DOTFILES/skills/"*) rm -f "$link" ;;
  esac
done

indexed_skill_count=0
for index in "${!skill_dirs[@]}"; do
  ln -sfn "${skill_dirs[$index]}" "$SKILL_INDEX/${skill_names[$index]}"
  indexed_skill_count=$((indexed_skill_count + 1))
done

echo "  $indexed_skill_count skills → flat discovery index"

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
