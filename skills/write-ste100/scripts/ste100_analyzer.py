from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from typing import Any, Iterable

from ste100_glossary import Glossary
from ste100_index import DictionaryIndex


class AnalysisError(ValueError):
    pass


WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
CONTRACTIONS = (
    "ain't",
    "aren't",
    "can't",
    "couldn't",
    "could've",
    "didn't",
    "doesn't",
    "don't",
    "hadn't",
    "hasn't",
    "haven't",
    "he'd",
    "he'll",
    "he's",
    "I'd",
    "I'll",
    "I'm",
    "I've",
    "isn't",
    "it'd",
    "it'll",
    "it's",
    "let's",
    "mightn't",
    "might've",
    "mustn't",
    "must've",
    "needn't",
    "shan't",
    "she'd",
    "she'll",
    "she's",
    "shouldn't",
    "should've",
    "that'll",
    "that's",
    "there'd",
    "there'll",
    "there's",
    "they'd",
    "they'll",
    "they're",
    "they've",
    "wasn't",
    "we'd",
    "we'll",
    "we're",
    "we've",
    "weren't",
    "what'd",
    "what'll",
    "what's",
    "when's",
    "where's",
    "who'd",
    "who'll",
    "who's",
    "won't",
    "wouldn't",
    "would've",
    "you'd",
    "you'll",
    "you're",
    "you've",
)
CONTRACTION_RE = re.compile(
    r"\b(?:"
    + "|".join(re.escape(item).replace("'", "['’]") for item in CONTRACTIONS)
    + r")\b",
    re.IGNORECASE,
)
IDENTIFIER_PATTERNS = (
    re.compile(r"`[^`\n]+`"),
    re.compile(r"(?<=\])\([^\n)]*\)"),
    re.compile(r"https?://[^\s)>]+", re.IGNORECASE),
    re.compile(
        r"(?<!\w)(?:--?[A-Za-z][\w-]*|/[A-Za-z0-9._/-]+|[A-Za-z]+_[A-Za-z0-9_]+|[a-z]+[A-Z][A-Za-z0-9]*)"
    ),
)
MEASUREMENT_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mm|cm|m|km|in|ft|kg|g|lb|psi|bar|hz|v|a)\b|\b\d+(?:\.\d+)?\s*%",
    re.IGNORECASE,
)
PROPER_NAME_RE = re.compile(r"\b(?:[A-Z][a-z]+\s+){1,}[A-Z][a-z]+\b")
COUNT_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-/][A-Za-z0-9]+)*")
PASSIVE_RE = re.compile(
    r"\b(?:am|are|is|was|were|be|been|being)\s+(?:\w+ly\s+)?\w+(?:ed|en)\b",
    re.IGNORECASE,
)
COMPLEX_VERB_RE = re.compile(
    r"\b(?:has|have|had)\s+\w+(?:ed|en)\b|\b(?:am|are|is|was|were|be|been)\s+\w+ing\b|\bwill\s+have\b",
    re.IGNORECASE,
)
COMMON_IMPERATIVES = {
    "add",
    "apply",
    "attach",
    "check",
    "close",
    "connect",
    "continue",
    "disconnect",
    "do",
    "install",
    "make",
    "move",
    "open",
    "put",
    "remove",
    "set",
    "start",
    "stop",
    "turn",
    "use",
    "verify",
    "wait",
}
NOUN_GROUP_STOP = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "if",
    "in",
    "is",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "will",
    "with",
}


@dataclass(frozen=True)
class Block:
    original: str
    prepared: str
    line_numbers: tuple[int, ...]
    line_starts: tuple[int, ...]
    mode: str
    safety: bool
    note: bool
    paragraph: bool

    def location(self, start: int, end: int) -> dict[str, int]:
        start_line_index = max(0, bisect_right(self.line_starts, start) - 1)
        end_offset = max(start, end - 1)
        end_line_index = max(0, bisect_right(self.line_starts, end_offset) - 1)
        return {
            "line": self.line_numbers[start_line_index],
            "column": start - self.line_starts[start_line_index] + 1,
            "end_line": self.line_numbers[end_line_index],
            "end_column": end_offset - self.line_starts[end_line_index] + 2,
        }


def _blank_prefix(line: str, pattern: re.Pattern[str]) -> tuple[str, bool]:
    match = pattern.match(line)
    if not match:
        return line, False
    return " " * match.end() + line[match.end() :], True


def _blocks(text: str, document_type: str) -> list[Block]:
    lines = text.splitlines()
    available: list[tuple[int, str]] = []
    fence: str | None = None
    for line_number, line in enumerate(lines, start=1):
        marker = re.match(r"^\s*(```+|~~~+)", line)
        if marker:
            token = marker.group(1)[0]
            if fence is None:
                fence = token
            elif fence == token:
                fence = None
            continue
        if fence is None:
            available.append((line_number, line))

    result: list[Block] = []
    pending: list[tuple[int, str, str]] = []

    def flush_pending() -> None:
        if not pending:
            return
        originals = [item[1] for item in pending]
        prepared = [item[2] for item in pending]
        starts: list[int] = []
        cursor = 0
        for line in originals:
            starts.append(cursor)
            cursor += len(line) + 1
        mode = document_type if document_type != "auto" else "description"
        result.append(
            Block(
                "\n".join(originals),
                "\n".join(prepared),
                tuple(item[0] for item in pending),
                tuple(starts),
                mode,
                False,
                False,
                True,
            )
        )
        pending.clear()

    ordered_re = re.compile(r"^\s*\d+[.)]\s+")
    safety_re = re.compile(r"^\s*(?:WARNING|CAUTION|DANGER)\s*[:—-]\s*", re.IGNORECASE)
    note_re = re.compile(r"^\s*NOTE\s*[:—-]\s*", re.IGNORECASE)
    markdown_re = re.compile(r"^\s*(?:#{1,6}\s+|[-*+]\s+)")
    for line_number, original in available:
        if not original.strip():
            flush_pending()
            continue
        prepared, ordered = _blank_prefix(original, ordered_re)
        if ordered:
            flush_pending()
            mode = document_type if document_type != "auto" else "procedure"
            result.append(
                Block(
                    original, prepared, (line_number,), (0,), mode, False, False, False
                )
            )
            continue
        prepared, safety = _blank_prefix(original, safety_re)
        if safety:
            flush_pending()
            mode = document_type if document_type != "auto" else "procedure"
            result.append(
                Block(
                    original, prepared, (line_number,), (0,), mode, True, False, False
                )
            )
            continue
        prepared, note = _blank_prefix(original, note_re)
        if note:
            flush_pending()
            mode = document_type if document_type != "auto" else "description"
            result.append(
                Block(
                    original, prepared, (line_number,), (0,), mode, False, True, False
                )
            )
            continue
        prepared, _ = _blank_prefix(original, markdown_re)
        pending.append((line_number, original, prepared))
    flush_pending()
    return result


def _ranges_for_literals(text: str, literals: Iterable[str]) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for pattern in IDENTIFIER_PATTERNS:
        ranges.extend((match.start(), match.end()) for match in pattern.finditer(text))
    for literal in literals:
        ranges.extend(
            (match.start(), match.end())
            for match in re.finditer(re.escape(literal), text)
        )
    return _merge_ranges(ranges)


def _merge_ranges(ranges: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


def _apply_ranges(
    text: str, ranges: Iterable[tuple[int, int]], placeholder: bool
) -> str:
    characters = list(text)
    for start, end in ranges:
        for index in range(start, end):
            characters[index] = " "
        if placeholder and start < end:
            characters[start] = "X"
    return "".join(characters)


def _sentence_ranges(text: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start = 0
    for match in re.finditer(r"[.!?]+(?:[\"')\]]+)?", text):
        if text[start : match.end()].strip():
            ranges.append((start, match.end()))
        start = match.end()
    tail = text[start:]
    if tail.strip() and (tail.rstrip().endswith(":") or "\n" not in tail):
        ranges.append((start, len(text)))
    return ranges


def _count_words(text: str) -> int:
    text = re.sub(r"\([^()]*\)", " ", text)
    text = re.sub(r'"[^"\n]*"|“[^”\n]*”', " X ", text)
    text = MEASUREMENT_RE.sub(" X ", text)
    text = PROPER_NAME_RE.sub(" X ", text)
    return len(COUNT_WORD_RE.findall(text))


def _phrase_matches(text: str, phrase: str) -> Iterable[re.Match[str]]:
    boundary = rf"(?<![\w-]){re.escape(phrase)}(?![\w-])"
    return re.finditer(boundary, text, re.IGNORECASE)


class Analyzer:
    def __init__(self, dictionary: DictionaryIndex, glossary: Glossary | None = None):
        self.dictionary = dictionary
        self.glossary = glossary
        self._lookup_cache: dict[str, list[dict[str, Any]]] = {}

    def analyze(self, path: Path, document_type: str = "auto") -> dict[str, Any]:
        if document_type not in {"auto", "procedure", "description"}:
            raise AnalysisError("Document type must be auto, procedure, or description")
        if not path.is_file():
            raise AnalysisError(f"Input file does not exist: {path}")
        if path.suffix.casefold() not in {".md", ".markdown", ".txt"}:
            raise AnalysisError("Only Markdown and plain-text inputs are supported")
        content = path.read_bytes()
        if len(content) > 10_000_000:
            raise AnalysisError("Input is larger than the 10 MB limit")
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as error:
            raise AnalysisError("Input must be UTF-8") from error

        findings: list[dict[str, Any]] = []
        unresolved: dict[str, list[dict[str, int]]] = {}
        coverage = {
            "candidate_terms": 0,
            "dictionary_matches": 0,
            "glossary_matches": 0,
            "excluded_literals": 0,
            "unresolved_occurrences": 0,
        }
        blocks = _blocks(text, document_type)
        for block in blocks:
            self._analyze_block(block, findings, unresolved, coverage)
        findings.sort(
            key=lambda finding: (
                finding["location"]["line"],
                finding["location"]["column"],
                finding["check_id"],
                finding["excerpt"],
            )
        )
        unresolved_terms = [
            {"term": term, "occurrences": locations}
            for term, locations in sorted(unresolved.items())
        ]
        coverage["status"] = "complete" if not unresolved_terms else "incomplete"
        coverage["terminology_authority"] = (
            self.glossary.scope if self.glossary else "official_dictionary_only"
        )
        errors = sum(finding["severity"] == "error" for finding in findings)
        warnings = sum(finding["severity"] == "warning" for finding in findings)
        heuristics = sum(finding["mode"] == "heuristic" for finding in findings)
        metadata = self.dictionary.metadata()
        return {
            "schema_version": 1,
            "standard": {
                "name": "ASD-STE100",
                "issue": 9,
                "date": metadata["issue_date"],
                "assessment": "preflight_not_certification",
            },
            "input": {
                "path": str(path.resolve()),
                "sha256": hashlib.sha256(content).hexdigest(),
                "document_type": document_type,
                "bytes": len(content),
            },
            "index": {
                "source_sha256": metadata["source_sha256"],
                "parser_version": metadata["parser_version"],
                "schema_version": int(metadata["schema_version"]),
            },
            "glossary": (
                {
                    "path": str(self.glossary.path),
                    "sha256": self.glossary.sha256,
                    "version": self.glossary.version,
                    "scope": self.glossary.scope,
                }
                if self.glossary
                else None
            ),
            "coverage": coverage,
            "summary": {
                "errors": errors,
                "warnings": warnings,
                "heuristic_warnings": heuristics,
            },
            "findings": findings,
            "unresolved_terms": unresolved_terms,
            "human_review_checklist": [
                "Confirm each dictionary word has the approved meaning and part of speech in context.",
                "Confirm project-term categories, forms, and consistency with the authoritative terminology source.",
                "Confirm technical accuracy, prerequisites, limits, and sequence.",
                "Confirm safety risk level, command or condition, consequence, and placement.",
                "Confirm final release approval with a qualified human reviewer.",
            ],
            "result": (
                "ready_for_human_review"
                if errors == 0 and warnings == 0 and coverage["status"] == "complete"
                else "findings_require_resolution"
            ),
        }

    def _analyze_block(
        self,
        block: Block,
        findings: list[dict[str, Any]],
        unresolved: dict[str, list[dict[str, int]]],
        coverage: dict[str, Any],
    ) -> None:
        literals = self.glossary.literal_forms if self.glossary else ()
        literal_ranges = _ranges_for_literals(block.prepared, literals)
        coverage["excluded_literals"] += len(literal_ranges)
        analysis_text = _apply_ranges(block.prepared, literal_ranges, placeholder=False)
        count_text = _apply_ranges(block.prepared, literal_ranges, placeholder=True)
        covered: list[tuple[int, int]] = list(literal_ranges)

        if self.glossary:
            for phrase, term in self.glossary.forbidden_phrases:
                for match in _phrase_matches(analysis_text, phrase):
                    if _overlaps((match.start(), match.end()), covered):
                        continue
                    covered.append((match.start(), match.end()))
                    findings.append(
                        self._finding(
                            block,
                            match.start(),
                            match.end(),
                            "STE-LEX-002",
                            "1.1",
                            "exact",
                            "error",
                            "high",
                            f"Forbidden project-term variant: {match.group(0)}",
                            f"Use an explicitly permitted form of {term.term!r}.",
                            [],
                            {"term": term.term, "category": term.category},
                        )
                    )
            for phrase, _term in self.glossary.permitted_phrases:
                for match in _phrase_matches(analysis_text, phrase):
                    if _overlaps((match.start(), match.end()), covered):
                        continue
                    covered.append((match.start(), match.end()))
                    coverage["glossary_matches"] += 1

        for match in re.finditer(";", analysis_text):
            findings.append(
                self._finding(
                    block,
                    match.start(),
                    match.end(),
                    "STE-PUN-001",
                    "8.1",
                    "exact",
                    "error",
                    "high",
                    "Semicolons are not permitted.",
                    "Use a period or restructure the information.",
                    [],
                    {},
                )
            )
        for match in CONTRACTION_RE.finditer(analysis_text):
            findings.append(
                self._finding(
                    block,
                    match.start(),
                    match.end(),
                    "STE-GRM-001",
                    "4.1",
                    "exact",
                    "error",
                    "high",
                    f"Contraction: {match.group(0)}",
                    "Write the complete words.",
                    [],
                    {},
                )
            )

        for match in WORD_RE.finditer(analysis_text):
            span = (match.start(), match.end())
            if _overlaps(span, covered):
                continue
            word = match.group(0)
            coverage["candidate_terms"] += 1
            evidence = self._lookup(word)
            if evidence:
                coverage["dictionary_matches"] += 1
                continue
            location = block.location(*span)
            normalized = word.casefold()
            unresolved.setdefault(normalized, []).append(location)
            coverage["unresolved_occurrences"] += 1
            findings.append(
                self._finding(
                    block,
                    *span,
                    "STE-LEX-001",
                    "1.1",
                    "exact",
                    "warning",
                    "high",
                    f"No permitted dictionary or glossary form was found for {word!r}.",
                    "Confirm the official dictionary form or add an approved, sourced project term.",
                    [],
                    {},
                )
            )

        sentences = _sentence_ranges(block.prepared)
        limit = 20 if block.mode == "procedure" else 25
        check_id = "STE-SEN-001" if block.mode == "procedure" else "STE-SEN-002"
        for start, end in sentences:
            sentence_count_text = count_text[start:end]
            word_count = _count_words(sentence_count_text)
            if word_count > limit:
                findings.append(
                    self._finding(
                        block,
                        start,
                        end,
                        check_id,
                        "5.1" if block.mode == "procedure" else "6.1",
                        "exact",
                        "error",
                        "high",
                        f"{block.mode.title()} sentence has {word_count} words; the limit is {limit}.",
                        "Split or rewrite the sentence without changing its technical meaning.",
                        [],
                        {"word_count": word_count, "limit": limit},
                    )
                )
            self._heuristics(block, start, end, analysis_text[start:end], findings)

        if block.paragraph and block.mode == "description" and len(sentences) > 6:
            findings.append(
                self._finding(
                    block,
                    sentences[6][0],
                    sentences[-1][1],
                    "STE-PAR-001",
                    "6.2",
                    "exact",
                    "error",
                    "high",
                    f"Descriptive paragraph has {len(sentences)} sentences; the limit is 6.",
                    "Split the paragraph by topic.",
                    [],
                    {"sentence_count": len(sentences), "limit": 6},
                )
            )
        if block.safety:
            safety_text = block.prepared.casefold()
            consequence = re.search(
                r"\b(?:can|could|will|may|cause|result|injury|death|damage|fire)\b",
                safety_text,
            )
            first_word = WORD_RE.search(safety_text)
            condition = re.search(
                r"^\s*(?:if|when|before|after|during|while|unless|make sure|do not|never|always)\b",
                safety_text,
            )
            command = False
            if first_word:
                command = self._starts_with_known_verb(safety_text)
            missing = []
            if not (condition or command):
                missing.append("command_or_condition")
            if not consequence:
                missing.append("possible_result")
            if missing:
                findings.append(
                    self._finding(
                        block,
                        0,
                        len(block.prepared),
                        "STE-HEU-007",
                        "7.1",
                        "heuristic",
                        "warning",
                        "medium",
                        "Safety statement might not contain a command or condition and a possible result.",
                        "Have a qualified reviewer confirm the risk, command or condition, and consequence.",
                        [],
                        {"possibly_missing": missing},
                    )
                )

    def _heuristics(
        self,
        block: Block,
        start: int,
        end: int,
        sentence: str,
        findings: list[dict[str, Any]],
    ) -> None:
        heuristic_specs = (
            (
                PASSIVE_RE,
                "STE-HEU-001",
                "Possible passive voice.",
                "Prefer active voice when the agent is known.",
            ),
            (
                COMPLEX_VERB_RE,
                "STE-HEU-002",
                "Possible complex verb construction.",
                "Use a permitted simple tense when it preserves the meaning.",
            ),
        )
        for pattern, check_id, message, suggestion in heuristic_specs:
            match = pattern.search(sentence)
            if match:
                findings.append(
                    self._finding(
                        block,
                        start + match.start(),
                        start + match.end(),
                        check_id,
                        "3.1",
                        "heuristic",
                        "warning",
                        "medium",
                        message,
                        suggestion,
                        [],
                        {},
                    )
                )
        ing = next(
            (
                match
                for match in re.finditer(r"\b[A-Za-z]+ing\b", sentence, re.IGNORECASE)
                if not self._is_permitted_ing_noun(match.group(0))
            ),
            None,
        )
        if ing:
            findings.append(
                self._finding(
                    block,
                    start + ing.start(),
                    start + ing.end(),
                    "STE-HEU-003",
                    "3.2",
                    "heuristic",
                    "warning",
                    "medium",
                    "Questionable -ing form.",
                    "Confirm that the form is a permitted technical noun or modifier.",
                    [],
                    {},
                )
            )
        words = list(WORD_RE.finditer(sentence))
        run: list[re.Match[str]] = []
        for word in words + [None]:
            if word is not None and word.group(0).casefold() not in NOUN_GROUP_STOP:
                run.append(word)
                continue
            if len(run) >= 4:
                findings.append(
                    self._finding(
                        block,
                        start + run[0].start(),
                        start + run[-1].end(),
                        "STE-HEU-004",
                        "2.1",
                        "heuristic",
                        "warning",
                        "low",
                        "Possible long noun group.",
                        "Confirm the approved technical noun and use a clear shorter form when necessary.",
                        [],
                        {},
                    )
                )
                break
            run = []
        if block.mode == "procedure" and re.search(
            r"\band\s+(?:then\s+)?[A-Za-z]+", sentence, re.IGNORECASE
        ):
            conjunction = re.search(r"\band\b", sentence, re.IGNORECASE)
            assert conjunction is not None
            findings.append(
                self._finding(
                    block,
                    start + conjunction.start(),
                    start + conjunction.end(),
                    "STE-HEU-005",
                    "5.2",
                    "heuristic",
                    "warning",
                    "low",
                    "Possible multiple instructions in one sentence.",
                    "Use one instruction per sentence unless the actions occur at the same time.",
                    [],
                    {},
                )
            )
        first_word = WORD_RE.search(sentence)
        if block.note and first_word and self._starts_with_known_verb(sentence):
            findings.append(
                self._finding(
                    block,
                    start + first_word.start(),
                    start + first_word.end(),
                    "STE-HEU-006",
                    "5.3",
                    "heuristic",
                    "warning",
                    "medium",
                    "A note might contain a command.",
                    "Move required actions to a procedural step.",
                    [],
                    {},
                )
            )

    def _lookup(self, word: str) -> list[dict[str, Any]]:
        normalized = word.casefold()
        if normalized not in self._lookup_cache:
            self._lookup_cache[normalized] = self.dictionary.lookup(normalized)
        return self._lookup_cache[normalized]

    def _starts_with_known_verb(self, text: str) -> bool:
        first_word = WORD_RE.search(text)
        if not first_word:
            return False
        candidate = first_word.group(0).casefold()
        if candidate in COMMON_IMPERATIVES or any(
            re.search(r"\b(?:v|verb)\b", entry["part_of_speech"], re.IGNORECASE)
            for entry in self._lookup(candidate)
        ):
            return True
        if not self.glossary:
            return False
        remaining = text[first_word.start() :]
        return any(
            term.category == "technical_verb"
            and any(match.start() == 0 for match in _phrase_matches(remaining, form))
            for term in self.glossary.terms
            for form in term.forms
        )

    def _is_permitted_ing_noun(self, word: str) -> bool:
        candidate = word.casefold()
        if any(
            re.search(r"\b(?:n|noun)\b", entry["part_of_speech"], re.IGNORECASE)
            for entry in self._lookup(candidate)
        ):
            return True
        if not self.glossary:
            return False
        return any(
            term.category == "technical_noun"
            and any(candidate in form.casefold().split() for form in term.forms)
            for term in self.glossary.terms
        )

    @staticmethod
    def _finding(
        block: Block,
        start: int,
        end: int,
        check_id: str,
        rule_id: str,
        mode: str,
        severity: str,
        confidence: str,
        message: str,
        suggestion: str,
        evidence: list[dict[str, Any]],
        details: dict[str, Any],
    ) -> dict[str, Any]:
        excerpt = re.sub(r"\s+", " ", block.original[start:end]).strip()
        if len(excerpt) > 160:
            excerpt = excerpt[:157].rstrip() + "..."
        return {
            "rule_id": rule_id,
            "check_id": check_id,
            "mode": mode,
            "severity": severity,
            "confidence": confidence,
            "location": block.location(start, end),
            "excerpt": excerpt,
            "message": message,
            "suggestion": suggestion,
            "dictionary_evidence": evidence[:3],
            "details": details,
        }


def _overlaps(span: tuple[int, int], ranges: Iterable[tuple[int, int]]) -> bool:
    return any(span[0] < end and start < span[1] for start, end in ranges)
