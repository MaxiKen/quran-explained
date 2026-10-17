"""Tests for the Tafsir al-Tabari importer.

    python3 -m unittest discover -s tools/tabari/tests
"""

import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from importer import extract_arabic, extract_passage, migrate_file  # noqa: E402

FIXTURE = os.path.join(HERE, "fixture_105_001.html")


def fixture_html():
    with open(FIXTURE, "r", encoding="utf-8") as fh:
        return fh.read()


class ExtractPassageTest(unittest.TestCase):
    def setUp(self):
        self.text = extract_passage(fixture_html())

    def test_passage_is_found(self):
        self.assertIsNotNone(self.text)
        self.assertTrue(
            self.text.startswith("The statement concerning the explanation of the saying of Allah")
        )

    def test_site_furniture_is_left_out(self):
        # the collapsed Arabic panel, the ayah links and the footer are not
        # part of the commentary
        self.assertNotIn("Show original Arabic", self.text)
        self.assertNotIn("القول في تأويل قوله", self.text)
        self.assertNotIn("Ayah 2", self.text)
        self.assertNotIn("built with care", self.text)

    def test_quotes_inside_the_passage_are_kept(self):
        # the Qur'anic quotation sits inside the sentence, in Arabic
        self.assertIn("أَلَمْ تَرَ كَيْفَ فَعَلَ رَبُّكَ بِأَصْحَابِ الْفِيلِ", self.text)
        self.assertIn("(105:1)", self.text)

    def test_paragraphs_are_kept_apart(self):
        self.assertIn("\n\n", self.text)

    def test_a_page_without_a_passage_returns_none(self):
        self.assertIsNone(extract_passage("<html><body><p>nothing here</p></body></html>"))


class ExtractArabicTest(unittest.TestCase):
    def setUp(self):
        self.text = extract_arabic(fixture_html())

    def test_arabic_is_found(self):
        self.assertIsNotNone(self.text)
        self.assertTrue(self.text.startswith("القول في تأويل قوله جل ثناؤه"))

    def test_paragraphs_are_kept_apart(self):
        self.assertIn("\n\n", self.text)

    def test_the_english_passage_is_not_mixed_in(self):
        self.assertNotIn("The statement concerning the explanation", self.text)
        self.assertNotIn("Show original Arabic", self.text)

    def test_a_page_without_an_arabic_panel_returns_none(self):
        self.assertIsNone(extract_arabic("<html><body><p>لا نص هنا</p></body></html>"))

    def test_the_arabic_panel_is_not_read_as_the_english_passage(self):
        # the Arabic container also carries a "text-base" class token, so the
        # two containers must never be confused
        html = fixture_html().replace(
            '<div dir="rtl" lang="ar"', '<div class="text-base" dir="rtl" lang="ar"'
        )
        self.assertIn("القول في تأويل", extract_arabic(html))
        self.assertNotIn("القول في تأويل", extract_passage(html))


class MigrateFileTest(unittest.TestCase):
    def test_flat_verse_map_becomes_nested(self):
        payload = {
            "surah": 1,
            "verses": {"1": 0, "2": 1},
            "sets": {"tabari": {"ranges": ["1:1", "1:2"], "blocks": ["a", "b"]}},
        }
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "tabari_001.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            self.assertTrue(migrate_file(path))
            with open(path, "r", encoding="utf-8") as fh:
                migrated = json.load(fh)
        self.assertEqual(migrated["verses"]["1"], {"tabari": 0})
        self.assertEqual(migrated["verses"]["2"], {"tabari": 1})

    def test_nested_verse_map_is_left_alone(self):
        payload = {"surah": 1, "verses": {"1": {"tabari": 0}}}
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "tabari_001.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            self.assertFalse(migrate_file(path))


if __name__ == "__main__":
    unittest.main()
