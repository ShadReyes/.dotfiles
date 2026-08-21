local parsers = {
	"bash",
	"c",
	"css",
	"csv",
	"dockerfile",
	"hoon",
	"html",
	"javascript",
	"json",
	"kdl",
	"lua",
	"markdown",
	"nix",
	"prisma",
	"python",
	"rust",
	"sql",
	"svelte",
	"typescript",
	"vim",
	"vimdoc",
	"yaml",
}

return {
	"nvim-treesitter/nvim-treesitter",
	branch = "main",
	lazy = false,
	build = ":TSUpdate",
	dependencies = {
		{
			"nvim-treesitter/nvim-treesitter-textobjects",
			branch = "main",
		},
	},
	config = function()
		local treesitter = require("nvim-treesitter")

		treesitter.setup()
		treesitter.install(parsers)

		vim.api.nvim_create_autocmd("FileType", {
			desc = "Enable Treesitter highlighting when a parser is available",
			group = vim.api.nvim_create_augroup("treesitter-highlight", { clear = true }),
			callback = function(event)
				pcall(vim.treesitter.start, event.buf)
			end,
		})

		vim.keymap.set({ "n", "x" }, "<C-Space>", function()
			vim.treesitter.select("parent")
		end, { desc = "Expand Treesitter selection" })
		vim.keymap.set("x", "<BS>", function()
			vim.treesitter.select("child")
		end, { desc = "Shrink Treesitter selection" })

		require("nvim-treesitter-textobjects").setup({
			move = { set_jumps = true },
		})

		local move = require("nvim-treesitter-textobjects.move")
		local function set_move(key, callback, capture, description)
			vim.keymap.set({ "n", "x", "o" }, key, function()
				callback(capture, "textobjects")
			end, { desc = description })
		end

		set_move("]f", move.goto_next_start, "@function.outer", "Next function start")
		set_move("]c", move.goto_next_start, "@class.outer", "Next class start")
		set_move("]a", move.goto_next_start, "@parameter.inner", "Next parameter start")
		set_move("]F", move.goto_next_end, "@function.outer", "Next function end")
		set_move("]C", move.goto_next_end, "@class.outer", "Next class end")
		set_move("]A", move.goto_next_end, "@parameter.inner", "Next parameter end")
		set_move("[f", move.goto_previous_start, "@function.outer", "Previous function start")
		set_move("[c", move.goto_previous_start, "@class.outer", "Previous class start")
		set_move("[a", move.goto_previous_start, "@parameter.inner", "Previous parameter start")
		set_move("[F", move.goto_previous_end, "@function.outer", "Previous function end")
		set_move("[C", move.goto_previous_end, "@class.outer", "Previous class end")
		set_move("[A", move.goto_previous_end, "@parameter.inner", "Previous parameter end")
	end,
}
