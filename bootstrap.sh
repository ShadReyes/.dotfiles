#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"

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

for pkg in wezterm claude ricekit; do
  echo "  stow $pkg"
  stow -v --target="$HOME" "$pkg"
done

# Neovim: handled separately since it may already exist as a git clone
if [ -d "$HOME/.config/nvim/.git" ]; then
  echo "  nvim: existing git repo detected, skipping stow"
  echo "  (manage nvim separately or remove .git and re-run)"
else
  echo "  stow nvim"
  stow -v --target="$HOME" nvim
fi

echo ""
echo "Done! Restart your shell or terminal to pick up changes."
