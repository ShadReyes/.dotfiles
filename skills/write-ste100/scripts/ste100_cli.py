from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Sequence

from ste100_index import (
    DictionaryIndex,
    IndexError as DictionaryIndexError,
    IndexStore,
    Issue9PdfParser,
    PdfStructureError,
)
from ste100_glossary import GlossaryValidationError, load_glossary
from ste100_analyzer import AnalysisError, Analyzer


EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_ERROR = 2


def data_root() -> Path:
    configured = os.environ.get("STE100_DATA_DIR")
    if configured:
        return Path(configured).expanduser()
    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        return Path(xdg_data).expanduser() / "ste100"
    return Path.home() / ".local" / "share" / "ste100"


def emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    error = payload.get("error")
    if error:
        print(f"ERROR [{error['code']}]: {error['message']}")
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")


def find_index() -> Path | None:
    issue_dir = data_root() / "issue-9"
    if not issue_dir.is_dir():
        return None
    candidates = list(issue_dir.glob("*/dictionary.sqlite3"))
    return (
        max(candidates, key=lambda path: path.stat().st_mtime) if candidates else None
    )


def doctor(output_format: str) -> int:
    index = find_index()
    if index is None:
        emit(
            {
                "error": {
                    "code": "index_not_found",
                    "message": "No private Issue 9 index is available. Run ste100 setup --pdf PATH.",
                }
            },
            output_format,
        )
        return EXIT_ERROR
    try:
        dictionary = DictionaryIndex(index)
        metadata = dictionary.metadata()
    except DictionaryIndexError as error:
        emit({"error": {"code": "index_invalid", "message": str(error)}}, output_format)
        return EXIT_ERROR
    emit(
        {
            "status": "ready",
            "standard": {
                "name": "ASD-STE100",
                "issue": 9,
                "date": metadata["issue_date"],
            },
            "index": {
                "path": str(index),
                "source_sha256": metadata["source_sha256"],
                "parser_version": metadata["parser_version"],
                "schema_version": int(metadata["schema_version"]),
            },
            "offline": True,
        },
        output_format,
    )
    return EXIT_OK


def setup(pdf_path: Path, output_format: str) -> int:
    try:
        entries, extraction = Issue9PdfParser().validate_and_parse(pdf_path)
        index_path = IndexStore(data_root()).install(pdf_path, entries, extraction)
        metadata = DictionaryIndex(index_path).metadata()
    except (PdfStructureError, DictionaryIndexError, OSError) as error:
        emit({"error": {"code": "setup_failed", "message": str(error)}}, output_format)
        return EXIT_ERROR
    emit(
        {
            "status": "ready",
            "standard": {
                "name": "ASD-STE100",
                "issue": 9,
                "date": metadata["issue_date"],
            },
            "index": {
                "path": str(index_path),
                "source_sha256": metadata["source_sha256"],
                "parser_version": metadata["parser_version"],
                "schema_version": int(metadata["schema_version"]),
            },
            "message": "Private Issue 9 index created. The source PDF was not copied.",
        },
        output_format,
    )
    return EXIT_OK


def dictionary_command(
    command: str,
    value: str,
    output_format: str,
    part_of_speech: str | None = None,
    limit: int = 10,
) -> int:
    index_path = find_index()
    if index_path is None:
        emit(
            {
                "error": {
                    "code": "index_not_found",
                    "message": "No private Issue 9 index is available. Run ste100 setup --pdf PATH.",
                }
            },
            output_format,
        )
        return EXIT_ERROR
    try:
        dictionary = DictionaryIndex(index_path)
        if command == "search" and limit < 1:
            raise DictionaryIndexError("Search limit must be a positive integer")
        results = (
            dictionary.lookup(value, part_of_speech)
            if command == "lookup"
            else dictionary.search(value, limit)
        )
        metadata = dictionary.metadata()
    except DictionaryIndexError as error:
        emit({"error": {"code": "query_invalid", "message": str(error)}}, output_format)
        return EXIT_ERROR
    payload = {
        "standard": {"name": "ASD-STE100", "issue": 9, "date": metadata["issue_date"]},
        "index": {"source_sha256": metadata["source_sha256"]},
        "query": {
            "command": command,
            "value": value,
            **({"part_of_speech": part_of_speech} if part_of_speech else {}),
            **({"limit": min(max(limit, 1), 25)} if command == "search" else {}),
        },
        "count": len(results),
        "results": results,
        "notice": "Bounded dictionary evidence for preflight use; human review is required.",
    }
    emit(payload, output_format)
    return EXIT_OK if results else EXIT_FINDINGS


def validate_glossary(path: Path, output_format: str) -> int:
    try:
        glossary = load_glossary(path)
    except GlossaryValidationError as error:
        emit(
            {"error": {"code": "glossary_invalid", "message": str(error)}},
            output_format,
        )
        return EXIT_ERROR
    categories = {
        category: 0 for category in ("technical_noun", "technical_verb", "literal")
    }
    for term in glossary.terms:
        categories[term.category] += 1
    emit(
        {
            "status": "valid",
            "glossary": {
                "path": str(glossary.path),
                "sha256": glossary.sha256,
                "version": glossary.version,
                "scope": glossary.scope,
                "term_count": len(glossary.terms),
                "categories": categories,
            },
            "notice": "Validation does not approve or add terminology.",
        },
        output_format,
    )
    return EXIT_OK


def _text_analysis(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        f"Result: {payload['result']}",
        "Assessment: ASD-STE100 Issue 9 preflight; not certification",
        f"Coverage: {payload['coverage']['status']}",
        f"Findings: {summary['errors']} errors, {summary['warnings']} warnings",
    ]
    for finding in payload["findings"]:
        location = finding["location"]
        lines.append(
            f"{finding['severity'].upper()} {finding['check_id']} "
            f"{location['line']}:{location['column']} [{finding['mode']}] {finding['message']}"
        )
    lines.append("Human review is required for every result.")
    return "\n".join(lines) + "\n"


def _markdown_analysis(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# ASD-STE100 Issue 9 preflight report",
        "",
        "> This automated preflight is not a compliance, certification, or verification statement. Human review is required.",
        "",
        f"- Result: `{payload['result']}`",
        f"- Input: `{payload['input']['path']}`",
        f"- Input SHA-256: `{payload['input']['sha256']}`",
        f"- Dictionary source SHA-256: `{payload['index']['source_sha256']}`",
        f"- Coverage: `{payload['coverage']['status']}`",
        f"- Findings: {summary['errors']} errors, {summary['warnings']} warnings",
        "",
        "## Findings",
        "",
    ]
    if payload["findings"]:
        lines.extend(
            [
                "| Location | Check | Mode | Severity | Finding | Suggestion |",
                "|---|---|---|---|---|---|",
            ]
        )
        for finding in payload["findings"]:
            location = finding["location"]
            values = (
                f"{location['line']}:{location['column']}",
                finding["check_id"],
                finding["mode"],
                finding["severity"],
                finding["message"],
                finding["suggestion"],
            )
            escaped = [
                str(value).replace("|", "\\|").replace("\n", " ") for value in values
            ]
            lines.append("| " + " | ".join(escaped) + " |")
    else:
        lines.append("No automated findings.")
    lines.extend(["", "## Unresolved terms", ""])
    if payload["unresolved_terms"]:
        lines.extend(
            f"- `{item['term']}` ({len(item['occurrences'])} occurrences)"
            for item in payload["unresolved_terms"]
        )
    else:
        lines.append("None.")
    lines.extend(["", "## Human-review checklist", ""])
    lines.extend(f"- [ ] {item}" for item in payload["human_review_checklist"])
    return "\n".join(lines) + "\n"


def _write_output(path: Path, source: Path, content: str) -> None:
    if path.resolve() == source.resolve():
        raise AnalysisError("Output path must not overwrite the source file")
    if not path.parent.is_dir():
        raise AnalysisError(f"Output directory does not exist: {path.parent}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}-", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def analyze_command(
    source: Path,
    document_type: str,
    glossary_path: Path | None,
    output_format: str,
    output_path: Path | None,
    fail_on: str,
    report: bool,
) -> int:
    index_path = find_index()
    if index_path is None:
        emit(
            {
                "error": {
                    "code": "index_not_found",
                    "message": "No private Issue 9 index is available. Run ste100 setup --pdf PATH.",
                }
            },
            "json" if output_format == "json" else "text",
        )
        return EXIT_ERROR
    try:
        glossary = load_glossary(glossary_path) if glossary_path else None
        payload = Analyzer(DictionaryIndex(index_path), glossary).analyze(
            source, document_type
        )
        if output_format == "json":
            rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        elif report:
            rendered = _markdown_analysis(payload)
        else:
            rendered = _text_analysis(payload)
        if output_path:
            _write_output(output_path, source, rendered)
        else:
            sys.stdout.write(rendered)
    except (
        AnalysisError,
        GlossaryValidationError,
        DictionaryIndexError,
        OSError,
    ) as error:
        emit(
            {"error": {"code": "analysis_failed", "message": str(error)}},
            "json" if output_format == "json" else "text",
        )
        return EXIT_ERROR
    threshold_failure = any(
        finding["severity"] == "error"
        or (fail_on == "warning" and finding["severity"] == "warning")
        for finding in payload["findings"]
    )
    incomplete = payload["coverage"]["status"] != "complete"
    return EXIT_FINDINGS if threshold_failure or incomplete else EXIT_OK


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="ste100")
    commands = root.add_subparsers(dest="command", required=True)
    setup_parser = commands.add_parser("setup")
    setup_parser.add_argument("--pdf", required=True, type=Path)
    setup_parser.add_argument("--format", choices=("text", "json"), default="text")
    doctor_parser = commands.add_parser("doctor")
    doctor_parser.add_argument("--format", choices=("text", "json"), default="text")
    lookup_parser = commands.add_parser("lookup")
    lookup_parser.add_argument("word")
    lookup_parser.add_argument("--part-of-speech")
    lookup_parser.add_argument("--format", choices=("text", "json"), default="text")
    search_parser = commands.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--format", choices=("text", "json"), default="text")
    glossary_parser = commands.add_parser("glossary")
    glossary_commands = glossary_parser.add_subparsers(
        dest="glossary_command", required=True
    )
    glossary_validate = glossary_commands.add_parser("validate")
    glossary_validate.add_argument("path", type=Path)
    glossary_validate.add_argument("--format", choices=("text", "json"), default="text")
    check_parser = commands.add_parser("check")
    check_parser.add_argument("file", type=Path)
    check_parser.add_argument(
        "--type", choices=("auto", "procedure", "description"), default="auto"
    )
    check_parser.add_argument("--glossary", type=Path)
    check_parser.add_argument("--format", choices=("text", "json"), default="text")
    check_parser.add_argument("--output", type=Path)
    check_parser.add_argument(
        "--fail-on", choices=("error", "warning"), default="error"
    )
    report_parser = commands.add_parser("report")
    report_parser.add_argument("file", type=Path)
    report_parser.add_argument(
        "--type", choices=("auto", "procedure", "description"), default="auto"
    )
    report_parser.add_argument("--glossary", type=Path)
    report_parser.add_argument("--format", choices=("markdown", "json"), required=True)
    report_parser.add_argument("--output", type=Path, required=True)
    report_parser.add_argument(
        "--fail-on", choices=("error", "warning"), default="error"
    )
    return root


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    if arguments.command == "setup":
        return setup(arguments.pdf, arguments.format)
    if arguments.command == "doctor":
        return doctor(arguments.format)
    if arguments.command == "lookup":
        return dictionary_command(
            "lookup", arguments.word, arguments.format, arguments.part_of_speech
        )
    if arguments.command == "search":
        return dictionary_command(
            "search", arguments.query, arguments.format, limit=arguments.limit
        )
    if arguments.command == "glossary" and arguments.glossary_command == "validate":
        return validate_glossary(arguments.path, arguments.format)
    if arguments.command == "check":
        return analyze_command(
            arguments.file,
            arguments.type,
            arguments.glossary,
            arguments.format,
            arguments.output,
            arguments.fail_on,
            report=False,
        )
    if arguments.command == "report":
        return analyze_command(
            arguments.file,
            arguments.type,
            arguments.glossary,
            arguments.format,
            arguments.output,
            arguments.fail_on,
            report=True,
        )
    return EXIT_ERROR
