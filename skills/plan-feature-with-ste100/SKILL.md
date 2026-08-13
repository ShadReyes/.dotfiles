---
name: plan-feature-with-ste100
description: Create, revise, or audit feature-planning documentation by combining blowmage:plan-feature with write-ste100 and a feature-local project glossary. Use when a feature plan, specification, task breakdown, or planning bundle must use ASD-STE100 Issue 9 controlled-English guidance, terminology validation, or an STE100 preflight without coupling the underlying skills.
---

# Plan a Feature With STE100

Coordinate two independent skills. Load and follow `blowmage:plan-feature` and
`write-ste100` before acting.

Use `blowmage:plan-feature` as the authority for repository orientation, evidence,
planning topology, requirements, decisions, delivery slices, and verification. Use
`write-ste100` as the authority for controlled language, glossary rules, CLI usage,
result interpretation, and human-review limits.

In the commands below, `ste100` means the CLI at `scripts/ste100` inside the installed
`write-ste100` skill. Resolve that skill path before running the command; do not assume
that `ste100` is installed globally.

## Preserve Meaning and Conventions

1. Follow repository-local instructions and established planning conventions.
2. Preserve technical meaning, citations, code, commands, identifiers, UI labels,
   product names, measurements, legal text, and quoted text.
3. Do not simplify away a requirement, condition, dependency, decision, risk, or
   acceptance criterion to satisfy a language rule.
4. Record an unresolved term or wording conflict when an accurate STE rewrite is
   not available.
5. Describe the result as an **STE draft—not verified**. Never describe an automated
   result as compliant, certified, verified, or approved for release.

## Locate the Glossary

Use a glossary path supplied by the user. Otherwise, determine the planning location
with `blowmage:plan-feature`, then co-locate the glossary with the feature artifacts:

- For a feature directory, use `<feature-dir>/ste100-glossary.yaml`.
- For a standalone planning file, use a sibling
  `<work-name>-ste100-glossary.yaml` without reorganizing project documentation.

Reuse an existing applicable glossary before creating another one. Keep one glossary
per CLI check because `write-ste100` accepts one `--glossary` path. Combine all terms
needed for the checked artifact in that file.

Set `scope: authoritative` only when the glossary governs all applicable project
terminology in the checked artifacts. Otherwise, set `scope: partial`. Do not invent
term classifications, permitted forms, or source metadata. Obtain them from an
authoritative project source or the user.

## Plan and Preflight

1. Inspect the repository and build the evidence base with `blowmage:plan-feature`.
2. Choose the planning shape before selecting the default glossary path.
3. Collect authoritative project terms and literals needed by the plan.
4. Run `ste100 doctor` and follow the setup requirements in `write-ste100`.
5. Validate the glossary with `ste100 glossary validate <glossary-path>`.
6. Draft or revise the planning artifacts. Apply Issue 9 guidance without changing
   their planning responsibilities or technical intent.
7. Check each supported Markdown or plain-text planning artifact with
   `--glossary <glossary-path>` and the default `--fail-on error`.
8. Resolve every incomplete-coverage term through evidence or list it as unresolved.
   Do not weaken the failure threshold or fabricate a glossary classification.
9. Recheck planning links, requirement mappings, decision status, phase dependencies,
   terminology consistency, and CLI findings before finalizing.

## Report the Result

Return the planning artifacts in the repository's established location. Report:

- the glossary path and whether its scope is authoritative or partial;
- the checked artifact paths;
- the STE target and preflight result;
- unresolved terms, incomplete coverage, and material findings; and
- the required human review for technical meaning, terminology classification,
  safety, and release approval.
