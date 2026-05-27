---
name: lazyvim-config
description: Use when asking questions about Neovim, LazyVim, or Lua configuration. Use when configuring plugins, keymaps, options, or troubleshooting Neovim issues. Triggers on nvim, neovim, lazyvim, lua config, plugin errors, keymap not working.
---

# LazyVim Configuration Helper

## Overview

Helps configure and troubleshoot your LazyVim setup at `~/.config/nvim/`.

## Config Structure

```
~/.config/nvim/
├── init.lua              # Entry point (loads config.lazy)
├── lazyvim.json          # Enabled LazyVim extras
├── lazy-lock.json        # Plugin version lock file
└── lua/
    ├── config/
    │   ├── autocmds.lua  # Auto commands
    │   ├── keymaps.lua   # Custom keybindings
    │   ├── lazy.lua      # Lazy.nvim bootstrap
    │   └── options.lua   # Vim options
    └── plugins/
        └── *.lua         # Plugin specs (each file auto-loaded)
```

## Quick Reference

| Task | File | Pattern |
|------|------|---------|
| Add keymap | `lua/config/keymaps.lua` | `vim.keymap.set("n", "<leader>xx", function, { desc = "Description" })` |
| Set option | `lua/config/options.lua` | `vim.opt.relativenumber = true` |
| Add plugin | `lua/plugins/NAME.lua` | `return { "author/plugin-name" }` |
| Configure plugin | `lua/plugins/NAME.lua` | `return { "plugin", opts = { ... } }` |
| Disable plugin | `lua/plugins/NAME.lua` | `return { "plugin", enabled = false }` |
| Enable extra | `:LazyExtras` | Toggle in UI, saves to `lazyvim.json` |

## Current Extras Enabled

- `lazyvim.plugins.extras.lang.typescript`
- `lazyvim.plugins.extras.util.dot`

## Common Plugin Patterns

### Add a new plugin
```lua
-- lua/plugins/my-plugin.lua
return {
  "author/plugin-name",
  event = "VeryLazy",  -- lazy load
  opts = {
    -- plugin options
  },
}
```

### Override LazyVim plugin opts
```lua
return {
  "existing/plugin",
  opts = { option = "value" },  -- merged with defaults
}
```

### Override with function (full control)
```lua
return {
  "existing/plugin",
  opts = function(_, opts)
    opts.something = "new"
    return opts
  end,
}
```

### Add dependencies
```lua
return {
  "main/plugin",
  dependencies = { "dep/plugin" },
}
```

## Keymapping

```lua
-- In lua/config/keymaps.lua
local map = vim.keymap.set

-- Normal mode
map("n", "<leader>w", "<cmd>w<cr>", { desc = "Save file" })

-- Multiple modes
map({ "n", "v" }, "<leader>y", '"+y', { desc = "Yank to clipboard" })

-- With function
map("n", "<leader>t", function()
  -- do something
end, { desc = "Do thing" })
```

## Troubleshooting

| Issue | Command/Solution |
|-------|------------------|
| Check health | `:checkhealth` |
| Lazy status | `:Lazy` |
| Update plugins | `:Lazy update` |
| Sync plugins | `:Lazy sync` |
| View logs | `:Lazy log` |
| LSP info | `:LspInfo` |
| Mason status | `:Mason` |
| Treesitter info | `:TSInstallInfo` |
| Clear cache | Delete `~/.local/share/nvim` and `~/.local/state/nvim` |

## Common Issues

**Plugin not loading**: Check if `enabled = false` elsewhere, verify event/keys triggers.

**Keymap conflict**: Use `:verbose map <key>` to see what's bound. LazyVim default keymaps: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua

**LSP not attaching**: Check `:LspInfo`, ensure server installed via Mason, check filetype with `:set ft?`

**Options not applying**: Ensure file is in `lua/config/options.lua`, check load order (options load before plugins).
