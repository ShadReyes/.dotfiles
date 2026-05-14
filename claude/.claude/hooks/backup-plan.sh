#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="$HOME/.claude/plan-backups"
MAX_AGE_DAYS=30

input=$(cat)

file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# Guard: only back up plan files
case "$file_path" in
  */.claude/plans/*.md) ;;
  *) exit 0 ;;
esac

tool_name=$(echo "$input" | jq -r '.tool_name // empty')

# Get content based on tool type
if [[ "$tool_name" == "Write" ]]; then
  content=$(echo "$input" | jq -r '.tool_input.content // empty')
elif [[ "$tool_name" == "Edit" ]]; then
  [[ -f "$file_path" ]] || exit 0
  content=$(cat "$file_path")
else
  exit 0
fi

[[ -z "$content" ]] && exit 0

# Extract description from first heading: strip "#", strip "Plan:" prefix, take first 2 words, lowercase, hyphenate
description=$(echo "$content" \
  | grep -m1 '^# ' \
  | sed 's/^#[[:space:]]*//' \
  | sed 's/^[Pp]lan:[[:space:]]*//' \
  | tr '[:upper:]' '[:lower:]' \
  | awk '{print $1"-"$2}' \
  | sed 's/-$//' \
  | tr -cd 'a-z0-9-')

[[ -z "$description" ]] && description="untitled"

# Build filename
project_dir=$(echo "$input" | jq -r '.cwd // empty' | xargs basename 2>/dev/null || echo "unknown")
date_stamp=$(date +%Y-%m-%d)
base_name="${project_dir}_${date_stamp}_${description}"

mkdir -p "$BACKUP_DIR"

# Determine final path with version suffix if needed
backup_path="$BACKUP_DIR/${base_name}.md"
if [[ -f "$backup_path" ]]; then
  v=2
  while [[ -f "$BACKUP_DIR/${base_name}_v${v}.md" ]]; do
    ((v++))
  done
  backup_path="$BACKUP_DIR/${base_name}_v${v}.md"
fi

echo "$content" > "$backup_path"

# Auto-prune backups older than 30 days
find "$BACKUP_DIR" -name '*.md' -mtime +"$MAX_AGE_DAYS" -delete 2>/dev/null || true
