---
name: write-ste100
description: Draft, rewrite, review, and run an offline ASD-STE100 Issue 9 preflight on Markdown or plain-text technical documentation. Use for procedures, descriptions, safety instructions, controlled English, STE terminology lookup, glossary validation, or requests to check ASD-STE100 compliance. The automated result is never certification or verification.
---

# Write ASD-STE100

Write technical content that is accurate, consistent, and easy to understand for an international audience. Preserve the technical meaning and required structure.

## Establish the target

Classify the request before editing:

- **STE draft**: Apply Issue 9 writing rules, use the private dictionary index when available, and list unresolved terms.
- **STE-informed clarity**: Apply the core principles without an exact dictionary check.
- **Human-reviewed STE deliverable**: Use the official standard, authoritative project terminology, governing directives, and qualified technical and linguistic reviewers.

Default to an **STE draft**. Never describe an automated or agent-produced result as compliant, certified, or verified. The strongest CLI result is `ready_for_human_review`.

## Prepare the source

1. Identify the audience, task, document type, safety context, and required meaning.
2. Separate procedures from descriptions. Treat warnings and cautions as safety procedures and notes as descriptions.
3. Preserve code, commands, identifiers, UI labels, legal text, quoted text, measurements, and product names unless the user authorizes changes.
4. Collect approved project terms. Keep one technical noun for each item and one technical verb for each action.
5. Resolve factual ambiguity before simplifying language.

## Use the offline preflight

The CLI is [scripts/ste100](scripts/ste100). It requires `uv`, uses its committed script lock, makes no network requests during indexing or analysis, and supports only UTF-8 Markdown and plain text in v1.

Run `doctor` before dictionary or document checks:

```sh
skills/write-ste100/scripts/ste100 doctor --format json
```

If the index is absent, ask the user for their officially obtained Issue 9 PDF. Do not download the standard, use OCR, or copy the PDF or index into the skill. Then run:

```sh
skills/write-ste100/scripts/ste100 setup --pdf /path/to/official-issue-9.pdf --format json
```

The private index is stored below `${STE100_DATA_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/ste100}` with source-hash provenance and private permissions. Setup rejects other issues, scanned copies, incomplete content, and changed table geometry.

Use bounded dictionary evidence when a term needs review:

```sh
skills/write-ste100/scripts/ste100 lookup WORD --part-of-speech POS --format json
skills/write-ste100/scripts/ste100 search "approved meaning" --limit 10 --format json
```

Validate a project glossary before using it. Read [references/glossary-schema.md](references/glossary-schema.md) for the YAML contract.

```sh
skills/write-ste100/scripts/ste100 glossary validate project-terms.yaml --format json
```

Check a document or write a durable report:

```sh
skills/write-ste100/scripts/ste100 check document.md --type auto --glossary project-terms.yaml --format json
skills/write-ste100/scripts/ste100 report document.md --type auto --glossary project-terms.yaml --format markdown --output ste-preflight.md
```

Interpret results as follows:

- Exit `0`: No finding met the selected threshold and coverage is complete. Human review is still required.
- Exit `1`: A finding met the threshold or terminology coverage is incomplete.
- Exit `2`: Setup, index, input, glossary, or output error.
- `coverage.status: incomplete`: Resolve every listed term; do not weaken the threshold or invent a glossary classification.
- `mode: exact`: Deterministic preflight check, not proof that meaning or part of speech is correct in context.
- `mode: heuristic`: Review warning only. A confidence label never turns a heuristic into an error.

Use `--fail-on error` by default. Use `--fail-on warning` when the workflow requires warnings to fail. Never treat the CLI result as release approval.

## Apply the standard

Read [references/rule-guide.md](references/rule-guide.md) before drafting or reviewing. Use the user's official Issue 9 copy as the authority for exact rules, examples, exceptions, and dictionary decisions.

Rewrite in this order:

1. Preserve the exact technical intent, conditions, sequence, and risk.
2. Normalize terminology and classify necessary domain terms only from an authoritative source.
3. Replace unapproved general vocabulary by rewriting the sentence when necessary.
4. Use approved meanings, parts of speech, and forms.
5. Use active voice and imperative procedural steps.
6. Put one instruction in each procedural sentence unless actions occur at the same time.
7. Keep procedure sentences at 20 words or fewer and description sentences at 25 words or fewer, with the official exceptions.
8. Keep one topic and no more than six sentences in each descriptive paragraph.
9. Make safety text identify the risk level, command or condition, and possible result.
10. Review punctuation, references, lists, spelling, terminology, and literal content.

Do not mechanically substitute synonyms. Rewrite when substitution changes meaning or produces unnatural text.

## Review and report

Review technical fidelity, terminology, grammar and structure, safety, and literal content in separate passes. Return rewritten text first when the user asks for a rewrite. Then state Issue 9, the target, material changes, unresolved terms, coverage, and useful findings by location.

Label work without a complete dictionary and authoritative project-term review **STE draft—not verified**. Always require qualified human review for meaning in context, technical accuracy, term classification, safety risk, and final release approval.
