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

Use one standing Project named `Product Bets` per team. A bet is a Document on
that Project, not a Project of its own.

When `Product Bets` does not exist:

1. Tell the user it is missing.
2. Ask for confirmation before creating it.
3. Create it on the `Current` team.
4. Attach it to the `Admin & Dev Ex` Initiative by default.
5. Use another Initiative only when the user explicitly requests it.

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
3. Confirm the standing `Product Bets` Project exists, creating it only after
   user confirmation.
4. Create the document at stage `Problem framed`, or `Intake` when evidence is
   still thin.
5. Tell the user when the document is team-visible.

## Advance a bet

1. Find the document with `list-docs --project "Product Bets" --query "Bet:"`.
2. Read it with `get-doc` and identify the next empty or weak section.
3. Apply the corresponding gate from `REFERENCE.md`.
4. Update the document content and bump both `Stage` and `Updated`.

Evidence entries require a date, source, and number or verbatim quote. Shaping
requires a passing one-pager and at least two independent evidence types.
Ready-to-bet requires appetite, solution sketch, cheapest solution test, metric,
rabbit holes, no-gos, and measurable instrumentation.

## Graduation and passing

When a bet wins:

1. Create or identify the real delivery Project using `linear-create`.
2. Default the delivery Project to `Admin & Dev Ex` unless another Initiative
   is explicitly requested.
3. Link the bet document from the Project description.
4. Slice delivery issues using the current Project-based issue workflow.
5. Update the bet stage to `Won -> <project>`.

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
