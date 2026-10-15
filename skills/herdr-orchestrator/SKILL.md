---
name: herdr-orchestrator
description: "Launch and coordinate coding agents through Herdr panes and worktree-backed workspaces. Use when the user explicitly asks to orchestrate, delegate, or parallelize work through Herdr. Requires HERDR_ENV=1."
---

# Herdr Orchestrator

Use Herdr as the visible execution substrate for the orchestration described by
the user's prompt. Keep the calling pane available as the coordinator unless
the prompt explicitly assigns a different topology.

Load and follow the `herdr:herdr` skill for current CLI discovery, pane and
workspace control, worktree setup, agent-status semantics, focus preservation,
and cleanup safety. The installed `herdr` binary remains the syntax authority.
Do not reproduce executable Herdr CLI examples here; describe the orchestration
outcome and use the procedures from `herdr:herdr`.

This skill does not choose how orchestration is expressed. Do not add, remove,
or reinterpret delegation layers, worker prompts, skill invocations, task
ownership, integration responsibilities, or validation steps supplied by the
user. A worker prompt is opaque task input: submit it verbatim, including
prompts that invoke `$orchestrator`, other skills, or their own sub-agents.

## Run the requested topology

1. Before any Herdr command, use `herdr:herdr` to verify the environment and
   learn the installed syntax. If its environment check fails, stop as directed
   by that skill.

2. Use the caller-validation procedure from `herdr:herdr` and store the
   verified pane, tab, and workspace IDs separately as coordinator context.
   Resolve any caller ambiguity before creating resources. Treat every ID as
   opaque.

3. Create the panes, tabs, workspaces, or worktree-backed workspaces requested
   by the prompt. Herdr can parallelize work within one checkout, across
   isolated worktrees in one repository, or across multiple repositories.
   Use the worktree create or open procedure from `herdr:herdr` whenever the
   requested topology includes Git worktrees; never create an invisible raw
   worktree.

4. Verify each created resource's destination through `herdr:herdr` before
   starting workers. Record every resource and the returned pane used to
   control it. Never add the coordinator pane to the worker-resource ledger.

5. Give each requested worker a useful unique agent name. Start it through the
   agent-start procedure in `herdr:herdr`, using the returned pane, an available
   agent kind selected from `herdr agent start --help`, honoring the user's
   requested harness. Apply the worker-permissions rules below to every launch,
   including retries and replacement workers. Record the live agent name,
   hosting pane ID, and permission arguments used.

6. Verify the launch arguments select the intended permission mode before
   dispatch. If startup output reports a different mode, resolve the mismatch
   before sending work. Submit the worker prompt exactly as provided through
   the agent-prompt procedure in `herdr:herdr`. Pass the full prompt as one text
   argument so shell expansion does not consume `$skill` invocations or alter
   other prompt text.

7. Monitor workers through their unique agent names or explicit hosting pane
   IDs, using the agent status, wait, and read procedures from `herdr:herdr`.
   On timeout or `blocked`, inspect the agent and apply only the follow-up
   behavior requested by the prompt.

8. Report the created topology, worker status, and results requested by the
   prompt. Preserve the calling pane and all unrelated Herdr resources.

## Worker permissions

Default workers launched by this orchestrator to permission-bypass mode
unless the user explicitly requests a restricted mode. Set the mode through
native agent launch arguments, passed after Herdr's `--` separator. A worker
prompt is not a permission setting. Do not assume workers inherit the
coordinator's permission mode or shell aliases.

For each selected harness, read its installed executable's help and identify
the exact native flags that activate permission bypass. Use the canonical
executable with those explicit flags, not a shell alias or flags copied from
another harness. Distinguish flags that activate bypass from flags that only
make it available. If approval prompts and sandbox restrictions have separate
controls, select both explicitly; suppressing prompts alone does not establish
unrestricted execution.

If the harness has no permission gate or sandbox by design, verify that
behavior before omitting bypass flags. If you cannot establish how to select
the requested mode, report that limitation before dispatch instead of silently
launching with unknown permissions.

Honor explicit user permission settings and enforced platform restrictions.
Bypass mode does not expand the worker's task scope.

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
