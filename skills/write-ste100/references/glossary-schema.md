# STE preflight glossary schema

Use UTF-8 YAML with `version: 1`, a declared `scope`, and an explicit `terms` list.

```yaml
version: 1
scope: authoritative # or partial
terms:
  - term: hydraulic pump
    category: technical_noun
    source: Project terminology specification, section 4
    forms:
      - hydraulic pump
      - hydraulic pumps
    forbidden_forms:
      - hyd pump

  - term: calibrate
    category: technical_verb
    source: Maintenance engineering approval 42
    forms:
      - calibrate
      - calibrates
      - calibrated

  - term: API_TOKEN
    category: literal
    forms:
      - API_TOKEN
```

Use only these categories:

- `technical_noun`: Project-approved noun. Provide non-empty `source` metadata.
- `technical_verb`: Project-approved verb. Provide non-empty `source` metadata.
- `literal`: Exact content that the checker excludes, such as an identifier or UI label. Source metadata is optional.

List every permitted form explicitly, including the canonical `term`. Use `forbidden_forms` only for known prohibited variants. A form cannot occur in more than one term and cannot be both permitted and forbidden.

Set `scope: authoritative` only when the glossary governs all applicable project terminology for the checked document. Otherwise, set `scope: partial`. Validation checks structure and ambiguity; it does not approve terminology, invent forms, or add unknown terms.
