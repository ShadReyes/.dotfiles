#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"

# --- pi packages (stow-style symlinked dirs under ~/.pi/agent/extensions) ---
# Package dirs may be tracked directly or pinned as git submodules. Each holds
# an index.ts entry point, so pi auto-discovers it via its
# `~/.pi/agent/extensions/*/index.ts` rule and /reload picks up edits.
PI_EXTENSIONS="$HOME/.pi/agent/extensions"

mkdir -p "$PI_EXTENSIONS"

git -C "$DOTFILES" submodule update --init --recursive -- pi/orca-pi

prune_dead_pi_links() {
  local dir="$1" link target

  for link in "$dir"/*; do
    [ -L "$link" ] || continue
    target="$(readlink "$link")"
    [[ "$target" == "$DOTFILES/pi/"* ]] || continue
    [ -e "$target" ] && continue
    rm -f "$link"
  done
}

prune_dead_pi_links "$PI_EXTENSIONS"

pi_count=0
for pkg_dir in "$DOTFILES/pi"/*/; do
  [ -d "$pkg_dir" ] || continue
  name="$(basename "$pkg_dir")"
  if [[ -f "$pkg_dir/package-lock.json" ]] &&
    { [[ ! -f "$pkg_dir/node_modules/.package-lock.json" ]] ||
      [[ "$pkg_dir/package-lock.json" -nt "$pkg_dir/node_modules/.package-lock.json" ]]; }; then
    npm --prefix "$pkg_dir" ci --no-audit --no-fund
  fi
  ln -sfn "$pkg_dir" "$PI_EXTENSIONS/$name"
  pi_count=$((pi_count + 1))
done

echo "  $pi_count pi packages → ~/.pi/agent/extensions"
