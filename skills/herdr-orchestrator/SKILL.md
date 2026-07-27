---
name: herdr-orchestrator
description: "Orchestrate delegated Codex work in visible Herdr panes while keeping the calling pane as coordinator. Use when the user explicitly asks to orchestrate, delegate, or run sub-agents through Herdr so their progress is visible in the terminal UI. Requires HERDR_ENV=1."
---

# Herdr Orchestrator

Keep the calling pane as the orchestrator. Create every worker as an interactive Codex session in a sibling Herdr pane so the user can watch progress. Do not also create invisible collaboration sub-agents for the same work.

## Orchestrate

1. Run this as the first command, before any `herdr` command:

   ```bash
   test "${HERDR_ENV:-}" = 1
   ```

   If this fails, explain that the skill must run inside Herdr and stop. Do not run even read-only Herdr discovery, fall back to hidden workers, or control the focused Herdr session from outside it.

2. Learn the installed syntax with `herdr --help` and `herdr pane`. Capture the parent with `herdr pane current --current` and store its pane ID separately as the orchestrator pane. Never add that ID to the worker ledger or pass it to a close command. Treat every returned ID as opaque.

3. Split the objective into bounded tasks with non-overlapping ownership. Keep integration, conflict resolution, and final delivery in the parent pane. Default workers to the current tab and working directory; create another tab, workspace, worktree, or cwd only when the user requests it.

4. Create one sibling pane per worker. Inspect the parent rectangle with:

   ```bash
   herdr pane layout --pane "$HERDR_PANE_ID"
   ```

   Split a wide pane right and a narrow or tall pane down. Re-check geometry before additional splits and avoid unusably small panes. Preserve the user's focus:

   ```bash
   herdr pane split --current --direction right --no-focus
   ```

   Read `result.pane.pane_id` from the JSON response. Rename the pane for its responsibility.

5. Launch and brief the worker:

   ```bash
   herdr pane rename <pane-id> "<responsibility>"
   herdr pane run <pane-id> "codex"
   herdr pane get <pane-id>
   herdr wait agent-status <pane-id> --status idle --timeout 30000
   herdr pane run <pane-id> "<bounded task and all context the independent session needs>"
   herdr wait agent-status <pane-id> --status working --timeout 30000
   ```

   Give editing workers exclusive files or modules. Tell each worker that other agents share the repository, not to revert others' changes, and to report its summary, files, tests, and blockers.

6. Track a small ledger in the parent context: pane ID, responsibility, owned scope, status, and expected result. Monitor with explicit IDs:

   ```bash
   herdr pane get <pane-id>
   herdr pane read <pane-id> --source recent-unwrapped --lines 120
   ```

   Read existing output before waiting. Background completion normally becomes `done`; a pane visible to the user may return to `idle`. Treat either as complete only after inspecting status and transcript.

7. On timeout, inspect the pane before acting. Send a precise follow-up with `herdr pane run` when a worker is blocked or incomplete. Synthesize and validate all results from the parent pane.

8. After capturing and integrating a completed worker's final result, verify that its pane ID is in the worker ledger and differs from the stored orchestrator pane ID. Then close it automatically and mark it closed:

   ```bash
   herdr pane close <worker-pane-id>
   ```

   Keep blocked or incomplete workers open until their work is resolved. Before final delivery, close every completed worker pane created by this orchestration.

## Preserve the session

- Use `--no-focus`, `--current`, or explicit IDs.
- Parse IDs from command responses; never construct or infer them.
- Close only worker panes recorded as created by this orchestration.
- Never close the calling orchestrator pane, even if it reports `idle` or `done`.
- Do not close panes or other resources that this orchestration did not create.
- Never stop the Herdr server or kill the main Herdr process.
