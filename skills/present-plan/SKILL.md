---
name: present-plan
description: Convert implementation plans, product plans, technical proposals, roadmaps, PRDs, ADR drafts, or planning notes into polished, standalone HTML briefings. Use when the user asks to make a plan presentable, explain plan choices and tradeoffs, create an executive or technical plan brief, turn a plan into an HTML document, or produce a shareable artifact for stakeholders.
---

The user has asked you to turn a plan into a presentable HTML document. Treat the output as a durable planning artifact: it should explain the plan, the reasoning behind it, the tradeoffs, and the decisions still in motion.

## Plan Brief Workspace

Use the current directory as the workspace unless the user specifies another location.

- `./plan-briefs/*.html`: Final presentation documents. Name files `0001-<dash-case-title>.html`, incrementing the number each time.
- `./assets/*`: Reusable components shared across plan briefs. Before authoring a brief, inspect this directory and reuse existing styles or components.
- `./assets/plan-brief.css`: Default shared stylesheet. If the workspace does not already have a suitable stylesheet, copy this skill's `assets/plan-brief.css` into the workspace and link to it from the HTML.

Do not create auxiliary documentation unless the user asks for it. The HTML brief is the primary output.

## Workflow

1. Gather the source plan.
   - Read the plan from the prompt, attached text, referenced file, issue, PRD, or local planning document.
   - If the plan depends on repository context, inspect the relevant files before writing.
   - Ask a concise clarifying question only when the intended audience, decision, or source plan is missing and cannot be inferred safely.

2. Extract the planning structure.
   - Identify the goal, audience, scope, non-goals, phases, milestones, dependencies, risks, validation strategy, and open questions.
   - Separate settled decisions from assumptions and unresolved options.
   - Surface implicit tradeoffs that are present in the plan but not clearly named.

3. Choose the brief shape.
   - Default to a stakeholder-ready technical brief for mixed product and engineering readers.
   - Bias toward an executive brief when the user mentions leadership, clients, fundraising, or nontechnical stakeholders.
   - Bias toward an implementation brief when the user mentions engineers, architecture, tickets, Linear, GitHub, rollout, or delivery planning.

4. Write the HTML document.
   - Make the document standalone enough that a reader can understand it without seeing the original raw plan.
   - Preserve the plan's substance, but rewrite for clarity, sequencing, and decision quality.
   - Use clear headings, comparison tables, timelines, callouts, and concise prose.
   - Include links to source files, issues, PRs, docs, or external references when available.
   - Avoid marketing copy, filler, and generic claims.

5. Validate the artifact.
   - Ensure relative links resolve from the HTML file's location.
   - Open the HTML file when possible and inspect it for layout problems.
   - Check that the document prints well: no dark full-page backgrounds, no clipped tables, and sensible page breaks.

## Recommended Sections

Use only the sections that fit the plan.

- Title and metadata: plan name, status, author/date if known, intended audience.
- Executive summary: one short paragraph naming the outcome and why it matters.
- Context: the problem, constraints, and current state.
- Objectives and non-goals: what success means and what is intentionally out of scope.
- Plan at a glance: phases, milestones, owners, and validation checkpoints.
- Implementation path: the actual sequence of work, with expected outputs per phase.
- Key choices: decisions made, rationale, alternatives considered, and why they were not chosen.
- Tradeoffs: costs, benefits, reversibility, operational burden, UX impact, delivery risk.
- Risks and mitigations: what could go wrong and how the plan reduces or detects it.
- Dependencies: teams, systems, approvals, data, infrastructure, or unresolved questions.
- Testing and rollout: how the plan will be verified, released, monitored, and rolled back.
- Open questions: items that require a decision before or during execution.
- Next actions: a short checklist of concrete follow-ups.

## Design Standards

Make the brief beautiful, readable, and restrained.

- Use a print-friendly, responsive layout with a readable measure and generous whitespace.
- Prefer semantic HTML and CSS over JavaScript. Use JavaScript only for genuinely useful interactions.
- Use tables for tradeoff matrices and decision comparisons.
- Use timelines or ordered phase lists for sequencing.
- Use callouts sparingly for decisions, risks, and assumptions.
- Keep the color palette quiet and purposeful; do not let decoration compete with the plan.
- Make status labels precise: `Proposed`, `Accepted`, `Assumption`, `Risk`, `Decision`, `Open`.

## Tradeoff Writing

Tradeoffs are the core of this skill. For each major choice, explain:

- What was chosen.
- What alternatives were considered.
- What the chosen path optimizes for.
- What it gives up.
- Whether the decision is reversible.
- What evidence would cause the team to revisit it.

Do not flatten disagreement. If the plan has uncertainty, make the uncertainty legible.

## Source Integrity

When the source plan contains facts, preserve them accurately. When you infer, label the inference as an assumption or recommendation. When a claim depends on current external facts, verify it with trustworthy sources and link those sources in the brief.
