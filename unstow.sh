#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
cd "$DOTFILES"

unstow_packages_in() {
  local base="$1"
  local pkg_path pkg

  [ -d "$base" ] || return 0

  for pkg_path in "$base"/*/; do
    [ -d "$pkg_path" ] || continue
    pkg="$(basename "$pkg_path")"
    echo "Unstowing $pkg..."
    stow -v --delete --no-folding --dir="$base" --target="$HOME" "$pkg"
  done
}

remove_symlink_package() {
  local base="$1"
  local pkg="$2"
  local source_dir="$base/$pkg"
  local file rel_path target_file current_target

  [ -d "$source_dir" ] || return 0

  echo "Removing direct symlinks for $pkg..."
  while IFS= read -r -d '' file; do
    rel_path="${file#$source_dir/}"
    target_file="$HOME/$rel_path"
    [ -L "$target_file" ] || continue
    current_target="$(readlink "$target_file")"
    [ "$current_target" = "$file" ] && rm -f "$target_file"
  done < <(find "$source_dir" -type f -print0)
}

remove_symlink_packages_in() {
  local base="$1"
  local pkg_path pkg

  [ -d "$base" ] || return 0

  for pkg_path in "$base"/*/; do
    [ -d "$pkg_path" ] || continue
    pkg="$(basename "$pkg_path")"
    remove_symlink_package "$base" "$pkg"
  done
}

# Remove sync-skills symlinks first (these aren't managed by stow)
echo "Removing skill/agent/command symlinks..."
rm -f "$HOME/.claude/skills"/* "$HOME/.claude/agents"/* "$HOME/.claude/commands"/* 2>/dev/null
rm -f "$HOME/.codex/agents"/* 2>/dev/null
rm -f "$HOME/.agents/skills"/* 2>/dev/null
for skill_dir in "$DOTFILES/skills"/*/; do
  [ -d "$skill_dir" ] || continue
  rm -f "$HOME/.codex/skills/$(basename "$skill_dir")" 2>/dev/null
done
rmdir "$HOME/.claude/skills" "$HOME/.claude/agents" "$HOME/.claude/commands" 2>/dev/null
rmdir "$HOME/.codex/agents" 2>/dev/null
rmdir "$HOME/.agents/skills" "$HOME/.agents" 2>/dev/null

unstow_packages_in "$DOTFILES/shared/stow"
unstow_packages_in "$DOTFILES/mac/stow"
unstow_packages_in "$DOTFILES/linux/stow"
remove_symlink_packages_in "$DOTFILES/shared/symlink"
remove_symlink_packages_in "$DOTFILES/mac/symlink"
remove_symlink_packages_in "$DOTFILES/linux/symlink"

echo "All symlinks removed."
