import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
CLI = SKILL_DIR / "scripts" / "ste100"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from ste100_index import DictionaryEntry, ExtractionManifest, IndexStore  # noqa: E402


def install_test_index(data_dir: str) -> None:
    root = Path(data_dir)
    source = root / "source.pdf"
    source.write_bytes(b"source used only to calculate provenance")
    entries = [
        DictionaryEntry(
            headword="alpha",
            permitted_forms=("alpha", "alphas"),
            part_of_speech="n",
            meaning="An invented item for a parser test",
            alternatives="use bravo",
            examples="Use alpha.",
            page_start=300,
            page_end=300,
            font_name="Helvetica",
            font_size=10.0,
            source_bbox=(40.0, 80.0, 500.0, 100.0),
        ),
        DictionaryEntry(
            headword="bravo",
            permitted_forms=("bravo",),
            part_of_speech="v",
            meaning="An invented action",
            alternatives="",
            examples="Bravo the item.",
            page_start=301,
            page_end=301,
            font_name="Helvetica",
            font_size=10.0,
            source_bbox=(40.0, 80.0, 500.0, 100.0),
        ),
        DictionaryEntry(
            headword="and",
            permitted_forms=("and",),
            part_of_speech="conj",
            meaning="Joins words",
            alternatives="",
            examples="Alpha and bravo.",
            page_start=302,
            page_end=302,
            font_name="Helvetica",
            font_size=10.0,
            source_bbox=(40.0, 80.0, 500.0, 100.0),
        ),
    ]
    IndexStore(root).install(
        source,
        entries,
        ExtractionManifest(434, (300, 301), (40, 150, 250, 430), 200_000),
    )


class DoctorCommandTest(unittest.TestCase):
    def test_reports_a_missing_index_as_a_setup_error(self):
        self.assertTrue(CLI.exists(), "the ste100 executable must exist")

        with tempfile.TemporaryDirectory() as data_dir:
            environment = os.environ.copy()
            environment["STE100_DATA_DIR"] = data_dir

            result = subprocess.run(
                [str(CLI), "doctor", "--format", "json"],
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )

        self.assertEqual(2, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("index_not_found", payload["error"]["code"])
        self.assertIn("ste100 setup --pdf", payload["error"]["message"])

    def test_reports_index_provenance_without_network_access(self):
        with tempfile.TemporaryDirectory() as data_dir:
            install_test_index(data_dir)
            environment = os.environ.copy()
            environment["STE100_DATA_DIR"] = data_dir
            environment["HTTP_PROXY"] = "http://127.0.0.1:1"
            environment["HTTPS_PROXY"] = "http://127.0.0.1:1"

            result = subprocess.run(
                [str(CLI), "doctor", "--format", "json"],
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("ready", payload["status"])
        self.assertEqual(9, payload["standard"]["issue"])
        self.assertTrue(payload["offline"])


class DictionaryCommandTest(unittest.TestCase):
    def test_lookup_returns_only_query_specific_evidence(self):
        with tempfile.TemporaryDirectory() as data_dir:
            install_test_index(data_dir)
            environment = os.environ.copy()
            environment["STE100_DATA_DIR"] = data_dir

            result = subprocess.run(
                [
                    str(CLI),
                    "lookup",
                    "ALPHAS",
                    "--part-of-speech",
                    "n",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(1, payload["count"])
        self.assertEqual("alpha", payload["results"][0]["headword"])
        self.assertEqual(
            ["alpha", "alphas"], payload["results"][0].get("permitted_forms")
        )
        self.assertIn("human review", payload["notice"])

    def test_search_rejects_an_empty_query_instead_of_exporting_the_dictionary(self):
        with tempfile.TemporaryDirectory() as data_dir:
            install_test_index(data_dir)
            environment = os.environ.copy()
            environment["STE100_DATA_DIR"] = data_dir

            result = subprocess.run(
                [str(CLI), "search", " ", "--limit", "999", "--format", "json"],
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )

        self.assertEqual(2, result.returncode)
        self.assertEqual("query_invalid", json.loads(result.stdout)["error"]["code"])

    def test_search_rejects_a_nonpositive_limit(self):
        with tempfile.TemporaryDirectory() as data_dir:
            install_test_index(data_dir)
            environment = os.environ.copy()
            environment["STE100_DATA_DIR"] = data_dir

            result = subprocess.run(
                [str(CLI), "search", "alpha", "--limit", "0", "--format", "json"],
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )

        self.assertEqual(2, result.returncode)
        self.assertIn("positive", json.loads(result.stdout)["error"]["message"])


class SetupCommandTest(unittest.TestCase):
    def test_rejects_a_structurally_incomplete_pdf_without_copying_or_mutating_it(self):
        with tempfile.TemporaryDirectory() as data_dir:
            source = Path(data_dir) / "not-issue-9.pdf"
            source.write_bytes(b"%PDF-1.4\n%%EOF\n")
            before = source.read_bytes()
            private_data = Path(data_dir) / "private"
            environment = os.environ.copy()
            environment["STE100_DATA_DIR"] = str(private_data)

            result = subprocess.run(
                [str(CLI), "setup", "--pdf", str(source), "--format", "json"],
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )
            after = source.read_bytes()
            private_data_created = private_data.exists()

        self.assertEqual(2, result.returncode)
        self.assertEqual("setup_failed", json.loads(result.stdout)["error"]["code"])
        self.assertEqual(before, after)
        self.assertFalse(private_data_created)


class GlossaryCommandTest(unittest.TestCase):
    def test_invalid_glossary_is_an_input_error(self):
        with tempfile.TemporaryDirectory() as directory:
            glossary = Path(directory) / "glossary.yaml"
            glossary.write_text(
                """\
version: 1
scope: partial
terms:
  - term: widget
    category: technical_noun
    forms: [widget]
""",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    str(CLI),
                    "glossary",
                    "validate",
                    str(glossary),
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(2, result.returncode)
        self.assertEqual("glossary_invalid", json.loads(result.stdout)["error"]["code"])


class AnalysisCommandTest(unittest.TestCase):
    def test_clean_check_returns_ready_for_human_review(self):
        with tempfile.TemporaryDirectory() as data_dir:
            install_test_index(data_dir)
            source = Path(data_dir) / "source.txt"
            source.write_text("alpha.\n", encoding="utf-8")
            environment = os.environ.copy()
            environment["STE100_DATA_DIR"] = data_dir

            result = subprocess.run(
                [str(CLI), "check", str(source), "--format", "json"],
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("ready_for_human_review", payload["result"])
        self.assertEqual(
            "preflight_not_certification", payload["standard"]["assessment"]
        )

    def test_incomplete_coverage_fails_even_at_the_error_threshold(self):
        with tempfile.TemporaryDirectory() as data_dir:
            install_test_index(data_dir)
            source = Path(data_dir) / "source.txt"
            source.write_text("unknownterm.\n", encoding="utf-8")
            environment = os.environ.copy()
            environment["STE100_DATA_DIR"] = data_dir

            result = subprocess.run(
                [
                    str(CLI),
                    "check",
                    str(source),
                    "--format",
                    "json",
                    "--fail-on",
                    "error",
                ],
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )

        self.assertEqual(1, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual("incomplete", payload["coverage"]["status"])
        self.assertEqual("unknownterm", payload["unresolved_terms"][0]["term"])

    def test_heuristic_warning_obeys_the_selected_failure_threshold(self):
        with tempfile.TemporaryDirectory() as data_dir:
            install_test_index(data_dir)
            source = Path(data_dir) / "source.md"
            source.write_text("1. alpha and alpha.\n", encoding="utf-8")
            environment = os.environ.copy()
            environment["STE100_DATA_DIR"] = data_dir

            error_threshold = subprocess.run(
                [
                    str(CLI),
                    "check",
                    str(source),
                    "--format",
                    "json",
                    "--fail-on",
                    "error",
                ],
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )
            warning_threshold = subprocess.run(
                [
                    str(CLI),
                    "check",
                    str(source),
                    "--format",
                    "json",
                    "--fail-on",
                    "warning",
                ],
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )

        self.assertEqual(0, error_threshold.returncode)
        self.assertEqual(1, warning_threshold.returncode)
        findings = json.loads(error_threshold.stdout)["findings"]
        self.assertEqual(
            "warning",
            next(item for item in findings if item["check_id"] == "STE-HEU-005")[
                "severity"
            ],
        )

    def test_report_writes_markdown_without_modifying_the_source(self):
        with tempfile.TemporaryDirectory() as data_dir:
            install_test_index(data_dir)
            source = Path(data_dir) / "source.txt"
            report = Path(data_dir) / "report.md"
            source.write_text("alpha.\n", encoding="utf-8")
            before = source.read_bytes()
            environment = os.environ.copy()
            environment["STE100_DATA_DIR"] = data_dir

            result = subprocess.run(
                [
                    str(CLI),
                    "report",
                    str(source),
                    "--format",
                    "markdown",
                    "--output",
                    str(report),
                ],
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )

            after = source.read_bytes()
            report_text = report.read_text(encoding="utf-8")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)
        self.assertEqual(before, after)
        self.assertIn("preflight report", report_text)
        self.assertIn(
            "not a compliance, certification, or verification statement", report_text
        )

    def test_output_cannot_overwrite_the_input(self):
        with tempfile.TemporaryDirectory() as data_dir:
            install_test_index(data_dir)
            source = Path(data_dir) / "source.txt"
            source.write_text("alpha.\n", encoding="utf-8")
            environment = os.environ.copy()
            environment["STE100_DATA_DIR"] = data_dir

            result = subprocess.run(
                [
                    str(CLI),
                    "check",
                    str(source),
                    "--format",
                    "json",
                    "--output",
                    str(source),
                ],
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )

            unchanged = source.read_text(encoding="utf-8")

        self.assertEqual(2, result.returncode)
        self.assertEqual("alpha.\n", unchanged)
        self.assertEqual("analysis_failed", json.loads(result.stdout)["error"]["code"])


class RuntimePrerequisiteTest(unittest.TestCase):
    def test_executable_explains_how_to_install_uv_when_it_is_unavailable(self):
        environment = os.environ.copy()
        environment["PATH"] = "/usr/bin:/bin"

        result = subprocess.run(
            [str(CLI), "doctor"],
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )

        self.assertEqual(2, result.returncode)
        self.assertIn("requires uv", result.stderr)
        self.assertIn("docs.astral.sh/uv", result.stderr)


if __name__ == "__main__":
    unittest.main()
