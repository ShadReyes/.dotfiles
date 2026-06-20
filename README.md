# .dotfiles

Personal dev environment, managed with [GNU Stow](https://www.gnu.org/software/stow/), a macOS `Brewfile`, and a custom sync script for shared AI resources.

## Fresh machine setup

Requires Xcode Command Line Tools (prompted automatically by `git`).

```sh
xcode-select --install  # if not already installed
git clone git@github.com:ShadReyes/.dotfiles.git ~/.dotfiles
cd ~/.dotfiles
./bootstrap.sh
```

`bootstrap.sh` will:
1. Install [Homebrew](https://brew.sh) if missing
2. Install all dependencies from `Brewfile` (stow, neovim, wezterm, ripgrep, rustup, hack-nerd-font, etc.)
3. Symlink shared and platform-specific stow packages into `$HOME`
4. Run `sync-skills.sh` to symlink skills, agents, and commands to all AI CLIs

The ricekit CLI is not on Homebrew (private, proprietary repo) — see [ricekit setup](#ricekit-setup) below to build it.

## Repository layout

```text
Brewfile              # macOS package source of truth
bootstrap.sh          # fresh-machine install entrypoint
shared/stow/          # configs shared across platforms
shared/symlink/       # direct shared symlink packages
mac/stow/             # macOS-only stow packages
mac/symlink/          # direct macOS symlink packages
linux/stow/           # reserved for Linux-only stow packages
linux/symlink/        # direct Linux symlink packages
skills/               # shared SKILL.md resources
agents/               # canonical TOML agent definitions
commands/             # Claude slash commands
scripts/              # helper scripts
```

This keeps the repo close to a shared/platform split while retaining the existing
winning pieces: `Brewfile` for macOS packages, readable bootstrap docs, and the
canonical TOML agent source used by `sync-skills.sh`.

## Stow packages

Shared stow packages live in `shared/stow/`. Platform stow packages live in
`mac/stow/` or `linux/stow/`. Direct symlink packages can live in the matching
`shared/symlink/`, `mac/symlink/`, or `linux/symlink/` layer when Stow is the
wrong tool for a config.

### wezterm

WezTerm terminal configuration.

- `~/.wezterm.lua` — keybindings, appearance, fonts
- Source: `shared/stow/wezterm/`

### nvim

Neovim config based on [kickstart.nvim](https://github.com/nvim-kickstart/kickstart.nvim).

- `~/.config/nvim/init.lua` — main config
- `~/.config/nvim/lua/custom/plugins/` — personal plugins
- `~/.config/nvim/lua/kickstart/plugins/` — kickstart plugin modules

On first launch, [lazy.nvim](https://github.com/folke/lazy.nvim) auto-installs all plugins. No manual steps needed.

- Source: `shared/stow/nvim/`

### claude

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI configuration.

- `~/.claude/CLAUDE.md` — global instructions
- `~/.claude/settings.json` — model, permissions, hooks, plugins
- `~/.claude/hooks/` — post-tool-use hooks (plan backup)
- `~/.claude/templates/` — PR summary template
- `~/.claude/statusline-command.js` — iTerm2 status line

> Skills, agents, and commands are managed by `sync-skills.sh` (see below).

- Source: `shared/stow/claude/`

### codex

[OpenAI Codex CLI](https://github.com/openai/codex) configuration.

- `~/.codex/AGENTS.md` — global instructions

> Skills and agents are managed by `sync-skills.sh` (see below).

- Source: `shared/stow/codex/`

### ricekit

[Ricekit](https://ricekit.dev) theme manager configuration.

- `~/.config/ricekit/marketplace.toml` — installed configs and themes
- `~/.config/ricekit/custom-themes/` — personal themes (morning-mountains, vo9lyx14s41a1)
- `~/.config/ricekit/custom-integrations/` — custom integrations (govee-color)
- `~/.config/ricekit/extensions/` — browser extensions (firefox)

After stowing, run `ricekit apply` to render the active theme across apps.

- Source: `mac/stow/ricekit/`

#### ricekit setup

Ricekit is a private, proprietary product — not on Homebrew. Build the CLI from source after bootstrap:

```sh
rustup default stable   # rustup is installed by Brewfile but has no toolchain yet
git clone git@github.com:brs98/ricekit.git ~/src/ricekit
cd ~/src/ricekit
cargo install --path crates/ricekit-cli --locked
. "$HOME/.cargo/env"    # add ~/.cargo/bin to PATH for this shell
```

The community configs listed in `marketplace.toml` are not bundled with the repo (the
`installed-configs/` directory is runtime state and gitignored). Reinstall them on a fresh machine:

```sh
ricekit marketplace refresh
for cfg in wezterm-colors slack-desktop linear-desktop chrome-colors userstyles; do
  ricekit marketplace install "$cfg"
done
ricekit apply <theme>
```

## Shared AI resources

Skills, agents, and commands live in agent-neutral top-level directories. `sync-skills.sh` symlinks them into the right places for each AI CLI.

### skills/

Custom skills in shared `SKILL.md` format (works with both Claude Code and Codex).

Synced to `~/.claude/skills/` and `~/.agents/skills/`.
Direct root skills also have `agents/openai.yaml` metadata so they appear cleanly in Codex skill
UI lists.

In Codex, `/skills` opens a menu. Choose `List skills` to open the `$` mention picker, then search
for a skill such as `address` or type `$address-pr-comments` directly.

The `brando` and `matt` directories are local plugin bundles for vendored skill sets.
Plugin skills are namespaced, such as `brando:react-doctor` and `matt:tdd`.
The root `grilling` skill is still vendored from
[`mattpocock/skills`](https://github.com/mattpocock/skills).

### agents/

Custom agent definitions in canonical TOML format. `sync-skills.sh` symlinks the TOML to Codex and generates Claude Code markdown.

- `agents/*.toml` — single source of truth per agent

Synced to `~/.codex/agents/` (symlink) and `~/.claude/agents/` (generated `.md`).

### commands/

Slash commands (Claude Code only).

Synced to `~/.claude/commands/`.

## Managing packages

```sh
cd ~/.dotfiles

# Stow a single package
stow -v --no-folding --dir=shared/stow --target="$HOME" wezterm

# Unstow a single package
stow -v --delete --no-folding --dir=shared/stow --target="$HOME" wezterm

# Re-sync skills/agents/commands after changes
./sync-skills.sh

# Unstow everything
./unstow.sh
```

## Adding new configs

1. Pick the right layer: `shared/stow`, `mac/stow`, or `linux/stow`
2. `mkdir -p <layer>/<package>/<path-mirroring-home>`
3. Move the config file into the new package directory
4. `stow -v --no-folding --dir=<layer> --target="$HOME" <package>`
5. Commit and push

## Adding a new skill

1. `mkdir skills/<skill-name>`
2. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`) and markdown body
3. Run `./sync-skills.sh`
4. Commit and push

Imported third-party skills should include their companion docs in the same skill directory, plus an
`agents/openai.yaml` file for Codex UI metadata.
