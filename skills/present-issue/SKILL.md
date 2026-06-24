---
name: present-issue
description: Convert bug reports, production incidents, support escalations, QA findings, regression notes, investigation summaries, or issue tracker threads into polished, single-file HTML briefings with inline CSS. Use when the user asks to make a bug or issue presentable, summarize an incident, explain impact and root cause, compare fixes, document remediation tradeoffs, or create a shareable issue brief for stakeholders.
---

The user has asked you to turn a bug, issue, or incident into a presentable HTML document. Treat the output as a durable evidence brief: it should help readers understand what happened, who is affected, how confident the diagnosis is, and what remediation path is recommended.

## Issue Brief Workspace

Use the current directory as the workspace unless the user specifies another location.

- `./issue-briefs/*.html`: Final presentation documents. Name files `0001-<dash-case-title>.html`, incrementing the number each time.
- Skill asset `assets/issue-brief.css`: Default source stylesheet. Read it from this skill and inline the CSS inside the generated HTML.
- Workspace `./assets/*`: Existing local assets or prior reusable components. Inspect this directory before authoring, but do not require external CSS for the final brief.

Do not create auxiliary documentation unless the user asks for it. The HTML brief is the primary output and should be shareable as one file.

## Workflow

1. Gather the evidence.
   - Read the bug report, issue, support thread, logs, screenshots, reproduction notes, stack traces, PRs, commits, monitoring links, or local files the user provides.
   - If the issue depends on repository behavior, inspect the relevant code before writing.
   - For production investigations, preserve exact identifiers, timestamps, versions, environments, and affected records when available.
   - Ask a concise clarifying question only when the audience, source issue, or desired decision is missing and cannot be inferred safely.

2. Separate facts from interpretation.
   - Label confirmed facts, user-reported symptoms, inferred causes, assumptions, and open questions.
   - Record confidence on diagnosis and fix options as `High`, `Medium`, or `Low`.
   - Avoid overstating root cause when the evidence only supports correlation.

3. Choose the brief shape.
   - Default to a stakeholder-ready technical issue brief for mixed product, support, and engineering readers.
   - Bias toward an incident brief when the user mentions production, outage, severity, customer impact, timeline, monitoring, or postmortem.
   - Bias toward a QA bug brief when the user mentions reproduction steps, expected vs actual behavior, browser/device, regression, or acceptance criteria.
   - Bias toward a remediation brief when the user mentions fixes, options, patches, rollout, rollback, or tradeoffs.

4. Write the HTML document.
   - Make the document standalone enough that a reader can understand the issue without reading the original raw thread.
   - Embed CSS in a `<style>` tag in the document `<head>`; do not link to `./assets/issue-brief.css` unless the user explicitly asks for separate assets.
   - Start from this skill's `assets/issue-brief.css` when the workspace does not already have suitable CSS, then adapt the inlined styles to the brief.
   - Preserve the evidence accurately, but rewrite for clarity, sequencing, and decision quality.
   - Use clear headings, impact summaries, evidence tables, timelines, callouts, and concise prose.
   - Include links to source issues, PRs, logs, dashboards, docs, traces, or commits when available.
   - Avoid blame, speculation presented as fact, generic claims, and filler.

5. Validate the artifact.
   - Confirm the final HTML has no required local stylesheet dependency; it should render when shared by itself.
   - Ensure any remaining relative links resolve from the HTML file's location.
   - Open the HTML file when possible and inspect it for layout problems.
   - Check that the document prints well: no dark full-page backgrounds, no clipped tables, and sensible page breaks.

## Recommended Sections

Use only the sections that fit the issue.

- Title and metadata: issue name, status, severity, owner, date, environment, audience.
- Executive summary: one short paragraph naming the symptom, impact, and current recommendation.
- Impact: affected users, accounts, workflows, data, revenue, reliability, support load, or operational risk.
- Current status: `Investigating`, `Mitigated`, `Fix proposed`, `Fix shipped`, `Monitoring`, or `Closed`.
- Reproduction: prerequisites, steps, expected behavior, actual behavior, and reproducibility.
- Evidence: logs, screenshots, traces, metrics, user reports, code references, and timestamps.
- Timeline: discovery, first occurrence, detection, mitigation, fix, rollout, and monitoring events.
- Root cause analysis: confirmed cause, contributing factors, confidence, and evidence gaps.
- Fix options: candidate fixes, expected effect, implementation cost, risk, reversibility, and test coverage.
- Recommended path: the chosen remediation and why it best fits the evidence.
- Tradeoffs: speed vs safety, hotfix vs durable fix, scope containment, data repair, migration risk, and user communication.
- Testing and rollout: verification plan, regression coverage, deployment path, monitoring, rollback, and success criteria.
- Open questions: items that require more evidence or a decision.
- Next actions: a short checklist of concrete follow-ups.

## Design Standards

Make the brief readable, evidence-forward, and calm.

- Use a print-friendly, responsive layout with a readable measure and generous whitespace.
- Prefer semantic HTML and CSS over JavaScript. Use JavaScript only for genuinely useful interactions.
- Use tables for evidence inventories, reproduction matrices, and fix comparisons.
- Use timelines for incidents or multi-step investigations.
- Use callouts sparingly for impact, diagnosis, recommendation, and unresolved risk.
- Keep the color palette restrained; severity color should help scanning, not create alarm.
- Make status labels precise: `Confirmed`, `Reported`, `Inferred`, `Assumption`, `Open`, `Recommended`, `Shipped`.

## Evidence Writing

Evidence quality is the core of this skill. For each major claim, explain:

- What the evidence shows.
- Where the evidence came from.
- Whether the claim is confirmed or inferred.
- How confident the diagnosis is.
- What evidence would disprove or weaken the claim.
- What evidence is still missing.

Do not turn uncertainty into certainty. If the issue is unresolved, make the uncertainty legible.

## Remediation Tradeoffs

For each meaningful fix option, explain:

- What the fix changes.
- What symptom or cause it addresses.
- What it optimizes for.
- What it gives up.
- Whether it is reversible.
- How it will be tested and monitored.

Prefer a recommendation over a neutral list when the evidence supports one. If it does not, state what investigation should happen next.

## Source Integrity

When the source issue contains facts, preserve them accurately. When you infer, label the inference as an assumption, hypothesis, or recommendation. When a claim depends on current external facts, verify it with trustworthy sources and link those sources in the brief.
