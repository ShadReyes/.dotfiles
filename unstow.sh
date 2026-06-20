#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
cd "$DOTFILES"

is_macos() {
  [[ "${OSTYPE:-}" == darwin* ]] || [ "$(uname -s)" = "Darwin" ]
}

managed_link() {
  local path="$1"
  [ -L "$path" ] || return 1

  local target resolved
  target="$(readlink "$path")"
  case "$target" in
    "$DOTFILES"/*) return 0 ;;
  esac

  resolved="$(cd "$(dirname "$path")" 2>/dev/null && cd "$(dirname "$target")" 2>/dev/null && pwd -P)/$(basename "$target")" || return 1
  case "$resolved" in
    "$DOTFILES"/*) return 0 ;;
  esac

  return 1
}

remove_managed_path() {
  local path="$1"
  if managed_link "$path"; then
    rm -f "$path"
  fi
}

remove_empty_dir() {
  local dir="$1"
  rmdir "$dir" 2>/dev/null || true
}

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

remove_synced_ai_resources() {
  local skill_dir name agent_file command_file generated_agent

  echo "Removing skill/agent/command symlinks managed by this repo..."

  for skill_dir in "$DOTFILES/skills"/*/; do
    [ -d "$skill_dir" ] || continue
    name="$(basename "$skill_dir")"
    remove_managed_path "$HOME/.claude/skills/$name"
    remove_managed_path "$HOME/.agents/skills/$name"
    remove_managed_path "$HOME/.codex/skills/$name"
  done

  for agent_file in "$DOTFILES/agents"/*.toml; do
    [ -f "$agent_file" ] || continue
    name="$(basename "$agent_file" .toml)"
    remove_managed_path "$HOME/.codex/agents/$name.toml"

    # Claude agents are generated markdown files rather than symlinks. Remove
    # only the files that correspond to this repo's canonical agent sources.
    generated_agent="$HOME/.claude/agents/$name.md"
    [ -f "$generated_agent" ] && [ ! -L "$generated_agent" ] && rm -f "$generated_agent"
  done

  for command_file in "$DOTFILES/commands"/*; do
    [ -f "$command_file" ] || continue
    remove_managed_path "$HOME/.claude/commands/$(basename "$command_file")"
  done

  remove_empty_dir "$HOME/.claude/skills"
  remove_empty_dir "$HOME/.claude/agents"
  remove_empty_dir "$HOME/.claude/commands"
  remove_empty_dir "$HOME/.codex/agents"
  remove_empty_dir "$HOME/.codex/skills"
  remove_empty_dir "$HOME/.agents/skills"
  remove_empty_dir "$HOME/.agents"
}

remove_synced_ai_resources
unstow_packages_in "$DOTFILES/shared/stow"

if is_macos; then
  unstow_packages_in "$DOTFILES/mac/stow"
else
  unstow_packages_in "$DOTFILES/linux/stow"
fi

remove_symlink_packages_in "$DOTFILES/shared/symlink"

if is_macos; then
  remove_symlink_packages_in "$DOTFILES/mac/symlink"
else
  remove_symlink_packages_in "$DOTFILES/linux/symlink"
fi

echo "Managed symlinks removed. Manually-created AI resources were preserved."
