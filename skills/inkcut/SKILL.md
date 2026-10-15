---
name: inkcut
description: Prepare local outlined SVG artwork as sized copies in Inkcut, inspect the active job, and verify imports using inkcutctl. Use for one-off signs or repeated artwork from any workflow. Does not dispatch cuts.
---

# Inkcut preparation

Discover `inkcutctl --help` and `inkcutctl prepare --help`, then inspect
`inkcutctl status --json`. This skill requires the Inkcut Automation plugin;
upstream `inkcut open` is not its acknowledged import API. If unavailable, report
the missing CLI/plugin or stopped app instead of issuing guessed GUI commands.

Use the supplied local SVG. A requested size such as “3-inch copies” means
per-copy artwork width, with aspect ratio preserved. State that interpretation
when it matters. Read the current usable material width from status; use an
explicit width if supplied. Ask when physical material width is unknown rather
than inventing it. Default spacing is 0.25 inches, and packing is rows with no
rotation or mirroring. Requests needing nesting, weed borders, or other unsupported
features need a separate reviewed artwork preparation step.

Generate and retain one UUID per deliberate operation. Run `prepare` with
`--width`, `--copies`, explicit material width when known, and `--dry-run --json`.
Check per-copy dimensions, exact count, row layout, material fit, and feed length.
A dry run does not modify the open job. Preserve source files; if unsupported SVG
content is rejected, convert to outlined plain SVG in a separate file and review
it. Never silently discard text, images, or unsupported elements.

Publish by repeating the same inputs without `--dry-run`. If a document is open,
inspect it and use `--expected-revision` only when replacement is authorized by
the task. User edits or restart invalidate a revision. Honor existing authorization;
do not ask again merely because the operation is automated.

Keep the exact publication command/key and JSON receipt. On uncertain transport
or publication, inspect status and retry the identical command/key. A successful
retry returns a historical receipt, so inspect current status afterward. A changed
input needs a deliberate new operation, not a retry disguised by a new UUID.

Use `load` for a reviewed SVG that should keep its source scale and one copy.
Use `prepare` for sizing and duplication. Both preserve the original SVG.

Completion evidence is the acknowledged source hash, per-copy width/height,
copy count, fit/feed length, and current document revision. Inspect the Inkcut
preview when available, especially for a new source format. Report the distinction
between verified digital geometry and a physical cut. Cutter connection, motion,
and successful physical completion are not provided by this tool.
