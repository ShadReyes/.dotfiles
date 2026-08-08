from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any

import yaml


class GlossaryValidationError(ValueError):
    pass


@dataclass(frozen=True)
class GlossaryTerm:
    term: str
    category: str
    source: str | None
    forms: tuple[str, ...]
    forbidden_forms: tuple[str, ...]


@dataclass(frozen=True)
class Glossary:
    path: Path
    sha256: str
    version: int
    scope: str
    terms: tuple[GlossaryTerm, ...]

    @property
    def literal_forms(self) -> tuple[str, ...]:
        return tuple(
            form
            for term in self.terms
            if term.category == "literal"
            for form in term.forms
        )

    @property
    def permitted_phrases(self) -> tuple[tuple[str, GlossaryTerm], ...]:
        pairs = [
            (form, term)
            for term in self.terms
            if term.category != "literal"
            for form in term.forms
        ]
        return tuple(
            sorted(
                pairs,
                key=lambda pair: (
                    -len(pair[0].split()),
                    -len(pair[0]),
                    pair[0].casefold(),
                ),
            )
        )

    @property
    def forbidden_phrases(self) -> tuple[tuple[str, GlossaryTerm], ...]:
        pairs = [(form, term) for term in self.terms for form in term.forbidden_forms]
        return tuple(
            sorted(
                pairs,
                key=lambda pair: (
                    -len(pair[0].split()),
                    -len(pair[0]),
                    pair[0].casefold(),
                ),
            )
        )


ALLOWED_CATEGORIES = {"technical_noun", "technical_verb", "literal"}
ALLOWED_ROOT_KEYS = {"version", "scope", "terms"}
ALLOWED_TERM_KEYS = {"term", "category", "source", "forms", "forbidden_forms"}


def _nonempty_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GlossaryValidationError(f"{location} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, location: str, required: bool) -> tuple[str, ...]:
    if value is None and not required:
        return ()
    if not isinstance(value, list) or (required and not value):
        qualifier = "a non-empty" if required else "a"
        raise GlossaryValidationError(f"{location} must be {qualifier} list of strings")
    strings = tuple(_nonempty_string(item, f"{location} item") for item in value)
    if len({item.casefold() for item in strings}) != len(strings):
        raise GlossaryValidationError(f"{location} contains duplicate forms")
    return strings


def load_glossary(path: Path) -> Glossary:
    if not path.is_file():
        raise GlossaryValidationError(f"Glossary does not exist: {path}")
    try:
        content = path.read_bytes()
    except OSError as error:
        raise GlossaryValidationError(f"Cannot read glossary: {error}") from error
    if len(content) > 1_000_000:
        raise GlossaryValidationError("Glossary is larger than the 1 MB limit")
    try:
        document = yaml.safe_load(content.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as error:
        raise GlossaryValidationError(
            f"Glossary is not valid UTF-8 YAML: {error}"
        ) from error
    if not isinstance(document, dict):
        raise GlossaryValidationError("Glossary root must be a mapping")
    unknown_root = set(document) - ALLOWED_ROOT_KEYS
    if unknown_root:
        raise GlossaryValidationError(
            f"Unknown glossary fields: {', '.join(sorted(unknown_root))}"
        )
    if document.get("version") != 1:
        raise GlossaryValidationError("Glossary version must be 1")
    scope = document.get("scope")
    if scope not in {"authoritative", "partial"}:
        raise GlossaryValidationError("Glossary scope must be authoritative or partial")
    raw_terms = document.get("terms")
    if not isinstance(raw_terms, list):
        raise GlossaryValidationError("Glossary terms must be a list")

    terms: list[GlossaryTerm] = []
    claimed_forms: dict[str, str] = {}
    for index, raw_term in enumerate(raw_terms, start=1):
        location = f"terms[{index}]"
        if not isinstance(raw_term, dict):
            raise GlossaryValidationError(f"{location} must be a mapping")
        unknown = set(raw_term) - ALLOWED_TERM_KEYS
        if unknown:
            raise GlossaryValidationError(
                f"{location} has unknown fields: {', '.join(sorted(unknown))}"
            )
        term = _nonempty_string(raw_term.get("term"), f"{location}.term")
        category = raw_term.get("category")
        if category not in ALLOWED_CATEGORIES:
            raise GlossaryValidationError(
                f"{location}.category must be technical_noun, technical_verb, or literal"
            )
        source_value = raw_term.get("source")
        source = (
            _nonempty_string(source_value, f"{location}.source")
            if source_value is not None
            else None
        )
        if category != "literal" and source is None:
            raise GlossaryValidationError(
                f"{location}.source is required for technical terms"
            )
        forms = _string_list(raw_term.get("forms"), f"{location}.forms", required=True)
        forbidden = _string_list(
            raw_term.get("forbidden_forms"),
            f"{location}.forbidden_forms",
            required=False,
        )
        if term.casefold() not in {form.casefold() for form in forms}:
            raise GlossaryValidationError(
                f"{location}.forms must explicitly include the term"
            )
        overlap = {form.casefold() for form in forms} & {
            form.casefold() for form in forbidden
        }
        if overlap:
            raise GlossaryValidationError(
                f"{location} permits and forbids the same form"
            )
        for form in forms + forbidden:
            normalized = form.casefold()
            previous = claimed_forms.get(normalized)
            if previous is not None:
                raise GlossaryValidationError(
                    f"Form {form!r} is ambiguous between {previous} and {term}"
                )
            claimed_forms[normalized] = term
        terms.append(GlossaryTerm(term, category, source, forms, forbidden))
    return Glossary(
        path=path.resolve(),
        sha256=hashlib.sha256(content).hexdigest(),
        version=1,
        scope=scope,
        terms=tuple(terms),
    )
