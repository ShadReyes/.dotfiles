-- Pull in the wezterm API
local wezterm = require("wezterm")

-- This will hold the configuration.
local config = wezterm.config_builder()

config.enable_wayland = false

config.colors = dofile(os.getenv("HOME") .. "/.config/wezterm/ricekit-colors.lua")

config.audible_bell = "Disabled"

local bar = wezterm.plugin.require("https://github.com/adriankarlen/bar.wezterm")
bar.apply_to_config(config, {
	position = "bottom",
	max_width = 32,
	padding = {
		left = 1,
		right = 1,
	},
	modules = {
		pane = {
			enabled = false,
		},
		username = {
			enabled = false,
		},
		clock = {
			enabled = false,
		},
		hostname = {
			enabled = false,
		},
		workspace = {
			enabled = true,
			icon = " ",
			color = 4,
			max_width = 32,
		},
		tabs = {
			active_tab_fg = 4,
			inactive_tab_fg = 8,
		},
	},
})

config.inactive_pane_hsb = {
	saturation = 0.85,
	brightness = 0.7,
}

config.font = wezterm.font("Hack Nerd Font")

-- Adaptive font size based on platform and screen
local font_size = 14.0
if wezterm.target_triple:find("darwin") then
	font_size = 18.0 -- Slightly larger on macOS
elseif wezterm.target_triple:find("linux") then
	font_size = 14.0 -- Standard size on Linux with DPI scaling
end
config.font_size = font_size

-- Better default window size
config.initial_cols = 120
config.initial_rows = 35

-- Window configuration
config.window_decorations = "RESIZE"
config.window_background_opacity = 0.7
config.enable_kitty_keyboard = false
config.enable_csi_u_key_encoding = false

-- macOS-specific improvements
if wezterm.target_triple:find("darwin") then
	config.native_macos_fullscreen_mode = false
	config.use_dead_keys = false
end

-- Better text rendering
config.freetype_load_target = "Normal"
config.freetype_render_target = "HorizontalLcd"

-- Listen for workspace updates and update the status bar
-- wezterm.on("update-status", function(window, _)
-- 	local status = wezterm.format({
-- 		{ Attribute = { Intensity = "Bold" } },
-- 		{ Foreground = { AnsiColor = "Purple" } },
-- 		{ Text = "  " .. window:active_workspace() .. "  " },
-- 	})
-- 	window:set_right_status(status)
-- end)

-- Swap pane with the one in the given direction
local function swap_pane(direction)
	return wezterm.action_callback(function(window, pane)
		local tab = window:mux_window():active_tab()
		local target_pane = tab:get_pane_direction(direction)
		if target_pane then
			target_pane:activate()
			tab:set_zoomed(false)
			window:perform_action(wezterm.action.RotatePanes("CounterClockwise"), pane)
		end
	end)
end

-- Handles same key for navigating panes and tabs
local function navigate_pane_or_tab(direction)
	return wezterm.action_callback(function(window, pane)
		local tab = window:mux_window():active_tab()
		if tab:get_pane_direction(direction) ~= nil then
			window:perform_action(wezterm.action.ActivatePaneDirection(direction), pane)
		else
			window:perform_action(wezterm.action.ActivateTabRelative(direction == "Left" and -1 or 1), pane)

			-- activate the non-direction-most pane
			tab = window:mux_window():active_tab()
			local opposite_direction = direction == "Left" and "Right" or "Left"
			while tab:get_pane_direction(opposite_direction) ~= nil do
				window:perform_action(wezterm.action.ActivatePaneDirection(opposite_direction), pane)
				tab = window:mux_window():active_tab()
			end
		end
	end)
end

local act = wezterm.action

-- Use the same pane shortcuts for Herdr panes and native WezTerm panes.
local function is_herdr_pane(pane)
	local process_name = pane:get_foreground_process_name()
	return process_name == "herdr" or (process_name and process_name:match("[/\\\\]herdr$") ~= nil)
end

local function herdr_or_wezterm(herdr_sequence, wezterm_action)
	return wezterm.action_callback(function(window, pane)
		if is_herdr_pane(pane) then
			window:perform_action(act.SendString(herdr_sequence), pane)
		else
			window:perform_action(wezterm_action, pane)
		end
	end)
end

config.keys = { -- Create new tab
	{
		key = "t",
		mods = "CTRL",
		action = act.SpawnTab("CurrentPaneDomain"),
	},
	{
		key = "t",
		mods = "SUPER",
		action = herdr_or_wezterm("\x02c", act.SpawnTab("CurrentPaneDomain")),
	},
	{ key = "Enter", mods = "SHIFT", action = wezterm.action({ SendString = "\x1b\r" }) },
	-- Close tab
	{
		key = "w",
		mods = "CTRL",
		action = wezterm.action.CloseCurrentTab({ confirm = true }),
	},
	-- Move tab to the left
	{ key = "LeftArrow", mods = "SUPER|CTRL", action = act.MoveTabRelative(-1) },

	-- Move tab to the right
	{ key = "RightArrow", mods = "SUPER|CTRL", action = act.MoveTabRelative(1) },

	-- Switch to default workspace
	{
		key = "1",
		mods = "SUPER|ALT",
		action = herdr_or_wezterm(
			"\x02!",
			act.SwitchToWorkspace({
				name = "default",
			})
		),
	},
	-- Switch to config workspace
	{
		key = "2",
		mods = "SUPER|ALT",
		action = herdr_or_wezterm(
			"\x02@",
			act.SwitchToWorkspace({
				name = "config",
				spawn = {
					args = {
						os.getenv("SHELL"),
						"-c",
						"cd ~/.dotfiles && nvim",
					},
				},
			})
		),
	},
	{ key = "3", mods = "SUPER|ALT", action = herdr_or_wezterm("\x02#", act.SendKey({ key = "3", mods = "SUPER|ALT" })) },
	{ key = "4", mods = "SUPER|ALT", action = herdr_or_wezterm("\x02$", act.SendKey({ key = "4", mods = "SUPER|ALT" })) },
	{ key = "5", mods = "SUPER|ALT", action = herdr_or_wezterm("\x02%", act.SendKey({ key = "5", mods = "SUPER|ALT" })) },
	{ key = "6", mods = "SUPER|ALT", action = herdr_or_wezterm("\x02^", act.SendKey({ key = "6", mods = "SUPER|ALT" })) },
	{ key = "7", mods = "SUPER|ALT", action = herdr_or_wezterm("\x02&", act.SendKey({ key = "7", mods = "SUPER|ALT" })) },
	{ key = "8", mods = "SUPER|ALT", action = herdr_or_wezterm("\x02*", act.SendKey({ key = "8", mods = "SUPER|ALT" })) },
	{ key = "9", mods = "SUPER|ALT", action = herdr_or_wezterm("\x02(", act.SendKey({ key = "9", mods = "SUPER|ALT" })) },
	{
		key = "h",
		mods = "SUPER|ALT",
		action = herdr_or_wezterm("\x02H", act.SendKey({ key = "h", mods = "SUPER|ALT" })),
	},
	{
		key = "l",
		mods = "SUPER|ALT",
		action = herdr_or_wezterm("\x02L", act.SendKey({ key = "l", mods = "SUPER|ALT" })),
	},
	-- Switch to work workspace
	-- {
	-- 	key = "3",
	-- 	mods = "SUPER|ALT",
	-- 	action = act.SwitchToWorkspace({
	-- 		name = "Work",
	-- 		spawn = {
	-- 			args = { os.getenv("SHELL"), "-c", "cd ~/work && nvim" },
	-- 		},
	-- 	}),
	-- },
	-- Prompt for a name to use for a new workspace and switch to it.
	{
		key = "n",
		mods = "SUPER|ALT",
		action = act.PromptInputLine({
			description = wezterm.format({
				{ Attribute = { Intensity = "Bold" } },
				{ Foreground = { AnsiColor = "Purple" } },
				{ Text = "Enter name for new workspace" },
			}),
			action = wezterm.action_callback(function(window, pane, line)
				-- line will be `nil` if they hit escape without entering anything
				-- An empty string if they just hit enter
				-- Or the actual line of text they wrote
				if line then
					window:perform_action(
						act.SwitchToWorkspace({
							name = line,
						}),
						pane
					)
				end
			end),
		}),
	},

	-- Show the launcher in fuzzy selection mode and have it list all workspaces
	-- and allow activating one.
	{
		key = "s",
		mods = "SUPER|ALT",
		action = act.ShowLauncherArgs({
			flags = "FUZZY|WORKSPACES",
		}),
	},

	{ key = "Enter", mods = "ALT", action = act.ToggleFullScreen },

	{ key = "1", mods = "ALT", action = herdr_or_wezterm("\x021", act.ActivateTab(0)) },
	{ key = "2", mods = "ALT", action = herdr_or_wezterm("\x022", act.ActivateTab(1)) },
	{ key = "3", mods = "ALT", action = herdr_or_wezterm("\x023", act.ActivateTab(2)) },
	{ key = "4", mods = "ALT", action = herdr_or_wezterm("\x024", act.ActivateTab(3)) },
	{ key = "5", mods = "ALT", action = herdr_or_wezterm("\x025", act.ActivateTab(4)) },
	{ key = "6", mods = "ALT", action = herdr_or_wezterm("\x026", act.ActivateTab(5)) },
	{ key = "7", mods = "ALT", action = herdr_or_wezterm("\x027", act.ActivateTab(6)) },
	{ key = "8", mods = "ALT", action = herdr_or_wezterm("\x028", act.ActivateTab(7)) },
	{ key = "9", mods = "ALT", action = herdr_or_wezterm("\x029", act.ActivateTab(8)) },
	{ key = "0", mods = "ALT", action = act.ActivateTab(9) },
	{
		key = "h",
		mods = "ALT|SHIFT",
		action = herdr_or_wezterm("\x02p", act.ActivateTabRelative(-1)),
	},
	{
		key = "l",
		mods = "ALT|SHIFT",
		action = herdr_or_wezterm("\x02n", act.ActivateTabRelative(1)),
	},
	{ key = "1", mods = "CTRL|ALT", action = herdr_or_wezterm("\x02\x1b1", act.SendKey({ key = "1", mods = "CTRL|ALT" })) },
	{ key = "2", mods = "CTRL|ALT", action = herdr_or_wezterm("\x02\x1b2", act.SendKey({ key = "2", mods = "CTRL|ALT" })) },
	{ key = "3", mods = "CTRL|ALT", action = herdr_or_wezterm("\x02\x1b3", act.SendKey({ key = "3", mods = "CTRL|ALT" })) },
	{ key = "4", mods = "CTRL|ALT", action = herdr_or_wezterm("\x02\x1b4", act.SendKey({ key = "4", mods = "CTRL|ALT" })) },
	{ key = "5", mods = "CTRL|ALT", action = herdr_or_wezterm("\x02\x1b5", act.SendKey({ key = "5", mods = "CTRL|ALT" })) },
	{ key = "6", mods = "CTRL|ALT", action = herdr_or_wezterm("\x02\x1b6", act.SendKey({ key = "6", mods = "CTRL|ALT" })) },
	{ key = "7", mods = "CTRL|ALT", action = herdr_or_wezterm("\x02\x1b7", act.SendKey({ key = "7", mods = "CTRL|ALT" })) },
	{ key = "8", mods = "CTRL|ALT", action = herdr_or_wezterm("\x02\x1b8", act.SendKey({ key = "8", mods = "CTRL|ALT" })) },
	{ key = "9", mods = "CTRL|ALT", action = herdr_or_wezterm("\x02\x1b9", act.SendKey({ key = "9", mods = "CTRL|ALT" })) },
	{
		key = "h",
		mods = "CTRL|ALT",
		action = herdr_or_wezterm("\x02\x1bh", act.SendKey({ key = "h", mods = "CTRL|ALT" })),
	},
	{
		key = "l",
		mods = "CTRL|ALT",
		action = herdr_or_wezterm("\x02\x1bl", act.SendKey({ key = "l", mods = "CTRL|ALT" })),
	},

	-- Cmd+Arrow for start/end of line
	{ key = "LeftArrow", mods = "SUPER", action = act.SendString("\x01") },
	{ key = "RightArrow", mods = "SUPER", action = act.SendString("\x05") },

	-- Cmd+Delete to kill whole line from cursor
	{ key = "Backspace", mods = "SUPER", action = act.SendString("\x15") },

	-- Alt+Arrow for pane/tab navigation
	{
		key = "LeftArrow",
		mods = "ALT",
		action = herdr_or_wezterm("\x02h", navigate_pane_or_tab("Left")),
	},
	{
		key = "RightArrow",
		mods = "ALT",
		action = herdr_or_wezterm("\x02l", navigate_pane_or_tab("Right")),
	},
	{
		key = "h",
		mods = "ALT",
		action = herdr_or_wezterm("\x02h", navigate_pane_or_tab("Left")),
	},
	{
		key = "l",
		mods = "ALT",
		action = herdr_or_wezterm("\x02l", navigate_pane_or_tab("Right")),
	},

	-- Ctrl+h/l for word navigation
	{ key = "h", mods = "CTRL", action = act.SendString("\x1bb") },
	{ key = "l", mods = "CTRL", action = act.SendString("\x1bf") },
	{
		key = "DownArrow",
		mods = "ALT",
		action = herdr_or_wezterm("\x02j", act.ActivatePaneDirection("Down")),
	},
	{
		key = "UpArrow",
		mods = "ALT",
		action = herdr_or_wezterm("\x02k", act.ActivatePaneDirection("Up")),
	},

	{
		key = "RightArrow",
		mods = "SUPER|ALT",
		action = herdr_or_wezterm("\x02v", act.SplitHorizontal({ domain = "CurrentPaneDomain" })),
	},
	{
		key = "DownArrow",
		mods = "SUPER|ALT",
		action = herdr_or_wezterm("\x02-", act.SplitVertical({ domain = "CurrentPaneDomain" })),
	},
	{
		key = "x",
		mods = "SUPER|ALT",
		action = herdr_or_wezterm("\x02x", act.CloseCurrentPane({ confirm = true })),
	},
	{
		key = "k",
		mods = "SUPER",
		action = herdr_or_wezterm(
			"\x0c",
			act.Multiple({
				act.ClearScrollback("ScrollbackAndViewport"),
				act.SendKey({ key = "L", mods = "CTRL" }),
			})
		),
	},
	{ key = "L", mods = "SHIFT|CTRL", action = act.ShowDebugOverlay },
	{ key = "P", mods = "SHIFT|CTRL", action = act.ActivateCommandPalette },
	{ key = "R", mods = "SHIFT|CTRL", action = act.ReloadConfiguration },

	{ key = "X", mods = "CTRL", action = act.ActivateCopyMode },
	{ key = "f", mods = "SUPER", action = act.Search("CurrentSelectionOrEmptyString") },
	{ key = "v", mods = "SUPER", action = act.PasteFrom("Clipboard") },
	{ key = "w", mods = "SUPER", action = act.CloseCurrentTab({ confirm = true }) },
	{ key = "x", mods = "SHIFT|CTRL", action = act.ActivateCopyMode },

	{ key = "LeftArrow", mods = "SHIFT|ALT|CTRL", action = act.AdjustPaneSize({ "Left", 1 }) },
	{ key = "RightArrow", mods = "SHIFT|ALT|CTRL", action = act.AdjustPaneSize({ "Right", 1 }) },
	{ key = "UpArrow", mods = "SHIFT|ALT|CTRL", action = act.AdjustPaneSize({ "Up", 1 }) },
	{ key = "DownArrow", mods = "SHIFT|ALT|CTRL", action = act.AdjustPaneSize({ "Down", 1 }) },

	-- Rotate panes
	{ key = "{", mods = "CTRL|SHIFT", action = act.RotatePanes("CounterClockwise") },
	{ key = "}", mods = "CTRL|SHIFT", action = act.RotatePanes("Clockwise") },

	-- Swap pane in direction
	{ key = "LeftArrow", mods = "SUPER|SHIFT", action = swap_pane("Left") },
	{ key = "RightArrow", mods = "SUPER|SHIFT", action = swap_pane("Right") },
	{ key = "UpArrow", mods = "SUPER|SHIFT", action = swap_pane("Up") },
	{ key = "DownArrow", mods = "SUPER|SHIFT", action = swap_pane("Down") },
}

wezterm.on("user-var-changed", function(window, pane, name, value)
	wezterm.log_info("user-var-changed fired: " .. name .. " = " .. value)
	if name == "claude_status" then
		local vars = pane:get_user_vars()
		local project = vars.claude_project or "unknown"
		window:toast_notification("Claude Code", project .. " — " .. value, nil, 5000)
	end
end)

-- and finally, return the configuration to wezterm
return config
