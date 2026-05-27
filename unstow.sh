#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
cd "$DOTFILES"

# Remove sync-skills symlinks first (these aren't managed by stow)
echo "Removing skill/agent/command symlinks..."
rm -f "$HOME/.claude/skills"/* "$HOME/.claude/agents"/* "$HOME/.claude/commands"/* 2>/dev/null
rm -f "$HOME/.codex/agents"/* 2>/dev/null
rm -f "$HOME/.agents/skills"/* 2>/dev/null
rmdir "$HOME/.claude/skills" "$HOME/.claude/agents" "$HOME/.claude/commands" 2>/dev/null
rmdir "$HOME/.codex/agents" 2>/dev/null
rmdir "$HOME/.agents/skills" "$HOME/.agents" 2>/dev/null

for pkg in wezterm nvim claude codex ricekit; do
  if [ -d "$pkg" ]; then
    echo "Unstowing $pkg..."
    stow -v --delete --target="$HOME" "$pkg"
  fi
done

echo "All symlinks removed."
