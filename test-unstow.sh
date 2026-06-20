#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  ✓ $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  ✗ $1"; }
assert_file() { [ -f "$1" ] && pass "$2" || fail "$2"; }
assert_missing() { [ ! -e "$1" ] && [ ! -L "$1" ] && pass "$2" || fail "$2"; }

make_fake_stow() {
  local bin="$1"
  cat > "$bin/stow" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
base=""
target=""
delete=0
pkg=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dir=*) base="${1#--dir=}" ;;
    --target=*) target="${1#--target=}" ;;
    --delete|-D) delete=1 ;;
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
  dest="$target/$rel"
  if [ "$delete" = 1 ]; then
    if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$src/$rel" ]; then
      rm -f "$dest"
    fi
  else
    mkdir -p "$target/$(dirname "$rel")"
    ln -sfn "$src/$rel" "$dest"
  fi
done
SH
  chmod +x "$bin/stow"
}

echo "Safe unstow"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
bin="$tmp/bin"
mkdir -p "$bin" "$tmp/home/.claude/skills/manual-skill" "$tmp/home/.claude/agents" "$tmp/home/.claude/commands" "$tmp/home/.codex/agents" "$tmp/home/.agents/skills/manual-skill"
make_fake_stow "$bin"
printf 'manual skill\n' > "$tmp/home/.claude/skills/manual-skill/SKILL.md"
printf 'manual codex skill\n' > "$tmp/home/.agents/skills/manual-skill/SKILL.md"
printf 'manual agent\n' > "$tmp/home/.claude/agents/manual.md"
printf 'manual command\n' > "$tmp/home/.claude/commands/manual.md"
printf 'manual codex agent\n' > "$tmp/home/.codex/agents/manual.toml"

HOME="$tmp/home" PATH="$bin:/usr/bin:/bin" "$DOTFILES/sync-skills.sh" > /dev/null
assert_file "$tmp/home/.claude/skills/address-pr-comments/SKILL.md" "dotfiles skill linked before unstow"
assert_file "$tmp/home/.claude/skills/manual-skill/SKILL.md" "manual Claude skill exists before unstow"

if HOME="$tmp/home" PATH="$bin:/usr/bin:/bin" "$DOTFILES/unstow.sh" > "$tmp/unstow.out" 2> "$tmp/unstow.err"; then
  pass "unstow.sh exits successfully"
else
  sed 's/^/    unstow: /' "$tmp/unstow.out"
  sed 's/^/    unstow err: /' "$tmp/unstow.err"
  fail "unstow.sh should exit successfully"
fi

assert_missing "$tmp/home/.claude/skills/address-pr-comments" "dotfiles Claude skill symlink removed"
assert_missing "$tmp/home/.agents/skills/address-pr-comments" "dotfiles shared skill symlink removed"
assert_missing "$tmp/home/.codex/agents/remote-dom-specialist.toml" "dotfiles Codex agent symlink removed"
assert_missing "$tmp/home/.claude/commands/update-status.md" "dotfiles Claude command symlink removed"
assert_file "$tmp/home/.claude/skills/manual-skill/SKILL.md" "manual Claude skill preserved"
assert_file "$tmp/home/.agents/skills/manual-skill/SKILL.md" "manual shared skill preserved"
assert_file "$tmp/home/.claude/agents/manual.md" "manual Claude agent preserved"
assert_file "$tmp/home/.claude/commands/manual.md" "manual Claude command preserved"
assert_file "$tmp/home/.codex/agents/manual.toml" "manual Codex agent preserved"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  $PASS passed, $FAIL failed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

[ "$FAIL" -eq 0 ] || exit 1
