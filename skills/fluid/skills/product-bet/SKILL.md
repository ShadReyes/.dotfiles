---
name: product-bet
description: Guide a Fluid product problem or feature idea through intake, evidence, shaping, and a ready-to-bet decision, storing each bet as a shared Linear Document.
user-invocable: true
---

# Product Bet

Guide one product problem through:

```text
Intake -> Problem framed -> Gathering evidence -> Shaped -> Ready to bet
```

Each bet is one Linear Document. The document's completed sections are the
state; do not skip gates without recording that the gate was overridden.

## Fluid Linear integration

Use the bundled direct GraphQL script, not Linear MCP tools:

```bash
node <skill-dir>/scripts/linear.mjs <command> [options]
```

The script is locked to Fluid Commerce and reads `LINEAR_API_KEY` from
`~/.config/linear/workspaces/fluid.env` through the shared Fluid GraphQL
transport. It supports `whoami`, `list-teams`, `list-projects`,
`save-project`, `list-docs`, `get-doc`, and `save-doc`.

For document bodies, write Markdown to a temporary file and pass
`--content-file`; do not inline multiline content in command arguments.

## Where bets live

Each bet gets its own problem-named Project. The Project is created on the
`Current` team and attached to the `Admin & Dev Ex` Initiative by default.
Use another Initiative only when the user explicitly requests it.

The bet's Linear Document is attached to that same Project. Do not create a
shared `Product Bets` Project and do not create a second delivery Project later.

Do not infer Initiative membership from the bet owner or assignee. Initiatives
are organizational context, not delivery ownership.

## Document anatomy

Create documents titled `Bet: <problem-named title>` with this structure:

```md
**Stage:** Intake | Problem framed | Gathering evidence | Shaped | Ready to bet | Won -> <project> | Passed (not bet on)
**Updated:** <date>

## One-pager
**Problem:** ... **Evidence:** ... **Who:** ... **Why now:** ...
**What success would look like:** <metric + direction, no target/solution/date>
*Not yet decided: the solution.*

## Evidence log
- <date> - <source: interview/data/tickets> - <finding, with numbers/quotes>

## Shaped pitch
**Appetite:** ... **Solution sketch:** ... **Success metric:** <metric, target, cohort, window>
**Rabbit holes:** ... **No-gos:** ...

## Decision
<prioritization date, outcome, or why passed>
```

## Start a new bet

1. Reframe feature requests into customer behavior. Ask what the customer
   cannot do and why it matters; do not create a bet around a solution name.
2. Draft the one-pager with the user. Run every one-pager lint check in
   `REFERENCE.md` and show pass/fail.
3. Propose a concise, problem-named Project title and get confirmation before
   creating the Project.
4. Create that Project on `Current`, attaching it to `Admin & Dev Ex` by
   default. Use `save-project --name ... --team Current` and override the
   Initiative only when explicitly requested.
5. Create the Document on the new Project at stage `Problem framed`, or `Intake` when evidence is
   still thin.
6. Tell the user when the Project and Document are team-visible.

## Advance a bet

1. Find the bet Document with `list-docs --query "Bet:"`, then use its linked
   Project for all subsequent reads and updates.
2. Read it with `get-doc` and identify the next empty or weak section.
3. Apply the corresponding gate from `REFERENCE.md`.
4. Update the document content and bump both `Stage` and `Updated`.

Evidence entries require a date, source, and number or verbatim quote. Shaping
requires a passing one-pager and at least two independent evidence types.
Ready-to-bet requires appetite, solution sketch, cheapest solution test, metric,
rabbit holes, no-gos, and measurable instrumentation.

## Graduation and passing

When a bet wins, the existing bet Project becomes the delivery Project:

1. Keep the same Project and Initiative; do not create another Project.
2. Slice implementation issues into that Project using the current
   Project-based `linear-create` workflow.
3. Link the bet Document from each implementation issue description and carry
   the relevant discovery constraints, evidence, and acceptance criteria into
   the issue body. The Document is supporting context; issue descriptions are
   the implementation contract.
4. Update the bet stage to `Won -> <same project>`.

When a bet is rejected, update it to `Passed (not bet on)` with a concise reason
in `Decision`. Passing is a valid outcome and is preferable to leaving stale
uncertainty in the table.

## Open-bet review

List all `Bet:` documents and flag any not updated in three or more weeks.
Recommend one of: an evidence task, a shaping session, or an explicit pass.

## Fallback

If Linear is unavailable, keep the same document at `./bets/<slug>.md` and say
that it is local-only. Offer to publish it once the API credential or network is
available.

Use terse, operational language. When a gate fails, push back once and explain
the rationale from `REFERENCE.md`; if the user overrides it, record
`(gate overridden)` beside the stage.
