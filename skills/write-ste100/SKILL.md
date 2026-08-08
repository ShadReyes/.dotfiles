---
name: write-ste100
description: Draft, rewrite, and review technical documentation with ASD-STE100 Simplified Technical English (STE). Use for procedures, descriptions, safety instructions, maintenance content, software documentation, specifications, and terminology work when the user requests ASD-STE100, Simplified Technical English, controlled English, STE compliance, or an STE-style clarity review.
---

# Write ASD-STE100

Write technical content that is accurate, consistent, and easy to understand for an international audience. Preserve the technical meaning and the user's required document structure.

## Establish the conformance target

Classify the request before you edit:

- **Verified STE**: Apply the current official ASD-STE100 standard and its dictionary. Require access to the applicable issue, the project terminology, and any governing style or contractual rules.
- **STE draft**: Apply the official writing rules and check vocabulary against the official dictionary when it is available. Identify unresolved terms for human review.
- **STE-informed clarity**: Apply the core principles without claiming ASD-STE100 compliance.

If the user does not specify a target, produce an **STE draft**. Do not describe text as compliant, certified, or verified unless you checked it against the applicable official standard and project terminology.

## Prepare the source

1. Identify the audience, task, document type, safety context, and required meaning.
2. Separate procedural text from descriptive text. Treat warnings and cautions as safety instructions.
3. Preserve code, commands, identifiers, UI labels, legal text, quoted text, measurements, and product names exactly unless the user authorizes changes.
4. Collect the approved project terms. Keep one technical noun for each item and one technical verb for each action.
5. Resolve factual ambiguity before you simplify the language. Do not make a technically unclear sentence look authoritative.

## Apply the standard

Read [references/rule-guide.md](references/rule-guide.md) before you draft or review text. Use the current official ASD-STE100 issue as the source of truth for exact rule and dictionary decisions.

Rewrite in this order:

1. Preserve the exact technical intent, conditions, sequence, and risk.
2. Normalize terminology and classify necessary domain terms as technical nouns or technical verbs.
3. Replace unapproved general vocabulary with approved words or a different sentence construction.
4. Use approved meanings, parts of speech, word forms, and verb forms.
5. Use active voice. Use the imperative form for procedural steps.
6. Put one instruction in each procedural sentence, except for actions that occur at the same time.
7. Keep procedural sentences at 20 words or fewer and descriptive sentences at 25 words or fewer. Apply the official word-count rules.
8. Give descriptive information gradually. Keep one topic in each paragraph and no more than six sentences in a paragraph.
9. Make safety text identify the risk level, state the command or condition, and explain the possible result.
10. Review punctuation, articles, references, lists, spelling, and consistency.

Do not mechanically substitute synonyms. Rewrite the sentence when a word-for-word replacement changes the meaning or produces unnatural text.

## Review in separate passes

Perform these passes in order:

1. **Technical fidelity**: Compare the draft with the source. Confirm that no prerequisite, limit, result, or hazard changed.
2. **Terminology**: Check each general word in the official dictionary. Check each domain term against the project glossary and the permitted technical-term categories.
3. **Grammar and structure**: Check voice, verb tense, sentence type, sentence length, paragraph structure, and list structure.
4. **Safety**: Check risk level, command or condition, consequence, placement, and consistency with the governing safety standard.
5. **Literal content**: Confirm that commands, code, identifiers, values, units, labels, and quoted text remain exact.

Treat automated results as findings, not proof. Use human technical and linguistic review for a verified deliverable.

## Report the result

Return the rewritten text first. Then include only the review information that helps the user:

- State the conformance target and the ASD-STE100 issue used.
- List unresolved vocabulary, technical terms, or source ambiguities.
- Explain material changes that affect terminology, structure, or safety wording.
- For a review request, identify each finding by location, rule area, reason, and proposed correction.
- If exact dictionary or project-term checks were not possible, label the result **STE draft—not verified**.

Do not add a compliance statement when the user only asks for clearer writing.
