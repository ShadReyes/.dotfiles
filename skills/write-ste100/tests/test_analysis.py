import sys
from pathlib import Path
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
sys.path.insert(0, str(SKILL_DIR / "tests"))

from ste100_analyzer import Analyzer  # noqa: E402
from ste100_glossary import load_glossary  # noqa: E402
from ste100_index import DictionaryIndex  # noqa: E402
from test_cli import install_test_index  # noqa: E402


class SentenceLengthTest(unittest.TestCase):
    def test_procedure_limit_is_twenty_words(self):
        with tempfile.TemporaryDirectory() as directory:
            install_test_index(directory)
            dictionary_path = next(Path(directory).glob("issue-9/*/dictionary.sqlite3"))
            twenty = Path(directory) / "twenty.md"
            twenty_one = Path(directory) / "twenty-one.md"
            twenty.write_text(
                "1. " + " ".join(["alpha"] * 20) + ".\n", encoding="utf-8"
            )
            twenty_one.write_text(
                "1. " + " ".join(["alpha"] * 21) + ".\n", encoding="utf-8"
            )
            analyzer = Analyzer(DictionaryIndex(dictionary_path))

            accepted = analyzer.analyze(twenty)
            rejected = analyzer.analyze(twenty_one)

        self.assertNotIn(
            "STE-SEN-001", [finding["check_id"] for finding in accepted["findings"]]
        )
        length_findings = [
            finding
            for finding in rejected["findings"]
            if finding["check_id"] == "STE-SEN-001"
        ]
        self.assertEqual(1, len(length_findings))
        self.assertEqual(21, length_findings[0]["details"]["word_count"])
        self.assertEqual(1, length_findings[0]["location"]["line"])

    def test_description_limit_is_twenty_five_words(self):
        with tempfile.TemporaryDirectory() as directory:
            install_test_index(directory)
            dictionary = DictionaryIndex(
                next(Path(directory).glob("issue-9/*/dictionary.sqlite3"))
            )
            accepted_path = Path(directory) / "accepted.txt"
            rejected_path = Path(directory) / "rejected.txt"
            accepted_path.write_text(" ".join(["alpha"] * 25) + ".\n", encoding="utf-8")
            rejected_path.write_text(" ".join(["alpha"] * 26) + ".\n", encoding="utf-8")
            analyzer = Analyzer(dictionary)

            accepted = analyzer.analyze(accepted_path)
            rejected = analyzer.analyze(rejected_path)

        self.assertNotIn(
            "STE-SEN-002", [finding["check_id"] for finding in accepted["findings"]]
        )
        finding = next(
            finding
            for finding in rejected["findings"]
            if finding["check_id"] == "STE-SEN-002"
        )
        self.assertEqual({"word_count": 26, "limit": 25}, finding["details"])

    def test_word_count_applies_documented_exceptions_at_the_boundary(self):
        accepted_sentences = {
            "parentheses": " ".join(["alpha"] * 20)
            + " (these words do not add to the count).",
            "measurement": " ".join(["alpha"] * 19) + " 10 kg.",
            "identifier": " ".join(["alpha"] * 19) + " API_TOKEN.",
            "quoted text": " ".join(["alpha"] * 19) + ' "Big Product Name".',
            "proper name": " ".join(["alpha"] * 19) + " Big Product Name.",
            "hyphenation": " ".join(["alpha"] * 19) + " alpha-alpha.",
            "vertical-list colon": " ".join(["alpha"] * 20) + ":",
        }
        with tempfile.TemporaryDirectory() as directory:
            install_test_index(directory)
            dictionary = DictionaryIndex(
                next(Path(directory).glob("issue-9/*/dictionary.sqlite3"))
            )
            analyzer = Analyzer(dictionary)
            for label, sentence in accepted_sentences.items():
                with self.subTest(label=label):
                    path = Path(directory) / f"{label}.md"
                    path.write_text(f"1. {sentence}\n", encoding="utf-8")

                    result = analyzer.analyze(path)

                    self.assertNotIn(
                        "STE-SEN-001",
                        [finding["check_id"] for finding in result["findings"]],
                        label,
                    )

    def test_type_override_changes_the_sentence_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            install_test_index(directory)
            dictionary = DictionaryIndex(
                next(Path(directory).glob("issue-9/*/dictionary.sqlite3"))
            )
            path = Path(directory) / "source.txt"
            path.write_text(" ".join(["alpha"] * 21) + ".\n", encoding="utf-8")
            analyzer = Analyzer(dictionary)

            automatic = analyzer.analyze(path)
            procedure = analyzer.analyze(path, "procedure")

        self.assertNotIn(
            "STE-SEN-002", [finding["check_id"] for finding in automatic["findings"]]
        )
        self.assertIn(
            "STE-SEN-001", [finding["check_id"] for finding in procedure["findings"]]
        )


class ParagraphAndExactRuleTest(unittest.TestCase):
    def test_description_paragraph_limit_is_six_sentences(self):
        with tempfile.TemporaryDirectory() as directory:
            install_test_index(directory)
            dictionary = DictionaryIndex(
                next(Path(directory).glob("issue-9/*/dictionary.sqlite3"))
            )
            six = Path(directory) / "six.txt"
            seven = Path(directory) / "seven.txt"
            six.write_text(" ".join(["alpha."] * 6), encoding="utf-8")
            seven.write_text(" ".join(["alpha."] * 7), encoding="utf-8")
            analyzer = Analyzer(dictionary)

            accepted = analyzer.analyze(six)
            rejected = analyzer.analyze(seven)

        self.assertNotIn(
            "STE-PAR-001", [finding["check_id"] for finding in accepted["findings"]]
        )
        finding = next(
            finding
            for finding in rejected["findings"]
            if finding["check_id"] == "STE-PAR-001"
        )
        self.assertEqual(7, finding["details"]["sentence_count"])

    def test_flags_semicolons_and_unambiguous_contractions_as_exact_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            install_test_index(directory)
            dictionary = DictionaryIndex(
                next(Path(directory).glob("issue-9/*/dictionary.sqlite3"))
            )
            path = Path(directory) / "source.txt"
            path.write_text("alpha; it can't alpha.\n", encoding="utf-8")

            result = Analyzer(dictionary).analyze(path)

        exact = {
            finding["check_id"]: finding
            for finding in result["findings"]
            if finding["check_id"] in {"STE-PUN-001", "STE-GRM-001"}
        }
        self.assertEqual({"STE-PUN-001", "STE-GRM-001"}, set(exact))
        self.assertTrue(all(finding["mode"] == "exact" for finding in exact.values()))
        self.assertTrue(
            all(finding["severity"] == "error" for finding in exact.values())
        )
        required_fields = {
            "rule_id",
            "check_id",
            "mode",
            "severity",
            "confidence",
            "location",
            "excerpt",
            "suggestion",
            "dictionary_evidence",
        }
        self.assertTrue(
            all(required_fields <= finding.keys() for finding in exact.values())
        )

    def test_contraction_check_is_broad_but_does_not_treat_a_name_possessive_as_a_contraction(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            install_test_index(directory)
            dictionary = DictionaryIndex(
                next(Path(directory).glob("issue-9/*/dictionary.sqlite3"))
            )
            path = Path(directory) / "source.txt"
            path.write_text(
                "they're alpha. alpha won't alpha. alpha should've alpha. John's alpha.\n",
                encoding="utf-8",
            )

            result = Analyzer(dictionary).analyze(path)

        contractions = [
            finding
            for finding in result["findings"]
            if finding["check_id"] == "STE-GRM-001"
        ]
        self.assertEqual(3, len(contractions))
        self.assertNotIn("John's", [finding["excerpt"] for finding in contractions])


class TerminologyAndMarkdownTest(unittest.TestCase):
    def test_permitted_technical_noun_does_not_get_a_questionable_ing_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            install_test_index(directory)
            dictionary = DictionaryIndex(
                next(Path(directory).glob("issue-9/*/dictionary.sqlite3"))
            )
            glossary_path = Path(directory) / "glossary.yaml"
            glossary_path.write_text(
                """\
version: 1
scope: partial
terms:
  - term: bearing
    category: technical_noun
    source: project terms
    forms: [bearing, bearings]
""",
                encoding="utf-8",
            )
            path = Path(directory) / "source.md"
            path.write_text("bearing alpha.\n", encoding="utf-8")

            result = Analyzer(dictionary, load_glossary(glossary_path)).analyze(path)

        self.assertNotIn(
            "STE-HEU-003", [finding["check_id"] for finding in result["findings"]]
        )

    def test_glossary_uses_longest_terms_and_flags_forbidden_forms(self):
        with tempfile.TemporaryDirectory() as directory:
            install_test_index(directory)
            dictionary = DictionaryIndex(
                next(Path(directory).glob("issue-9/*/dictionary.sqlite3"))
            )
            glossary_path = Path(directory) / "glossary.yaml"
            glossary_path.write_text(
                """\
version: 1
scope: authoritative
terms:
  - term: pump
    category: technical_noun
    source: project terms
    forms: [pump]
  - term: hydraulic pump
    category: technical_noun
    source: project terms
    forms: [hydraulic pump, hydraulic pumps]
    forbidden_forms: [hyd pump]
  - term: API_TOKEN
    category: literal
    forms: [API_TOKEN]
""",
                encoding="utf-8",
            )
            accepted_path = Path(directory) / "accepted.md"
            accepted_path.write_text(
                "The hydraulic pump uses API_TOKEN.\n", encoding="utf-8"
            )
            forbidden_path = Path(directory) / "forbidden.md"
            forbidden_path.write_text("The hyd pump is alpha.\n", encoding="utf-8")
            analyzer = Analyzer(dictionary, load_glossary(glossary_path))

            accepted = analyzer.analyze(accepted_path)
            forbidden = analyzer.analyze(forbidden_path)

        self.assertEqual(1, accepted["coverage"]["glossary_matches"])
        self.assertEqual("authoritative", accepted["coverage"]["terminology_authority"])
        self.assertFalse(
            any(
                item["term"] in {"hydraulic", "pump"}
                for item in accepted["unresolved_terms"]
            )
        )
        variant = next(
            finding
            for finding in forbidden["findings"]
            if finding["check_id"] == "STE-LEX-002"
        )
        self.assertEqual("error", variant["severity"])
        self.assertEqual("technical_noun", variant["details"]["category"])

    def test_excludes_markdown_code_destinations_identifiers_and_configured_literals(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            install_test_index(directory)
            dictionary = DictionaryIndex(
                next(Path(directory).glob("issue-9/*/dictionary.sqlite3"))
            )
            glossary_path = Path(directory) / "glossary.yaml"
            glossary_path.write_text(
                """\
version: 1
scope: partial
terms:
  - term: SCREEN_LABEL
    category: literal
    forms: [SCREEN_LABEL]
""",
                encoding="utf-8",
            )
            path = Path(directory) / "source.md"
            path.write_text(
                """\
alpha `UNLISTED_CODE` [alpha](https://unknown.example/path) API_TOKEN SCREEN_LABEL.

```sh
never_check_this_word
```
""",
                encoding="utf-8",
            )

            result = Analyzer(dictionary, load_glossary(glossary_path)).analyze(path)

        unresolved = {item["term"] for item in result["unresolved_terms"]}
        self.assertFalse(
            unresolved
            & {
                "unlisted",
                "code",
                "https",
                "unknown",
                "example",
                "path",
                "api",
                "token",
                "screen",
                "label",
                "never",
            }
        )
        self.assertGreaterEqual(result["coverage"]["excluded_literals"], 4)
        self.assertEqual("partial", result["coverage"]["terminology_authority"])


class HeuristicAndResultTest(unittest.TestCase):
    def test_safety_warning_requires_both_a_command_or_condition_and_a_result(self):
        with tempfile.TemporaryDirectory() as directory:
            install_test_index(directory)
            dictionary = DictionaryIndex(
                next(Path(directory).glob("issue-9/*/dictionary.sqlite3"))
            )
            missing_command = Path(directory) / "missing-command.md"
            complete_shape = Path(directory) / "complete-shape.md"
            missing_command.write_text(
                "WARNING: alpha can cause damage.\n", encoding="utf-8"
            )
            complete_shape.write_text(
                "WARNING: stop alpha. alpha can cause damage.\n", encoding="utf-8"
            )
            analyzer = Analyzer(dictionary)

            incomplete = analyzer.analyze(missing_command)
            complete = analyzer.analyze(complete_shape)

        self.assertIn(
            "STE-HEU-007",
            [finding["check_id"] for finding in incomplete["findings"]],
        )
        self.assertNotIn(
            "STE-HEU-007",
            [finding["check_id"] for finding in complete["findings"]],
        )

    def test_heuristic_findings_are_warnings_regardless_of_confidence(self):
        with tempfile.TemporaryDirectory() as directory:
            install_test_index(directory)
            dictionary = DictionaryIndex(
                next(Path(directory).glob("issue-9/*/dictionary.sqlite3"))
            )
            path = Path(directory) / "source.md"
            path.write_text(
                """\
The alpha is tested and alpha is running.

1. open alpha and close alpha.

NOTE: Bravo alpha.

WARNING: stop alpha.
""",
                encoding="utf-8",
            )

            result = Analyzer(dictionary).analyze(path)

        heuristics = [
            finding for finding in result["findings"] if finding["mode"] == "heuristic"
        ]
        self.assertTrue(heuristics)
        self.assertTrue(all(finding["severity"] == "warning" for finding in heuristics))
        self.assertTrue(
            {
                "STE-HEU-001",
                "STE-HEU-002",
                "STE-HEU-003",
                "STE-HEU-005",
                "STE-HEU-006",
                "STE-HEU-007",
            }
            <= {finding["check_id"] for finding in heuristics}
        )

    def test_clean_document_is_ready_only_for_human_review(self):
        with tempfile.TemporaryDirectory() as directory:
            install_test_index(directory)
            dictionary = DictionaryIndex(
                next(Path(directory).glob("issue-9/*/dictionary.sqlite3"))
            )
            path = Path(directory) / "source.txt"
            path.write_text("alpha.\n", encoding="utf-8")
            original = path.read_bytes()
            analyzer = Analyzer(dictionary)

            first = analyzer.analyze(path)
            second = analyzer.analyze(path)
            unchanged = path.read_bytes()

        self.assertEqual("ready_for_human_review", first["result"])
        self.assertNotIn(first["result"], {"compliant", "certified", "verified"})
        self.assertEqual("complete", first["coverage"]["status"])
        self.assertEqual(first, second)
        self.assertEqual(original, unchanged)
        self.assertEqual(5, len(first["human_review_checklist"]))


if __name__ == "__main__":
    unittest.main()
