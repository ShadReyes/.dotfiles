#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  ✓ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ✗ $1"; }
assert_file() { [ -f "$1" ] && pass "$2" || fail "$2"; }
assert_link() { [ -L "$1" ] && pass "$2" || fail "$2"; }
assert_contains() { grep -q "$2" "$1" 2>/dev/null && pass "$3" || fail "$3"; }
assert_not_contains() { ! grep -q "$2" "$1" 2>/dev/null && pass "$3" || fail "$3"; }
assert_missing() { [ ! -e "$1" ] && [ ! -L "$1" ] && pass "$2" || fail "$2"; }

make_fake_stow() {
  local bin="$1"
  cat > "$bin/stow" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
log="${DOTFILES_TEST_LOG:?}"
echo "stow $*" >> "$log"
base=""
target=""
pkg=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dir=*) base="${1#--dir=}" ;;
    --target=*) target="${1#--target=}" ;;
    --delete|-D) ;;
    -*) ;;
    *) pkg="$1" ;;
  esac
  shift
done
[ -n "$base" ] || exit 0
[ -n "$target" ] || exit 0
[ -n "$pkg" ] || exit 0
src="$base/$pkg"
[ -d "$src" ] || exit 0
cd "$src"
find . -type f | while IFS= read -r file; do
  rel="${file#./}"
  mkdir -p "$target/$(dirname "$rel")"
  ln -sfn "$src/$rel" "$target/$rel"
done
SH
  chmod +x "$bin/stow"
}

make_fake_common_tools() {
  local bin="$1"
  for name in brew curl apt-get sudo git npm; do
    cat > "$bin/$name" <<'SH'
#!/usr/bin/env bash
echo "$(basename "$0") $*" >> "${DOTFILES_TEST_LOG:?}"
case "$(basename "$0")" in
  sudo)
    if [ "${DOTFILES_TEST_SUDO_OK:-0}" = 1 ] && [ "${1:-}" = "-n" ] && [ "${2:-}" = "true" ]; then exit 0; fi
    if [ "${DOTFILES_TEST_SUDO_OK:-0}" = 1 ]; then exec "$@"; fi
    exit 1
    ;;
  apt-get)
    exit 0
    ;;
  brew)
    exit 0
    ;;
  curl)
    # This fake replaces installer downloads at the HTTP boundary.
    case "$*" in
      *herdr.dev/install.sh*) printf 'exit 0\n' ;;
      *) printf 'echo unexpected-homebrew-installer\nexit 42\n' ;;
    esac
    exit 0
    ;;
  git)
    # This fake replaces the Git network boundary used to clone Oh My Zsh.
    if [ "${1:-}" = "clone" ]; then
      if [ "${DOTFILES_TEST_GIT_CLONE_FAIL:-0}" = 1 ]; then
        echo "simulated Git clone failure" >&2
        exit 1
      fi
      for destination; do true; done
      mkdir -p "$destination"
      touch "$destination/oh-my-zsh.sh"
      exit 0
    fi
    exec /usr/bin/git "$@"
    ;;
  npm)
    # This fake replaces the npm package-install boundary used by Pi extensions.
    exit 0
    ;;
esac
SH
    chmod +x "$bin/$name"
  done
}

run_bootstrap() {
  local temp_home="$1"
  local bin="$1/bin"
  shift
  mkdir -p "$bin"
  make_fake_stow "$bin"
  make_fake_common_tools "$bin"
  DOTFILES_TEST_LOG="$temp_home/log" HOME="$temp_home" PATH="$bin:/usr/bin:/bin" DOTFILES_OS="${DOTFILES_TEST_OS:-}" "$DOTFILES/bootstrap.sh" "$@" > "$temp_home/out" 2> "$temp_home/err"
}

echo "Bootstrap flags"
test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT
tmp="$test_root/stow-only"
mkdir -p "$tmp/home"
if DOTFILES_TEST_OS=linux run_bootstrap "$tmp/home" --stow-only; then
  pass "--stow-only succeeds without Homebrew on Linux"
else
  fail "--stow-only should succeed without Homebrew on Linux"
fi
assert_missing "$tmp/home/.brew-called" "--stow-only does not create fake brew marker"
if grep -q '^brew ' "$tmp/home/log" 2>/dev/null || grep -q '^curl ' "$tmp/home/log" 2>/dev/null; then
  fail "--stow-only should not call brew or curl"
else
  pass "--stow-only skips package manager and Homebrew installer"
fi
if grep -q '^git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git ' "$tmp/home/log" 2>/dev/null; then
  fail "--stow-only should not install Oh My Zsh"
else
  pass "--stow-only skips Oh My Zsh installation"
fi
assert_file "$tmp/home/.codex/AGENTS.md" "--stow-only still stows shared codex config"
assert_file "$tmp/home/.claude/skills/address-pr-comments/SKILL.md" "--stow-only still syncs skills"
assert_link "$tmp/home/.zshrc" "--stow-only links the shared Zsh configuration"

echo ""
echo "WezTerm theme reload"
# WezTerm supplies HOME; the Ricekit installation owns the color file's presence.
assert_contains "$DOTFILES/shared/stow/wezterm/.wezterm.lua" '^local ricekit_colors_path = os.getenv("HOME") .. "/.config/wezterm/ricekit-colors.lua"$' "WezTerm defines the Ricekit color path once"
assert_contains "$DOTFILES/shared/stow/wezterm/.wezterm.lua" '^wezterm.add_to_config_reload_watch_list(ricekit_colors_path)$' "WezTerm watches Ricekit color changes"
assert_contains "$DOTFILES/shared/stow/wezterm/.wezterm.lua" '^config.colors = dofile(ricekit_colors_path)$' "WezTerm loads colors from the watched path"
assert_contains "$DOTFILES/shared/stow/wezterm/.wezterm.lua" '^config.text_background_opacity = 0.6$' "WezTerm softens application background colors"
assert_not_contains "$DOTFILES/shared/stow/zsh/.zshrc" 'NO_COLOR=1 command codex' "Zsh preserves Codex colors"

echo ""
echo "macOS package install remains Homebrew-first"
tmp_macos="$test_root/macos"
DOTFILES_TEST_OS=macos run_bootstrap "$tmp_macos" --packages
assert_contains "$tmp_macos/log" '^brew bundle --file=' "macOS package mode uses brew bundle"
assert_contains "$tmp_macos/log" '^git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git ' "macOS package mode installs Oh My Zsh"
assert_file "$tmp_macos/.oh-my-zsh/oh-my-zsh.sh" "Oh My Zsh installation is usable"
assert_contains "$DOTFILES/Brewfile" '^tap "FelixKratz/formulae"' "macOS Brewfile adds the JankyBorders tap"
assert_contains "$DOTFILES/Brewfile" '^brew "borders"' "macOS Brewfile installs JankyBorders"
if grep -q '^sudo apt-get' "$tmp_macos/log" 2>/dev/null; then
  fail "macOS package mode should not use apt-get"
else
  pass "macOS package mode does not use apt-get"
fi

echo ""
echo "Ricekit marketplace state"
assert_contains "$DOTFILES/mac/stow/ricekit/.config/ricekit/marketplace.toml" 'name = "jankyborders-colors"' "Ricekit marketplace state includes JankyBorders colors"

echo ""
echo "Existing Oh My Zsh installation"
tmp_existing="$test_root/existing"
mkdir -p "$tmp_existing/.oh-my-zsh"
printf 'existing-installation\n' > "$tmp_existing/.oh-my-zsh/oh-my-zsh.sh"
DOTFILES_TEST_OS=macos run_bootstrap "$tmp_existing" --packages
if grep -q '^git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git ' "$tmp_existing/log" 2>/dev/null; then
  fail "package mode should not replace an existing Oh My Zsh installation"
else
  pass "package mode preserves an existing Oh My Zsh installation"
fi
assert_contains "$tmp_existing/.oh-my-zsh/oh-my-zsh.sh" 'existing-installation' "existing Oh My Zsh files remain unchanged"

echo ""
echo "Incomplete Oh My Zsh path"
tmp_incomplete="$test_root/incomplete"
mkdir -p "$tmp_incomplete/.oh-my-zsh"
touch "$tmp_incomplete/.oh-my-zsh/unrelated-file"
if DOTFILES_TEST_OS=macos run_bootstrap "$tmp_incomplete" --packages; then
  fail "package mode should reject an incomplete Oh My Zsh path"
else
  pass "package mode rejects an incomplete Oh My Zsh path"
fi
assert_contains "$tmp_incomplete/err" 'exists but is not a complete Oh My Zsh installation' "incomplete path error explains the conflict"
if grep -q '^git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git ' "$tmp_incomplete/log" 2>/dev/null; then
  fail "package mode should not clone into an incomplete Oh My Zsh path"
else
  pass "package mode leaves an incomplete Oh My Zsh path unchanged"
fi

echo ""
echo "Broken Oh My Zsh symlink"
tmp_broken_link="$test_root/broken-link"
mkdir -p "$tmp_broken_link"
ln -s "$tmp_broken_link/missing-oh-my-zsh" "$tmp_broken_link/.oh-my-zsh"
if DOTFILES_TEST_OS=macos run_bootstrap "$tmp_broken_link" --packages; then
  fail "package mode should reject a broken Oh My Zsh symlink"
else
  pass "package mode rejects a broken Oh My Zsh symlink"
fi
assert_contains "$tmp_broken_link/err" 'exists but is not a complete Oh My Zsh installation' "broken symlink error explains the conflict"

echo ""
echo "Oh My Zsh clone failure"
tmp_clone_failure="$test_root/clone-failure"
if DOTFILES_TEST_OS=macos DOTFILES_TEST_GIT_CLONE_FAIL=1 run_bootstrap "$tmp_clone_failure" --packages; then
  fail "package mode should report an Oh My Zsh clone failure"
else
  pass "package mode reports an Oh My Zsh clone failure"
fi
assert_contains "$tmp_clone_failure/err" 'simulated Git clone failure' "Git clone failure remains visible"
assert_missing "$tmp_clone_failure/.oh-my-zsh" "failed clone does not produce an installation"

echo ""
echo "Linux package install"
tmp_linux="$test_root/linux"
DOTFILES_TEST_OS=linux DOTFILES_TEST_SUDO_OK=1 run_bootstrap "$tmp_linux" --packages
assert_contains "$tmp_linux/log" '^sudo apt-get update' "Linux package mode uses sudo apt-get update"
assert_contains "$tmp_linux/log" '^sudo apt-get install' "Linux package mode uses sudo apt-get install"
assert_contains "$tmp_linux/log" '^git clone --depth=1 https://github.com/ohmyzsh/ohmyzsh.git ' "Linux package mode installs Oh My Zsh"
if grep -q '^brew ' "$tmp_linux/log" 2>/dev/null; then
  fail "Linux package mode should not use brew"
else
  pass "Linux package mode does not use brew"
fi

echo ""
echo "Doctor"
if HOME="$tmp/home" PATH="$tmp/home/bin:/usr/bin:/bin" DOTFILES_DOCTOR_SKIP_STOW_DRY_RUN=1 "$DOTFILES/scripts/doctor" > "$tmp/doctor.out" 2> "$tmp/doctor.err"; then
  pass "doctor succeeds after stow-only setup"
else
  sed 's/^/    doctor: /' "$tmp/doctor.out"
  sed 's/^/    doctor err: /' "$tmp/doctor.err"
  fail "doctor should succeed after stow-only setup"
fi
assert_contains "$tmp/doctor.out" 'Broken symlinks: none' "doctor reports no broken symlinks"
assert_contains "$tmp/doctor.out" '~/.zshrc: symlink ->' "doctor reports the managed Zsh configuration"
expected_skill_count="$(find "$DOTFILES/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
assert_contains "$tmp/doctor.out" "Claude skills: $expected_skill_count" "doctor reports Claude skill count"
assert_contains "$tmp/doctor.out" 'Codex agents: 2' "doctor reports Codex agent count"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  $PASS passed, $FAIL failed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

[ "$FAIL" -eq 0 ] || exit 1
