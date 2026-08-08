# ASD-STE100 rule guide

Use this guide as an operating summary. Use the official standard for exact rules, examples, exceptions, technical-term categories, and dictionary decisions.

## Authority and scope

ASD-STE100 is a controlled natural language for technical documentation. Issue 9, dated January 15, 2025, contains 53 writing rules in nine sections and a controlled dictionary of approximately 900 approved general words. The dictionary does not contain all company, industry, or subject-field terms; STE permits controlled technical nouns and technical verbs.

Use these authorities in this order:

1. The applicable contract, publication specification, safety standard, and project glossary
2. The current official ASD-STE100 issue
3. This guide

Confirm the current issue on the official site before you claim verified conformance. Do not reproduce or invent an "approved" dictionary from memory.

## 1. Vocabulary and terminology

- Use an official dictionary word only with its approved meaning, part of speech, and form.
- Use an out-of-dictionary word only when it qualifies as a technical noun or technical verb under the standard.
- Prefer a short, easy technical noun. Avoid regional language, slang, and jargon.
- Use the project-approved technical noun for an item. Do not use multiple names for the same item.
- Use a technical noun only as a noun or as a modifier in another technical noun.
- Use a technical verb only as a verb.
- Use American English spelling unless a governing directive requires a different spelling.
- Record unresolved terms. Do not silently classify a convenient word as technical vocabulary.

For software documentation, treat exact identifiers such as API names, classes, functions, commands, options, paths, keys, and UI labels as literal or project terminology. Do not change an identifier to make the surrounding sentence simpler.

## 2. Multi-word nouns

- Keep a multi-word noun to three words or fewer when possible.
- If an approved technical noun has more than three words, write its full form at first use.
- Define a clear shorter form when repeated use is necessary, or use permitted hyphenation to show words that act as one unit.
- Do not create a shorter form that can refer to a different item.

## 3. Verbs

- Use only permitted verb forms and tenses: infinitive, imperative, simple present, simple past, simple future, and past participle as an adjective.
- Avoid perfect, progressive, and other complex verb constructions.
- Use an `-ing` form only when it is a technical noun or modifies a technical noun.
- Use active voice. In descriptive text, use passive voice only when the agent is unknown.
- Describe an action with a verb, not with an abstract noun phrase.

Prefer a direct instruction such as “Save the configuration file.” Avoid an indirect construction such as “The configuration file should be saved.” Confirm `save` as an approved project technical verb before a verified STE claim.

## 4. General sentence structure

- Write short, complete sentences. Do not omit necessary words and do not use contractions.
- Use a vertical list when a sentence contains complex or parallel information.
- Use explicit connecting words or phrases when they make the relationship between sentences clear.
- Use articles and demonstrative adjectives where standard English grammar requires them.
- Avoid stacked conditions, hidden subjects, vague pronouns, and long chains of modifiers.

## 5. Procedures

- Use no more than 20 words in a procedural sentence, including warnings and cautions. Apply the official word-count exceptions.
- Give one instruction in each sentence. Combine actions only when they occur at the same time.
- Use the imperative form and address the reader directly.
- Put a condition first when the reader must know it before the action. Separate it from the command with a comma.
- Use notes for information only. Put required actions in numbered work steps.

Example pattern:

```text
If the status light is red, stop the service.
Copy the API token to the configuration file.
```

Treat `status light`, `service`, `API token`, and `configuration file` as project technical nouns. Verify `copy` as an approved or permitted technical verb.

## 6. Descriptions

- Give information gradually and use repeated key terms to make the structure clear.
- Use no more than 25 words in a descriptive sentence.
- Group related sentences in a paragraph.
- Keep one topic in each paragraph.
- Use no more than six sentences in a paragraph.
- Do not use the imperative form for descriptive information.

## 7. Safety instructions

- Use the risk-level term required by the governing domain, such as `WARNING` or `CAUTION`.
- Start with a clear command or condition.
- Explain the hazard or possible result.
- Preserve the difference between injury or death risk and equipment or property damage.
- Do not weaken mandatory safety language during a rewrite.

Do not invent or reclassify a risk level. Escalate unclear safety content to a qualified reviewer.

## 8. Punctuation and word count

- Use standard English punctuation, but do not use semicolons.
- Use hyphens to connect directly related words when the standard permits them.
- Use parentheses only for the purposes permitted by the standard.
- Follow the official counting rules for lists, parenthetical text, numbers and units, abbreviations, identifiers, quoted text, headings, labels, proper nouns, and hyphenated words.
- Do not estimate compliance from a simple whitespace word count.

## 9. Writing practices

- Rewrite the sentence when direct word substitution is insufficient.
- Check the approved meaning every time a familiar word has multiple senses.
- Avoid phrasal verbs unless the dictionary approves the construction.
- Use the same terminology and wording for the same meaning throughout the document set.
- Prefer explicit references over vague pronouns. Add `that` when it makes a clause boundary clear.
- Avoid Latin abbreviations and culture-specific expressions when a clear English phrase is available.
- Use inclusive language that preserves technical precision.

## Conformance checklist

Before you label a deliverable verified, confirm all of these items:

- The applicable ASD-STE100 issue is identified.
- Each general word is approved for its meaning, part of speech, and form.
- Each project term is approved and consistently classified.
- Procedures and descriptions use the correct sentence type and length.
- Verb forms, voice, paragraphs, punctuation, and word counts follow the standard.
- Warnings and cautions preserve the correct risk and result.
- Literal technical content is unchanged.
- A qualified person reviewed the technical meaning and unresolved tool findings.

## Sources

- [Official ASD-STE100 site](https://www.asd-ste100.org/)
- [Official ASD-STE100 downloads](https://www.asd-ste100.org/STE_downloads.html)
- [Official ASD-STE100 FAQ](https://www.asd-ste100.org/STE_faq.html)
- [Official guidance about STE training](https://www.asd-ste100.org/STE_training.html)
- [Official guidance about STE software and checkers](https://www.asd-ste100.org/STEsoftware.html)
