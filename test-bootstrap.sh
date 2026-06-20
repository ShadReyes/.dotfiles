#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  ✓ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ✗ $1"; }
assert_file() { [ -f "$1" ] && pass "$2" || fail "$2"; }
assert_contains() { grep -q "$2" "$1" 2>/dev/null && pass "$3" || fail "$3"; }
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
  for name in brew curl apt-get sudo; do
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
    printf 'echo unexpected-homebrew-installer\nexit 42\n'
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
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/home"
if run_bootstrap "$tmp/home" --stow-only; then
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
assert_file "$tmp/home/.codex/AGENTS.md" "--stow-only still stows shared codex config"
assert_file "$tmp/home/.claude/skills/address-pr-comments/SKILL.md" "--stow-only still syncs skills"

echo ""
echo "macOS package install remains Homebrew-first"
tmp_macos="$(mktemp -d)"
DOTFILES_TEST_OS=macos run_bootstrap "$tmp_macos" --packages
assert_contains "$tmp_macos/log" '^brew bundle --file=' "macOS package mode uses brew bundle"
if grep -q '^sudo apt-get' "$tmp_macos/log" 2>/dev/null; then
  fail "macOS package mode should not use apt-get"
else
  pass "macOS package mode does not use apt-get"
fi

echo ""
echo "Linux package install"
tmp_linux="$(mktemp -d)"
DOTFILES_TEST_SUDO_OK=1 run_bootstrap "$tmp_linux" --packages
assert_contains "$tmp_linux/log" '^sudo apt-get update' "Linux package mode uses sudo apt-get update"
assert_contains "$tmp_linux/log" '^sudo apt-get install' "Linux package mode uses sudo apt-get install"
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
assert_contains "$tmp/doctor.out" 'Claude skills: 17' "doctor reports Claude skill count"
assert_contains "$tmp/doctor.out" 'Codex agents: 2' "doctor reports Codex agent count"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  $PASS passed, $FAIL failed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

[ "$FAIL" -eq 0 ] || exit 1
