import json
import stat
import sys
from pathlib import Path
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from ste100_index import (  # noqa: E402
    DictionaryEntry,
    DictionaryIndex,
    ExtractionManifest,
    IndexError,
    IndexStore,
    Issue9PdfParser,
    PdfStructureError,
)
from pdf_fixture import dictionary_header, write_pdf  # noqa: E402


class Issue9PdfParserTest(unittest.TestCase):
    def test_title_validation_requires_issue_9_and_the_exact_publication_date(self):
        Issue9PdfParser.validate_title_page_text(
            "ASD-STE100 Simplified Technical English ISSUE 9 January 15, 2025"
        )
        Issue9PdfParser.validate_title_page_text("ASD-STE100\nISSUE 9\n15 JANUARY 2025")

        with self.assertRaisesRegex(PdfStructureError, "January 15, 2025"):
            Issue9PdfParser.validate_title_page_text(
                "ASD-STE100 Simplified Technical English ISSUE 9 January 1, 2025"
            )

    def test_extracts_multiline_entries_and_cross_page_continuations(self):
        with tempfile.TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "dictionary.pdf"
            page_one = dictionary_header() + [
                (40, 700, "ALPHA, ALPHAS"),
                (150, 700, "n"),
                (250, 700, "An invented first"),
                (250, 684, "meaning line"),
                (430, 700, "Use alpha."),
                (40, 650, "BRAVO"),
                (150, 650, "v"),
                (250, 650, "An invented action that"),
                (250, 634, "continues"),
                (40, 20, "ASD-STE100 300"),
            ]
            page_two = dictionary_header() + [
                (250, 700, "on the next page"),
                (430, 700, "Use bravo."),
                (40, 660, "BRAVO"),
                (150, 660, "n"),
                (250, 660, "A second sense"),
            ]
            write_pdf(pdf_path, [page_one, page_two])

            entries = Issue9PdfParser().parse_tables(pdf_path)

        self.assertEqual(3, len(entries))
        self.assertEqual(("alpha", "alphas"), entries[0].permitted_forms)
        self.assertEqual("An invented first meaning line", entries[0].meaning)
        self.assertEqual(
            "An invented action that continues on the next page", entries[1].meaning
        )
        self.assertEqual((1, 2), (entries[1].page_start, entries[1].page_end))
        self.assertEqual("n", entries[2].part_of_speech)
        self.assertEqual("Helvetica", entries[2].font_name)
        self.assertGreater(entries[2].source_bbox[2], entries[2].source_bbox[0])
        self.assertNotIn("ASD-STE100", entries[1].meaning)

    def test_rejects_column_geometry_that_changes_between_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "malformed.pdf"
            changed_header = [
                (40, 740, "WORD"),
                (150, 740, "PART OF SPEECH"),
                (280, 740, "APPROVED MEANING"),
                (460, 740, "APPROVED EXAMPLE"),
            ]
            row = [(40, 700, "ALPHA"), (150, 700, "n"), (250, 700, "meaning")]
            write_pdf(pdf_path, [dictionary_header() + row, changed_header + row])

            with self.assertRaisesRegex(PdfStructureError, "geometry changed"):
                Issue9PdfParser().parse_tables(pdf_path)

    def test_rejects_a_pdf_without_dictionary_table_anchors(self):
        with tempfile.TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "no-table.pdf"
            write_pdf(pdf_path, [[(40, 740, "NOT A DICTIONARY")]])

            with self.assertRaisesRegex(PdfStructureError, "No four-column"):
                Issue9PdfParser().parse_tables(pdf_path)


class IndexStoreTest(unittest.TestCase):
    def test_installs_a_private_atomic_index_with_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "data"
            source = Path(directory) / "official.pdf"
            source.write_bytes(b"private source bytes")
            entry = DictionaryEntry(
                headword="alpha",
                permitted_forms=("alpha", "alphas"),
                part_of_speech="n",
                meaning="An invented item",
                alternatives="use bravo",
                examples="Use alpha.",
                page_start=300,
                page_end=301,
                font_name="Helvetica",
                font_size=10.0,
                source_bbox=(40.0, 80.0, 500.0, 110.0),
            )
            extraction = ExtractionManifest(
                434, (300, 301), (40, 150, 250, 430), 200_000
            )

            index_path = IndexStore(root).install(source, [entry], extraction)
            results = DictionaryIndex(index_path).lookup("ALPHAS", "n")

            self.assertEqual("alpha", results[0]["headword"])
            self.assertEqual([300, 301], results[0]["pages"])
            self.assertEqual(0o600, stat.S_IMODE(index_path.stat().st_mode))
            self.assertEqual(0o700, stat.S_IMODE(index_path.parent.stat().st_mode))
            self.assertEqual(0o700, stat.S_IMODE((root / "issue-9").stat().st_mode))
            self.assertEqual(0o700, stat.S_IMODE(root.stat().st_mode))
            self.assertEqual(b"private source bytes", source.read_bytes())
            self.assertFalse(any(index_path.parent.glob("*.pdf")))
            manifest = json.loads(
                DictionaryIndex(index_path).metadata()["extraction_manifest"]
            )
            self.assertEqual(9, manifest["issue"])
            self.assertEqual(64, len(manifest["source_sha256"]))
            self.assertEqual([300, 301], manifest["table_pages"])

    def test_database_failure_rolls_back_without_replacing_an_existing_index(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "data"
            source = Path(directory) / "official.pdf"
            source.write_bytes(b"stable source")
            target_dir = (
                root
                / "issue-9"
                / __import__("hashlib").sha256(b"stable source").hexdigest()
            )
            target_dir.mkdir(parents=True)
            existing = target_dir / "dictionary.sqlite3"
            existing.write_bytes(b"existing index")
            extraction = ExtractionManifest(434, (300,), (40, 150, 250, 430), 200_000)
            invalid_entry = DictionaryEntry(
                headword="alpha",
                permitted_forms=("alpha", "alpha"),
                part_of_speech="n",
                meaning="Invented",
                alternatives="",
                examples="",
                page_start=300,
                page_end=300,
                font_name="Helvetica",
                font_size=10.0,
                source_bbox=(40, 80, 300, 100),
            )

            with self.assertRaisesRegex(IndexError, "Could not create"):
                IndexStore(root).install(source, [invalid_entry], extraction)

            self.assertEqual(b"existing index", existing.read_bytes())
            self.assertFalse(any(target_dir.glob(".dictionary-*.tmp")))


if __name__ == "__main__":
    unittest.main()
