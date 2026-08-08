import sys
from pathlib import Path
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from ste100_glossary import GlossaryValidationError, load_glossary  # noqa: E402


class GlossaryValidationTest(unittest.TestCase):
    def test_loads_explicit_versioned_forms_and_term_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "glossary.yaml"
            path.write_text(
                """\
version: 1
scope: authoritative
terms:
  - term: hydraulic pump
    category: technical_noun
    source: Project terminology specification, section 4
    forms: [hydraulic pump, hydraulic pumps]
    forbidden_forms: [hyd pump]
  - term: calibrate
    category: technical_verb
    source: Maintenance engineering approval 42
    forms: [calibrate, calibrates, calibrated]
  - term: API_TOKEN
    category: literal
    forms: [API_TOKEN]
""",
                encoding="utf-8",
            )

            glossary = load_glossary(path)

        self.assertEqual(1, glossary.version)
        self.assertEqual("authoritative", glossary.scope)
        self.assertEqual(3, len(glossary.terms))
        self.assertEqual(("hydraulic pump", "hydraulic pumps"), glossary.terms[0].forms)
        self.assertEqual(("hyd pump",), glossary.terms[0].forbidden_forms)
        self.assertEqual(64, len(glossary.sha256))

    def test_rejects_ambiguous_or_untraceable_term_definitions(self):
        cases = {
            "missing technical source": """\
version: 1
scope: partial
terms:
  - term: widget
    category: technical_noun
    forms: [widget]
""",
            "invented category": """\
version: 1
scope: partial
terms:
  - term: widget
    category: convenient_word
    source: test
    forms: [widget]
""",
            "implicit form": """\
version: 1
scope: partial
terms:
  - term: widget
    category: technical_noun
    source: test
    forms: [widgets]
""",
            "form collision": """\
version: 1
scope: authoritative
terms:
  - term: widget
    category: technical_noun
    source: test
    forms: [widget]
  - term: other widget
    category: technical_noun
    source: test
    forms: [other widget]
    forbidden_forms: [widget]
""",
        }
        for label, content in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "glossary.yaml"
                path.write_text(content, encoding="utf-8")

                with self.assertRaises(GlossaryValidationError, msg=label):
                    load_glossary(path)


if __name__ == "__main__":
    unittest.main()
