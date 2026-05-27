#!/usr/bin/env python3
"""Convert a TOML agent definition to Claude Code markdown format.

Usage: toml2claude.py <input.toml> <output.md>

Reads a canonical TOML agent file and writes Claude Code's expected
markdown-with-YAML-frontmatter format. Claude-only fields (model, color)
are read from the [claude] table if present.
"""

import sys
import tomllib
from pathlib import Path


def convert(toml_path: str, md_path: str) -> None:
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)

    name = data["name"]
    description = data["description"]
    instructions = data.get("developer_instructions", "").strip()
    claude = data.get("claude", {})

    lines = ["---"]
    lines.append(f"name: {name}")
    lines.append(f"description: {description}")
    if "model" in claude:
        lines.append(f"model: {claude['model']}")
    if "color" in claude:
        lines.append(f"color: {claude['color']}")
    lines.append("---")
    lines.append("")
    lines.append(instructions)
    lines.append("")

    Path(md_path).write_text("\n".join(lines))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.toml> <output.md>", file=sys.stderr)
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
