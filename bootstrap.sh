#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
INSTALL_PACKAGES=1

usage() {
  cat <<'EOF'
Usage: ./bootstrap.sh [--packages|--no-packages|--stow-only]

Options:
  --packages     Install platform dependencies before linking configs (default)
  --no-packages  Skip package installation and only link/sync configs
  --stow-only    Alias for --no-packages; useful on servers/headless hosts
  -h, --help     Show this help
EOF
}

for arg in "$@"; do
  case "$arg" in
    --packages) INSTALL_PACKAGES=1 ;;
    --no-packages|--stow-only) INSTALL_PACKAGES=0 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; usage >&2; exit 2 ;;
  esac
done

is_macos() {
  [ "${DOTFILES_OS:-}" = "macos" ] || { [ -z "${DOTFILES_OS:-}" ] && { [[ "${OSTYPE:-}" == darwin* ]] || [ "$(uname -s)" = "Darwin" ]; }; }
}

is_linux() {
  [ "${DOTFILES_OS:-}" = "linux" ] || { [ -z "${DOTFILES_OS:-}" ] && [ "$(uname -s)" = "Linux" ]; }
}

have_sudo() {
  command -v sudo >/dev/null 2>&1 && sudo -n true >/dev/null 2>&1
}

install_macos_packages() {
  if ! command -v brew &>/dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi

  echo "Installing Brewfile..."
  brew bundle --file="$DOTFILES/Brewfile"
}

install_linux_packages() {
  local packages=(stow neovim ripgrep git curl jq)

  if command -v apt-get >/dev/null 2>&1; then
    if have_sudo; then
      echo "Installing Linux dependencies with apt-get..."
      sudo apt-get update
      sudo apt-get install -y "${packages[@]}"
    else
      echo "Skipping apt package install: passwordless sudo is not available."
      echo "Install dependencies manually if needed: ${packages[*]}"
    fi
  else
    echo "No supported Linux package manager found; skipping package install."
    echo "Install dependencies manually if needed: ${packages[*]}"
  fi
}

install_linux_herdr() {
  export PATH="$HOME/.local/bin:$PATH"
  if command -v herdr >/dev/null 2>&1; then
    return 0
  fi

  if ! command -v curl >/dev/null 2>&1; then
    echo "curl is required to install Herdr on Linux." >&2
    return 1
  fi

  echo "Installing Herdr..."
  curl -fsSL https://herdr.dev/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
}

install_packages() {
  if is_macos; then
    install_macos_packages
  elif is_linux; then
    install_linux_packages
    install_linux_herdr
  else
    echo "Unsupported OS for automatic package install: $(uname -s)"
    echo "Continuing without package installation."
  fi
}

install_herdr_integrations() {
  if ! command -v herdr >/dev/null 2>&1; then
    echo "Herdr not found; skipping Herdr agent integrations."
    return 0
  fi

  if [ -d "$HOME/.claude" ]; then
    echo "Installing Herdr Claude integration..."
    env -u HERDR_ENV herdr integration install claude
    normalize_herdr_hook "$HOME/.claude/settings.json" \
      'bash "$HOME/.claude/hooks/herdr-agent-state.sh" session'
  fi

  if [ -d "$HOME/.codex" ]; then
    echo "Installing Herdr Codex integration..."
    env -u HERDR_ENV herdr integration install codex
    normalize_herdr_hook "$HOME/.codex/hooks.json" \
      'bash "$HOME/.codex/herdr-agent-state.sh" session'
  fi
}

normalize_herdr_hook() {
  local settings_path="$1"
  local command="$2"
  local temp_path

  if ! command -v jq >/dev/null 2>&1; then
    echo "jq is required to normalize Herdr hooks; leaving installer output unchanged." >&2
    return 1
  fi

  [ -f "$settings_path" ] || return 0
  temp_path="$(mktemp)"

  if jq --arg command "$command" '
    .hooks.SessionStart = ((.hooks.SessionStart // [])
      | map(select([.hooks[]?.command // ""] | all(contains("herdr-agent-") | not)))
      + [{"matcher":"*","hooks":[{"type":"command","command":$command,"timeout":10}]}])
  ' "$settings_path" >"$temp_path"; then
    cat "$temp_path" >"$settings_path"
  fi

  rm -f "$temp_path"
}

require_stow() {
  if command -v stow >/dev/null 2>&1; then
    return 0
  fi

  cat >&2 <<'EOF'
GNU Stow is required to link dotfiles, but `stow` was not found on PATH.

Install it, then re-run bootstrap:
  macOS: brew install stow
  Ubuntu/Debian: sudo apt-get install stow

For headless/server hosts where you do not want package installs, install only stow
with the system package manager and then run:
  ./bootstrap.sh --stow-only
EOF
  exit 1
}

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

if [ "$INSTALL_PACKAGES" -eq 1 ]; then
  install_packages
else
  echo "Skipping package installation (--stow-only/--no-packages)."
fi

require_stow

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

if is_macos; then
  stow_packages_in "$DOTFILES/mac/stow"
else
  stow_packages_in "$DOTFILES/linux/stow"
fi

echo "Creating direct symlinks..."
symlink_packages_in "$DOTFILES/shared/symlink"

if is_macos; then
  symlink_packages_in "$DOTFILES/mac/symlink"
else
  symlink_packages_in "$DOTFILES/linux/symlink"
fi

# --- Sync skills, agents, commands ---
echo "Syncing skills..."
"$DOTFILES/sync-skills.sh"

echo "Syncing pi packages..."
"$DOTFILES/sync-pi.sh"

echo "Installing Herdr agent integrations..."
install_herdr_integrations

echo ""
echo "Done! Restart your shell or terminal to pick up changes."
