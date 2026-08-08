from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
from typing import Any

import pdfplumber
from pdfminer.pdfparser import PDFSyntaxError
from pdfplumber.utils.exceptions import PdfminerException


ISSUE = 9
ISSUE_DATE = "2025-01-15"
EXPECTED_PAGE_COUNT = 434
EXPECTED_UNIQUE_HEADWORDS = 875
PARSER_VERSION = "1.0.0"
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class DictionaryEntry:
    headword: str
    permitted_forms: tuple[str, ...]
    part_of_speech: str
    meaning: str
    alternatives: str
    examples: str
    page_start: int
    page_end: int
    font_name: str
    font_size: float
    source_bbox: tuple[float, float, float, float]


class PdfStructureError(ValueError):
    pass


class IndexError(ValueError):
    pass


@dataclass(frozen=True)
class ExtractionManifest:
    page_count: int
    table_pages: tuple[int, ...]
    column_geometry: tuple[float, float, float, float]
    embedded_text_characters: int


@dataclass
class _EntryBuilder:
    word_cell: list[str]
    part_of_speech: list[str]
    meaning: list[str]
    examples: list[str]
    page_start: int
    page_end: int
    font_name: str
    font_size: float
    x0: float
    top: float
    x1: float
    bottom: float

    def build(self) -> DictionaryEntry:
        raw_forms = re.split(r"\s*[,;/]\s*|\n+", " ".join(self.word_cell))
        forms = tuple(
            normalized for form in raw_forms if (normalized := _normalize_form(form))
        )
        if not forms:
            raise PdfStructureError(
                f"Entry on page {self.page_start} has no usable headword"
            )
        meaning = _join(self.meaning)
        alternatives = ""
        split = re.split(
            r"\bALTERNATIVES?\s*:\s*", meaning, maxsplit=1, flags=re.IGNORECASE
        )
        if len(split) == 2:
            meaning, alternatives = split[0].strip(), split[1].strip()
        return DictionaryEntry(
            headword=forms[0],
            permitted_forms=tuple(dict.fromkeys(forms)),
            part_of_speech=_join(self.part_of_speech),
            meaning=meaning,
            alternatives=alternatives,
            examples=_join(self.examples),
            page_start=self.page_start,
            page_end=self.page_end,
            font_name=self.font_name,
            font_size=self.font_size,
            source_bbox=(self.x0, self.top, self.x1, self.bottom),
        )


def _normalize_form(value: str) -> str:
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"\s+", " ", value).strip(" .").casefold()
    return value


def _join(parts: list[str]) -> str:
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def _group_lines(
    words: list[dict[str, Any]], tolerance: float = 3.0
) -> list[list[dict[str, Any]]]:
    lines: list[list[dict[str, Any]]] = []
    for word in sorted(
        words, key=lambda item: (round(float(item["top"]), 1), float(item["x0"]))
    ):
        if (
            not lines
            or abs(float(word["top"]) - float(lines[-1][0]["top"])) > tolerance
        ):
            lines.append([word])
        else:
            lines[-1].append(word)
    for line in lines:
        line.sort(key=lambda item: float(item["x0"]))
    return lines


def _header_columns(
    words: list[dict[str, Any]],
) -> tuple[float, tuple[float, float, float, float]] | None:
    for word_anchor in words:
        if str(word_anchor["text"]).upper() != "WORD":
            continue
        anchor_top = float(word_anchor["top"])
        band = [word for word in words if abs(float(word["top"]) - anchor_top) <= 25]
        part_anchors = [
            word
            for word in band
            if str(word["text"]).upper() == "PART"
            and float(word["x0"]) > float(word_anchor["x0"])
        ]
        approved_anchors = [
            word for word in band if str(word["text"]).upper() == "APPROVED"
        ]
        if not part_anchors or len(approved_anchors) < 2:
            continue
        word_x = float(word_anchor["x0"])
        part_x = min(float(word["x0"]) for word in part_anchors)
        approved = sorted(
            float(word["x0"]) for word in approved_anchors if float(word["x0"]) > part_x
        )
        if len(approved) < 2:
            continue
        columns = (word_x, part_x, approved[0], approved[-1])
        if not (columns[0] < columns[1] < columns[2] < columns[3]):
            raise PdfStructureError(
                "Dictionary table columns are not in the expected order"
            )
        if min(columns[index + 1] - columns[index] for index in range(3)) < 60:
            raise PdfStructureError("Dictionary table columns are too narrow")
        header_bottom = max(float(word["bottom"]) for word in band)
        return header_bottom, columns
    return None


class Issue9PdfParser:
    @staticmethod
    def validate_title_page_text(text: str) -> None:
        normalized = re.sub(r"\s+", " ", text).upper()
        required = ("ASD-STE100", "ISSUE 9")
        missing = [anchor for anchor in required if anchor not in normalized]
        has_issue_date = re.search(
            r"\b(?:JANUARY 15,? 2025|15 JANUARY 2025|2025-01-15)\b", normalized
        )
        if missing or not has_issue_date:
            raise PdfStructureError(
                "The PDF title page does not identify ASD-STE100 Issue 9 dated January 15, 2025"
            )

    def validate_and_parse(
        self, pdf_path: Path
    ) -> tuple[list[DictionaryEntry], ExtractionManifest]:
        if not pdf_path.is_file():
            raise PdfStructureError(f"PDF does not exist: {pdf_path}")
        if pdf_path.suffix.casefold() != ".pdf":
            raise PdfStructureError("The setup input must be a PDF")
        try:
            with pdfplumber.open(pdf_path) as document:
                page_count = len(document.pages)
                if page_count != EXPECTED_PAGE_COUNT:
                    raise PdfStructureError(
                        f"Issue 9 must contain {EXPECTED_PAGE_COUNT} pages; found {page_count}"
                    )
                first_text = document.pages[0].extract_text() or ""
                self.validate_title_page_text(first_text)
                embedded_text = sum(
                    len(page.extract_text() or "") for page in document.pages
                )
                if embedded_text < 100_000:
                    raise PdfStructureError(
                        "The PDF does not contain enough embedded text; OCR and scanned copies are not supported"
                    )
        except (PDFSyntaxError, PdfminerException) as error:
            raise PdfStructureError(f"The PDF cannot be parsed: {error}") from error

        entries = self.parse_tables(pdf_path)
        unique = {entry.headword for entry in entries}
        if len(unique) != EXPECTED_UNIQUE_HEADWORDS:
            raise PdfStructureError(
                f"Incomplete Issue 9 dictionary: expected {EXPECTED_UNIQUE_HEADWORDS} unique approved words; found {len(unique)}"
            )
        sequence = [entry.headword for entry in entries]
        if sequence != sorted(sequence):
            raise PdfStructureError(
                "Dictionary entries do not have the expected alphabetical progression"
            )
        manifest = self.inspect_tables(pdf_path)
        return entries, ExtractionManifest(
            page_count=page_count,
            table_pages=manifest.table_pages,
            column_geometry=manifest.column_geometry,
            embedded_text_characters=embedded_text,
        )

    def inspect_tables(self, pdf_path: Path) -> ExtractionManifest:
        table_pages: list[int] = []
        columns: tuple[float, float, float, float] | None = None
        text_characters = 0
        with pdfplumber.open(pdf_path) as document:
            for page_number, page in enumerate(document.pages, start=1):
                text_characters += len(page.extract_text() or "")
                words = page.extract_words(
                    extra_attrs=["fontname", "size"], use_text_flow=False
                )
                header = _header_columns(words)
                if header is None:
                    continue
                table_pages.append(page_number)
                candidate = header[1]
                if columns is None:
                    columns = candidate
                elif any(
                    abs(actual - expected) > 12
                    for actual, expected in zip(candidate, columns)
                ):
                    raise PdfStructureError(
                        f"Dictionary column geometry changed on page {page_number}"
                    )
        if not table_pages or columns is None:
            raise PdfStructureError(
                "No four-column Issue 9 dictionary tables were found"
            )
        return ExtractionManifest(
            len(document.pages), tuple(table_pages), columns, text_characters
        )

    def parse_tables(self, pdf_path: Path) -> list[DictionaryEntry]:
        entries: list[DictionaryEntry] = []
        current: _EntryBuilder | None = None
        reference_columns: tuple[float, float, float, float] | None = None
        table_pages = 0

        with pdfplumber.open(pdf_path) as document:
            for page_number, page in enumerate(document.pages, start=1):
                words = page.extract_words(
                    extra_attrs=["fontname", "size"], use_text_flow=False
                )
                header = _header_columns(words)
                if header is None:
                    continue
                table_pages += 1
                header_bottom, columns = header
                if reference_columns is None:
                    reference_columns = columns
                elif any(
                    abs(actual - expected) > 12
                    for actual, expected in zip(columns, reference_columns)
                ):
                    raise PdfStructureError(
                        f"Dictionary column geometry changed on page {page_number}"
                    )

                boundaries = tuple(
                    (columns[index] + columns[index + 1]) / 2 for index in range(3)
                )
                body = [
                    word
                    for word in words
                    if float(word["top"]) > header_bottom + 4
                    and float(word["bottom"]) < float(page.height) - 34
                ]
                for line in _group_lines(body):
                    cells: list[list[dict[str, Any]]] = [[], [], [], []]
                    for word in line:
                        x0 = float(word["x0"])
                        column = (
                            0
                            if x0 < boundaries[0]
                            else 1
                            if x0 < boundaries[1]
                            else 2
                            if x0 < boundaries[2]
                            else 3
                        )
                        cells[column].append(word)
                    text = [
                        _join([str(word["text"]) for word in cell]) for cell in cells
                    ]
                    if not any(text):
                        continue
                    starts_entry = bool(text[0] and text[1])
                    if starts_entry:
                        if current is not None:
                            entries.append(current.build())
                        source_words = [word for cell in cells for word in cell]
                        first = source_words[0]
                        current = _EntryBuilder(
                            word_cell=[text[0]],
                            part_of_speech=[text[1]],
                            meaning=[text[2]] if text[2] else [],
                            examples=[text[3]] if text[3] else [],
                            page_start=page_number,
                            page_end=page_number,
                            font_name=str(first.get("fontname", "")),
                            font_size=float(first.get("size", 0.0)),
                            x0=min(float(word["x0"]) for word in source_words),
                            top=min(float(word["top"]) for word in source_words),
                            x1=max(float(word["x1"]) for word in source_words),
                            bottom=max(float(word["bottom"]) for word in source_words),
                        )
                        continue
                    if current is None:
                        raise PdfStructureError(
                            f"Orphan dictionary fragment on page {page_number}"
                        )
                    if text[0]:
                        current.word_cell.append(text[0])
                    if text[1]:
                        current.part_of_speech.append(text[1])
                    if text[2]:
                        current.meaning.append(text[2])
                    if text[3]:
                        current.examples.append(text[3])
                    current.page_end = page_number
                    source_words = [word for cell in cells for word in cell]
                    current.x1 = max(
                        current.x1, *(float(word["x1"]) for word in source_words)
                    )
                    current.bottom = max(
                        current.bottom,
                        *(float(word["bottom"]) for word in source_words),
                    )

        if current is not None:
            entries.append(current.build())
        if table_pages == 0:
            raise PdfStructureError(
                "No four-column Issue 9 dictionary tables were found"
            )
        if not entries:
            raise PdfStructureError("Dictionary tables did not contain entries")
        return entries


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dictionary_checksum(entries: list[DictionaryEntry]) -> str:
    rows = [
        {
            "headword": entry.headword,
            "forms": entry.permitted_forms,
            "pos": entry.part_of_speech,
            "meaning": entry.meaning,
            "alternatives": entry.alternatives,
            "page_start": entry.page_start,
            "page_end": entry.page_end,
        }
        for entry in entries
    ]
    encoded = json.dumps(
        rows, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


class IndexStore:
    def __init__(self, root: Path):
        self.root = root

    def install(
        self,
        source_pdf: Path,
        entries: list[DictionaryEntry],
        extraction: ExtractionManifest,
    ) -> Path:
        if not entries:
            raise IndexError("Refusing to create an incomplete dictionary index")
        source_hash = sha256_file(source_pdf)
        issue_dir = self.root / "issue-9"
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self.root, 0o700)
        issue_dir.mkdir(mode=0o700, exist_ok=True)
        os.chmod(issue_dir, 0o700)
        target_dir = issue_dir / source_hash
        target_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(target_dir, 0o700)
        target = target_dir / "dictionary.sqlite3"
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".dictionary-", suffix=".tmp", dir=target_dir
        )
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            connection = sqlite3.connect(temporary)
            try:
                connection.executescript(
                    """
                    PRAGMA journal_mode=DELETE;
                    PRAGMA foreign_keys=ON;
                    CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                    CREATE TABLE entries (
                        id INTEGER PRIMARY KEY,
                        headword TEXT NOT NULL,
                        part_of_speech TEXT NOT NULL,
                        meaning TEXT NOT NULL,
                        alternatives TEXT NOT NULL,
                        examples TEXT NOT NULL,
                        page_start INTEGER NOT NULL,
                        page_end INTEGER NOT NULL,
                        font_name TEXT NOT NULL,
                        font_size REAL NOT NULL,
                        source_bbox TEXT NOT NULL
                    );
                    CREATE TABLE forms (
                        form TEXT NOT NULL,
                        entry_id INTEGER NOT NULL REFERENCES entries(id),
                        PRIMARY KEY (form, entry_id)
                    );
                    CREATE INDEX entries_headword ON entries(headword);
                    CREATE INDEX entries_meaning ON entries(meaning);
                    """
                )
                manifest = {
                    "issue": ISSUE,
                    "issue_date": ISSUE_DATE,
                    "source_sha256": source_hash,
                    "parser_version": PARSER_VERSION,
                    "schema_version": SCHEMA_VERSION,
                    "page_count": extraction.page_count,
                    "table_pages": extraction.table_pages,
                    "column_geometry": extraction.column_geometry,
                    "embedded_text_characters": extraction.embedded_text_characters,
                    "entry_count": len(entries),
                    "unique_headword_count": len({entry.headword for entry in entries}),
                    "dictionary_checksum": dictionary_checksum(entries),
                }
                metadata = {
                    "issue": str(ISSUE),
                    "issue_date": ISSUE_DATE,
                    "source_sha256": source_hash,
                    "parser_version": PARSER_VERSION,
                    "schema_version": str(SCHEMA_VERSION),
                    "extraction_manifest": json.dumps(
                        manifest, separators=(",", ":"), sort_keys=True
                    ),
                }
                connection.executemany(
                    "INSERT INTO metadata VALUES (?, ?)", metadata.items()
                )
                for entry in entries:
                    cursor = connection.execute(
                        """INSERT INTO entries
                           (headword, part_of_speech, meaning, alternatives, examples,
                            page_start, page_end, font_name, font_size, source_bbox)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            entry.headword,
                            entry.part_of_speech,
                            entry.meaning,
                            entry.alternatives,
                            entry.examples,
                            entry.page_start,
                            entry.page_end,
                            entry.font_name,
                            entry.font_size,
                            json.dumps(entry.source_bbox),
                        ),
                    )
                    connection.executemany(
                        "INSERT INTO forms VALUES (?, ?)",
                        ((form, cursor.lastrowid) for form in entry.permitted_forms),
                    )
                connection.commit()
            finally:
                connection.close()
            os.chmod(temporary, 0o600)
            os.replace(temporary, target)
            os.chmod(target, 0o600)
        except sqlite3.Error as error:
            temporary.unlink(missing_ok=True)
            raise IndexError(f"Could not create dictionary index: {error}") from error
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
        return target


class DictionaryIndex:
    def __init__(self, path: Path):
        if not path.is_file():
            raise IndexError(f"Dictionary index does not exist: {path}")
        self.path = path
        try:
            metadata = self.metadata()
        except sqlite3.Error as error:
            raise IndexError(f"Dictionary index is not readable: {error}") from error
        if metadata.get("schema_version") != str(SCHEMA_VERSION):
            raise IndexError(
                "Dictionary index schema is not supported; run ste100 setup again"
            )
        if metadata.get("parser_version") != PARSER_VERSION:
            raise IndexError(
                "Dictionary parser version changed; run ste100 setup again"
            )
        if (
            metadata.get("issue") != str(ISSUE)
            or metadata.get("issue_date") != ISSUE_DATE
        ):
            raise IndexError(
                "Dictionary index is not ASD-STE100 Issue 9; run ste100 setup again"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        return connection

    def metadata(self) -> dict[str, str]:
        with self._connect() as connection:
            return {
                row["key"]: row["value"]
                for row in connection.execute("SELECT key, value FROM metadata")
            }

    def lookup(
        self, word: str, part_of_speech: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        normalized = _normalize_form(word)
        if not normalized or len(normalized) > 100:
            raise IndexError("Lookup word must contain 1 to 100 characters")
        query = """
            SELECT DISTINCT e.*,
                (SELECT group_concat(form, char(31))
                   FROM (SELECT form FROM forms WHERE entry_id = e.id ORDER BY form)
                ) AS permitted_forms
            FROM entries e
            JOIN forms f ON f.entry_id = e.id
            WHERE f.form = ?
        """
        parameters: list[Any] = [normalized]
        if part_of_speech:
            query += " AND lower(e.part_of_speech) = lower(?)"
            parameters.append(part_of_speech.strip())
        query += " ORDER BY e.headword, e.part_of_speech, e.page_start LIMIT ?"
        parameters.append(min(max(limit, 1), 10))
        with self._connect() as connection:
            return [_public_entry(row) for row in connection.execute(query, parameters)]

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        normalized = re.sub(r"\s+", " ", query).strip().casefold()
        if len(normalized) < 2 or len(normalized) > 100:
            raise IndexError("Search query must contain 2 to 100 characters")
        bounded_limit = min(max(limit, 1), 25)
        escaped = normalized.replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped}%"
        with self._connect() as connection:
            rows = connection.execute(
                """SELECT DISTINCT e.*,
                       (SELECT group_concat(form, char(31))
                          FROM (SELECT form FROM forms WHERE entry_id = e.id ORDER BY form)
                       ) AS permitted_forms
                   FROM entries e
                   LEFT JOIN forms f ON f.entry_id = e.id
                   WHERE lower(e.headword) LIKE ? ESCAPE '\\'
                      OR lower(f.form) LIKE ? ESCAPE '\\'
                      OR lower(e.meaning) LIKE ? ESCAPE '\\'
                      OR lower(e.alternatives) LIKE ? ESCAPE '\\'
                   ORDER BY e.headword, e.part_of_speech, e.page_start LIMIT ?""",
                (pattern, pattern, pattern, pattern, bounded_limit),
            )
            return [_public_entry(row) for row in rows]


def _public_entry(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "headword": row["headword"],
        "permitted_forms": row["permitted_forms"].split("\x1f")
        if row["permitted_forms"]
        else [],
        "part_of_speech": row["part_of_speech"],
        "meaning": row["meaning"],
        "alternatives": row["alternatives"],
        "examples": row["examples"],
        "pages": [row["page_start"], row["page_end"]],
    }
