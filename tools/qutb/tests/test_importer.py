"""Tests for the Fī Ẓilāl al-Qurʾān importer and verifier.

    python3 -m unittest discover -s tools/qutb/tests
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import importer  # noqa: E402
import verify  # noqa: E402

SAMPLE = [
    "سورة کا تعارف\n\nیہ پہلا پیراگراف ہے ۔",
    "پہلی آیت کی تفسیر",
    "پہلی آیت کی تفسیر",
    "دوسری آیت کی تفسیر",
]


def make_source(root, surah, texts):
    """Write an upstream-shaped source tree: <surah>/<ayah>.json + <surah>.json."""
    folder = os.path.join(root, str(surah))
    os.makedirs(folder)
    listed = []
    for ayah, text in enumerate(texts, 1):
        item = {"text": text, "ayah": ayah, "surah": surah}
        with open(os.path.join(folder, f"{ayah}.json"), "w", encoding="utf-8") as fh:
            json.dump(item, fh, ensure_ascii=False, indent=2)
        listed.append(item)
    with open(os.path.join(root, f"{surah}.json"), "w", encoding="utf-8") as fh:
        json.dump(listed, fh, ensure_ascii=False, indent=2)
    return root


class CollapseTest(unittest.TestCase):
    def test_consecutive_duplicates_become_one_block(self):
        rows = [(1, SAMPLE[0]), (2, SAMPLE[1]), (3, SAMPLE[1]), (4, SAMPLE[3])]
        blocks, ranges, verses = importer.collapse(rows, 7)
        self.assertEqual(blocks, [SAMPLE[0], SAMPLE[1], SAMPLE[3]])
        self.assertEqual(ranges, ["7:1", "7:2-3", "7:4"])
        self.assertEqual(verses, {1: 0, 2: 1, 3: 1, 4: 2})

    def test_whitespace_differences_still_collapse(self):
        rows = [(1, "متن"), (2, "  متن  "), (3, "\nمتن\n")]
        blocks, ranges, _ = importer.collapse(rows, 3)
        self.assertEqual(blocks, ["متن"])
        self.assertEqual(ranges, ["3:1-3"])

    def test_a_text_that_returns_after_a_different_one_is_a_new_block(self):
        rows = [(1, "الف"), (2, "ب"), (3, "الف")]
        blocks, ranges, _ = importer.collapse(rows, 5)
        self.assertEqual(blocks, ["الف", "ب", "الف"])
        self.assertEqual(ranges, ["5:1", "5:2", "5:3"])

    def test_paragraph_breaks_are_preserved(self):
        rows = [(1, "پیراگراف ایک\n\nپیراگراف دو")]
        blocks, _, _ = importer.collapse(rows, 1)
        self.assertIn("\n\n", blocks[0])


class BuildSurahTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root)
        make_source(self.root, 3, SAMPLE)

    def test_payload_shape(self):
        payload = importer.build_surah(self.root, 3, 4)
        self.assertEqual(payload["surah"], 3)
        self.assertEqual(payload["lang"], "ur")
        self.assertEqual(payload["dir"], "rtl")
        self.assertEqual(payload["edition"], importer.EDITION)
        self.assertEqual(payload["blocks"], [SAMPLE[0], SAMPLE[1], SAMPLE[3]])
        self.assertEqual(payload["ranges"], ["3:1", "3:2-3", "3:4"])
        self.assertEqual(payload["verses"], {"1": 0, "2": 1, "3": 1, "4": 2})

    def test_short_surah_is_rejected(self):
        with self.assertRaises(SystemExit):
            importer.build_surah(self.root, 3, 5)

    def test_numeric_verse_order_not_lexicographic(self):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        texts = [f"آیت {n}" for n in range(1, 12)]
        make_source(root, 4, texts)
        payload = importer.build_surah(root, 4, 11)
        self.assertEqual(payload["verses"]["10"], 9)
        self.assertEqual(payload["ranges"][10 - 1], "4:10")


class VerifyTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root)
        make_source(self.root, 3, SAMPLE)
        self.payload = importer.build_surah(self.root, 3, 4)

    def _write(self, payload, name="qutb_003.json"):
        path = os.path.join(self.root, name)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)
        return path

    def test_clean_file_passes(self):
        path = self._write(self.payload)
        self.assertEqual(verify.check_surah(path, 3, 4), [])

    def test_missing_verse_is_caught(self):
        bad = json.loads(json.dumps(self.payload))
        del bad["verses"]["4"]
        errors = verify.check_surah(self._write(bad), 3, 4)
        self.assertTrue(any("unmapped" in e for e in errors), errors)

    def test_repeated_block_is_caught(self):
        bad = json.loads(json.dumps(self.payload))
        bad["blocks"][2] = bad["blocks"][1]
        errors = verify.check_surah(self._write(bad), 3, 4)
        self.assertTrue(any("repeats" in e for e in errors), errors)

    def test_wrong_range_is_caught(self):
        bad = json.loads(json.dumps(self.payload))
        bad["ranges"][1] = "3:2-2"
        errors = verify.check_surah(self._write(bad), 3, 4)
        self.assertTrue(any("range 1" in e or "expected" in e for e in errors), errors)

    def test_latin_only_block_is_caught(self):
        bad = json.loads(json.dumps(self.payload))
        bad["blocks"][0] = "not urdu"
        errors = verify.check_surah(self._write(bad), 3, 4)
        self.assertTrue(any("Arabic-script" in e for e in errors), errors)

    def test_wrong_edition_is_caught(self):
        bad = json.loads(json.dumps(self.payload))
        bad["edition"] = "something-else"
        errors = verify.check_surah(self._write(bad), 3, 4)
        self.assertTrue(any("edition" in e for e in errors), errors)


class VerseCountTest(unittest.TestCase):
    def test_reader_metadata_has_114_surahs_and_6236_verses(self):
        counts = importer.verse_counts()
        self.assertEqual(len(counts), 114)
        self.assertEqual(sum(counts.values()), 6236)
        self.assertEqual(counts[1], 7)
        self.assertEqual(counts[2], 286)
        self.assertEqual(counts[114], 6)


if __name__ == "__main__":
    unittest.main()
