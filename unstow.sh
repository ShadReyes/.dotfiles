#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
cd "$DOTFILES"

for pkg in wezterm nvim claude ricekit; do
  if [ -d "$pkg" ]; then
    echo "Unstowing $pkg..."
    stow -v --delete --target="$HOME" "$pkg"
  fi
done

echo "All symlinks removed."
