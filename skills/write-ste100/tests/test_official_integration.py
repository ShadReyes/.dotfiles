import json
import os
from pathlib import Path
import sys
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from ste100_index import DictionaryIndex, IndexStore, Issue9PdfParser  # noqa: E402


@unittest.skipUnless(os.environ.get("STE100_PDF"), "STE100_PDF is not set")
class OfficialIssue9IntegrationTest(unittest.TestCase):
    def test_official_copy_matches_the_issue_9_parser_manifest(self):
        source = Path(os.environ["STE100_PDF"])

        entries, extraction = Issue9PdfParser().validate_and_parse(source)

        self.assertEqual(434, extraction.page_count)
        self.assertEqual(875, len({entry.headword for entry in entries}))
        self.assertEqual(
            [entry.headword for entry in entries],
            sorted(entry.headword for entry in entries),
        )
        self.assertTrue(all(entry.meaning for entry in entries))
        self.assertTrue(all(entry.page_start <= entry.page_end for entry in entries))

        with tempfile.TemporaryDirectory() as directory:
            index_path = IndexStore(Path(directory)).install(
                source, entries, extraction
            )
            dictionary = DictionaryIndex(index_path)
            metadata = dictionary.metadata()
            manifest = json.loads(metadata["extraction_manifest"])

            self.assertEqual("2025-01-15", metadata["issue_date"])
            self.assertEqual(875, manifest["unique_headword_count"])
            self.assertEqual(64, len(manifest["dictionary_checksum"]))
            self.assertTrue(dictionary.lookup("close"))


if __name__ == "__main__":
    unittest.main()
