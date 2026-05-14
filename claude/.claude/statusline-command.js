#!/usr/bin/env node
"use strict";

const { execFileSync } = require("child_process");

let input = {};
try {
  input = JSON.parse(require("fs").readFileSync("/dev/stdin", "utf8"));
} catch (_) {}

const cwd = (input.workspace && input.workspace.current_dir) || process.cwd();
const repo = require("path").basename(cwd);
const model = (input.model && input.model.display_name) || "unknown";

function humanize(n) {
  if (n < 1_000) return String(n);
  if (n < 1_000_000) return (n / 1_000).toFixed(1) + "k";
  return (n / 1_000_000).toFixed(1) + "M";
}

// Worktrees
let worktrees = [];
try {
  const stdout = execFileSync("git", ["-C", cwd, "worktree", "list", "--porcelain"], {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "ignore"],
  });

  const paths = [...stdout.matchAll(/^worktree (.+)/gm)]
    .map((m) => m[1])
    .filter((p) => require("path").basename(p) !== ".bare");

  worktrees = paths.map((p) => {
    let name = require("path").basename(p);
    if (name.includes("@")) name = name.split("@").slice(1).join("@");

    let dirty = false;
    try {
      execFileSync("git", ["-C", p, "diff", "--quiet", "HEAD"], {
        stdio: ["ignore", "ignore", "ignore"],
      });
    } catch (_) {
      dirty = true;
    }

    const display = name.length > 18 ? "\u2026" + name.slice(-18) : name;
    return dirty ? display + "*" : display;
  });

  worktrees.sort((a, b) => {
    const mainNames = ["main", "main*", "master", "master*"];
    return (mainNames.includes(a) ? 0 : 1) - (mainNames.includes(b) ? 0 : 1);
  });
} catch (_) {}

// Context usage
const used = parseFloat((input.context_window && input.context_window.used_percentage) || 0);
const totalIn = (input.context_window && input.context_window.total_input_tokens) || 0;
const totalOut = (input.context_window && input.context_window.total_output_tokens) || 0;

// Progress bar
const barWidth = 10;
const filled = Math.min(barWidth, Math.max(0, Math.round((used * barWidth) / 100)));
const bar = "\u2588".repeat(filled) + "\u2591".repeat(barWidth - filled);

// Colors (ANSI)
const cyan = "\x1b[36m";
const dim = "\x1b[2m";
const reset = "\x1b[0m";
const barColor = used < 60 ? "\x1b[32m" : used < 85 ? "\x1b[33m" : "\x1b[31m";

const line1 =
  `${cyan}[${repo}]${reset} ${barColor}${bar}${reset} ${dim}${used.toFixed(1)}%${reset}` +
  ` \u2502 ${dim}${humanize(totalIn)} in / ${humanize(totalOut)} out${reset}` +
  ` \u2502 ${dim}${model}${reset}`;

const line2 = `${dim}${worktrees.join("  ")}${reset}`;

try {
  process.stdout.write(`${line1}\n${line2}`);
} catch (_) {
  process.exit(0);
}
