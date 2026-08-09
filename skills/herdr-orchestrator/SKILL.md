---
name: herdr-orchestrator
description: "Launch and coordinate visible Codex agents through Herdr panes and worktree-backed workspaces. Use when the user explicitly asks to orchestrate, delegate, or parallelize work through Herdr. Requires HERDR_ENV=1."
---

# Herdr Orchestrator

Use Herdr as the visible execution substrate for the orchestration described by
the user's prompt. Keep the calling pane available as the coordinator unless
the prompt explicitly assigns a different topology.

Load and follow the `herdr:herdr` skill for current CLI discovery, pane and
workspace control, worktree setup, agent-status semantics, focus preservation,
and cleanup safety. The installed `herdr` binary remains the syntax authority.

This skill does not choose how orchestration is expressed. Do not add, remove,
or reinterpret delegation layers, worker prompts, skill invocations, task
ownership, integration responsibilities, or validation steps supplied by the
user. A worker prompt is opaque task input: submit it verbatim, including
prompts that invoke `$orchestrator`, other skills, or their own sub-agents.

## Run the requested topology

1. Before any `herdr` command, run:

   ```bash
   test "${HERDR_ENV:-}" = 1
   ```

   If this fails, explain that the skill must run inside Herdr and stop. Do not
   inspect or control a focused Herdr session from outside it.

2. Use `herdr:herdr` to learn the installed syntax. Capture
   `herdr pane current --current` and store the returned pane ID separately as
   the coordinator pane. Treat every returned ID as opaque.

3. Create the panes, tabs, workspaces, or worktree-backed workspaces requested
   by the prompt. Herdr can parallelize work within one checkout, across
   isolated worktrees in one repository, or across multiple repositories.
   Use `herdr worktree create` or `herdr worktree open` whenever the requested
   topology includes Git worktrees; never create an invisible raw worktree.

4. Record every resource created by this orchestration and the returned pane
   used to control it. Never add the coordinator pane to the worker-resource
   ledger.

5. Start each requested Codex worker in its returned pane with:

   ```bash
   herdr pane run <pane-id> "codex --dangerously-bypass-approvals-and-sandbox"
   herdr pane get <pane-id>
   herdr wait agent-status <pane-id> --status idle --timeout 30000
   ```

6. Submit the worker prompt exactly as provided. Quote it safely so shell
   expansion does not consume `$skill` invocations or alter other prompt text:

   ```bash
   herdr pane run <pane-id> '<verbatim worker prompt>'
   herdr wait agent-status <pane-id> --status working --timeout 30000
   ```

7. Monitor workers through their explicit pane IDs. Inspect current status and
   recent unwrapped output before waiting. On timeout or `blocked`, read the
   transcript and apply only the follow-up behavior requested by the prompt.

8. Report the created topology, worker status, and results requested by the
   prompt. Preserve the calling pane and all unrelated Herdr resources.

## Resource safety

- Use `--no-focus`, `--current`, or explicit opaque IDs as directed by
  `herdr:herdr`.
- Never close the coordinator pane or a resource this orchestration did not
  create.
- Close created worker panes only when the prompt's requested lifecycle calls
  for it.
- Do not remove a worktree checkout merely because its worker completed.
- Use `herdr worktree remove` only when the user explicitly requests cleanup
  and the checkout is safe to delete.
- Never stop the Herdr server or kill the main Herdr process.
