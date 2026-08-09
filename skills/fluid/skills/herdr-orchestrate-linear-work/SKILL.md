---
name: herdr-orchestrate-linear-work
description: Coordinate an approved batch of Fluid Current-team Linear issues through visible Herdr worktree workspaces, with separate preparation and implementation phases and fresh agent conversations between them. Use after work selection when the user asks Herdr to prepare or implement one or more issues in parallel while preserving their worktrees for the next phase.
---

# Herdr-orchestrate Fluid Linear work

Run exactly one phase per invocation: `Prepare` or `Implement`. Infer the phase
only when it is explicit; otherwise ask which phase to run. Never continue from
preparation into implementation in one conversation.

Require `HERDR_ENV=1`. Read and follow `herdr-orchestrator`, which in turn owns
current Herdr CLI discovery and control semantics. This skill supplies the
Fluid-specific topology and worker lifecycle; do not duplicate or override the
generic Herdr instructions.

## Shared contract

Require an approved issue set with one Current-team issue ID or URL per worker
and a repository mapping for each issue. Preserve the calling pane as the
coordinator and resolve every workspace, worktree, and pane through Herdr.
Never infer or carry opaque IDs between invocations.

Maintain a resource ledger mapping each issue to its source workspace,
worktree-backed workspace, path, branch, phase-specific worker pane, and plan
path. Preserve all unrelated resources. Do not mutate Linear, commit, push,
open pull requests, remove worktrees, or close preparation panes unless the
user explicitly requests that named action.

Use one persistent issue worktree and branch across preparation and
implementation. Follow a user-supplied or repository branch convention and do
not add a phase suffix such as `-prepare`. Stop when an issue-to-repository
mapping is ambiguous or one issue requires an unapproved multi-repository
topology.

## Prepare

1. Confirm that the approved batch remains parallel-safe and has no unresolved
   decision that prevents useful preparation.
2. Resolve each source repository workspace and its local default branch
   through Herdr. Create one visible worktree-backed workspace per issue without
   moving focus from the coordinator.
3. Launch a Codex preparation worker in each returned worktree pane as directed
   by `herdr-orchestrator`.
4. Submit this worker prompt with the issue ID substituted, preserving the
   skill invocations literally:

   ```text
   $orchestrator $fluid:work-linear-issue Prepare <issue-id>
   ```

5. Monitor all workers through their explicit pane IDs. Collect each issue URL,
   blocker result, plan path, proposed decomposition, unresolved decisions, and
   reported repository boundary.
6. Compare completed plans against every shared contract from the approved
   proposal and every cross-issue dependency discovered during preparation.
   Use bounded worker follow-ups to resolve evidence-backed technical
   discrepancies. Ask the user about material product choices; do not invent
   agreement.
7. Stop without implementing. Preserve the issue worktrees, branches, plans,
   and preparation panes.

### Preparation handoff

Finish with a self-contained prompt for a new coordinator conversation. The
prompt must invoke `$fluid:herdr-orchestrate-linear-work Implement` and include:

- every issue ID and URL;
- source workspace name, worktree workspace label and path, and branch;
- approved plan path and blocker result;
- concurrency waves and blocking order;
- reconciled shared-contract decisions;
- unresolved decisions, which must be empty before recommending implementation;
- instructions to rediscover current Herdr IDs, reuse the existing worktrees,
  and create fresh implementation panes rather than continuing preparation
  conversations.

Present the prompt in one copyable fenced block. Do not submit it automatically.

## Implement

1. Require the self-contained preparation handoff, an approved plan for every
   issue, no active blockers, and no unresolved material cross-issue decision.
2. Rediscover each existing worktree-backed workspace by its recorded path and
   verify its repository, branch, working-tree state, and plan path. Do not
   silently create a replacement checkout when one is missing or mismatched.
3. Create a fresh pane and launch a new Codex process inside each existing
   issue worktree. Never reuse a preparation worker pane, continue its agent
   conversation, or send it an implementation follow-up.
4. Submit this worker prompt with the issue ID and plan path substituted,
   preserving the skill invocations literally:

   ```text
   $orchestrator $fluid:work-linear-issue Implement <issue-id> using the approved plan at <plan-path>
   ```

5. Monitor workers through the new pane IDs. On completion, collect changed
   files, verification results, satisfied and remaining acceptance criteria,
   blockers, and residual risks.
6. Check the worker reports against the reconciled shared contracts and flag
   integration conflicts before recommending shipping.

Report the final resource ledger and results. Preserve all worktrees and agent
panes unless the user explicitly requests cleanup. Use `fluid:ship-pr`
separately when the user authorizes commit, push, pull-request creation, and
review iteration.
