#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"

stow_package() {
  local base="$1"
  local pkg="$2"

  [ -d "$base/$pkg" ] || return 0

  echo "  stow $pkg"
  stow -v --no-folding --dir="$base" --target="$HOME" "$pkg"
}

stow_packages_in() {
  local base="$1"
  local skip="${2:-}"
  local pkg_path pkg

  [ -d "$base" ] || return 0

  for pkg_path in "$base"/*/; do
    [ -d "$pkg_path" ] || continue
    pkg="$(basename "$pkg_path")"
    [ "$pkg" = "$skip" ] && continue
    stow_package "$base" "$pkg"
  done
}

symlink_package() {
  local base="$1"
  local pkg="$2"
  local source_dir="$base/$pkg"
  local file rel_path target_file target_dir

  [ -d "$source_dir" ] || return 0

  echo "  symlink $pkg"
  while IFS= read -r -d '' file; do
    rel_path="${file#$source_dir/}"
    target_file="$HOME/$rel_path"
    target_dir="$(dirname "$target_file")"
    mkdir -p "$target_dir"
    ln -sfn "$file" "$target_file"
  done < <(find "$source_dir" -type f -print0)
}

symlink_packages_in() {
  local base="$1"
  local pkg_path pkg

  [ -d "$base" ] || return 0

  for pkg_path in "$base"/*/; do
    [ -d "$pkg_path" ] || continue
    pkg="$(basename "$pkg_path")"
    symlink_package "$base" "$pkg"
  done
}

# --- Homebrew ---
if ! command -v brew &>/dev/null; then
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# --- Dependencies ---
echo "Installing Brewfile..."
brew bundle --file="$DOTFILES/Brewfile"

# --- Stow packages ---
echo "Stowing dotfiles..."
cd "$DOTFILES"

stow_packages_in "$DOTFILES/shared/stow" nvim

# Neovim: handled separately since it may already exist as a git clone
if [ -d "$HOME/.config/nvim/.git" ]; then
  echo "  nvim: existing git repo detected, skipping stow"
  echo "  (manage nvim separately or remove .git and re-run)"
else
  stow_package "$DOTFILES/shared/stow" nvim
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
  stow_packages_in "$DOTFILES/mac/stow"
else
  stow_packages_in "$DOTFILES/linux/stow"
fi

echo "Creating direct symlinks..."
symlink_packages_in "$DOTFILES/shared/symlink"

if [[ "$OSTYPE" == "darwin"* ]]; then
  symlink_packages_in "$DOTFILES/mac/symlink"
else
  symlink_packages_in "$DOTFILES/linux/symlink"
fi

# --- Sync skills, agents, commands ---
echo "Syncing skills..."
"$DOTFILES/sync-skills.sh"

echo ""
echo "Done! Restart your shell or terminal to pick up changes."
