# dotfiles

Personal dev environment for macOS, managed with [GNU Stow](https://www.gnu.org/software/stow/).

## Fresh machine setup

Requires Xcode Command Line Tools (prompted automatically by `git`).

```sh
xcode-select --install  # if not already installed
git clone git@github.com:ShadReyes/dotfiles.git ~/dotfiles
cd ~/dotfiles
./bootstrap.sh
```

`bootstrap.sh` will:
1. Install [Homebrew](https://brew.sh) if missing
2. Install all dependencies from `Brewfile` (stow, neovim, wezterm, ripgrep, rustup, hack-nerd-font, etc.)
3. Symlink each package into `$HOME` via stow

The ricekit CLI is not on Homebrew (private, proprietary repo) — see [ricekit setup](#ricekit-setup) below to build it.

## Packages

### wezterm

WezTerm terminal configuration.

- `~/.wezterm.lua` — keybindings, appearance, fonts

### nvim

Neovim config based on [kickstart.nvim](https://github.com/nvim-kickstart/kickstart.nvim).

- `~/.config/nvim/init.lua` — main config
- `~/.config/nvim/lua/custom/plugins/` — personal plugins
- `~/.config/nvim/lua/kickstart/plugins/` — kickstart plugin modules

On first launch, [lazy.nvim](https://github.com/folke/lazy.nvim) auto-installs all plugins. No manual steps needed.

### claude

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI configuration.

- `~/.claude/CLAUDE.md` — global instructions
- `~/.claude/settings.json` — model, permissions, hooks, plugins
- `~/.claude/skills/` — 11 custom skills (code-search, grill-me, solving-linear-issues, etc.)
- `~/.claude/agents/` — custom agent definitions (bottom-sheet-specialist, remote-dom-specialist)
- `~/.claude/hooks/` — post-tool-use hooks (plan backup)
- `~/.claude/templates/` — PR summary template
- `~/.claude/commands/` — slash commands

> **Note:** Some skills (vercel-\*, web-design-guidelines) are managed externally
> via marketplace plugins and are not tracked here. They install automatically
> when the plugins are enabled in `settings.json`.

### ricekit

[Ricekit](https://ricekit.dev) theme manager configuration.

- `~/.config/ricekit/marketplace.toml` — installed configs and themes
- `~/.config/ricekit/custom-themes/` — personal themes (morning-mountains, vo9lyx14s41a1)
- `~/.config/ricekit/custom-integrations/` — custom integrations (govee-color)
- `~/.config/ricekit/extensions/` — browser extensions (firefox)

After stowing, run `ricekit apply` to render the active theme across apps.

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

## Managing packages

```sh
cd ~/dotfiles

# Stow a single package
stow -v --target="$HOME" wezterm

# Unstow a single package
stow -v --delete --target="$HOME" wezterm

# Unstow everything
./unstow.sh
```

## Adding new configs

1. `mkdir -p <package>/<path-mirroring-home>`
2. Move the config file into the new directory
3. `stow -v --target="$HOME" <package>`
4. Commit and push
