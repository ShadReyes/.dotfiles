# dotfiles

Personal dev environment managed with [GNU Stow](https://www.gnu.org/software/stow/).

## Setup

```sh
git clone git@github.com:USERNAME/dotfiles.git ~/dotfiles
cd ~/dotfiles
./bootstrap.sh
```

## Structure

Each top-level directory is a stow package. The directory structure inside each
package mirrors `$HOME`, so `stow <package>` symlinks everything into place.

```
dotfiles/
  wezterm/.wezterm.lua               -> ~/.wezterm.lua
  nvim/.config/nvim/                 -> ~/.config/nvim/
  claude/.claude/                    -> ~/.claude/{CLAUDE.md,settings.json,...}
  ricekit/.config/ricekit/           -> ~/.config/ricekit/{marketplace.toml,...}
```

## Individual packages

```sh
# Add a single package
stow -v --target="$HOME" wezterm

# Remove a single package
stow -v --delete --target="$HOME" wezterm
```

## Adding new configs

1. Create a new directory: `mkdir -p <package>/<path-mirroring-home>`
2. Move your config file into it
3. Run `stow <package>` to create the symlink
