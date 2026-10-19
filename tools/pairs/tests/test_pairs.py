"""Tests for the authored phrase-by-phrase explanations.

    cd tools/pairs && python3 -m unittest discover -s tests
"""

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools", "pairs"))

import assemble  # noqa: E402
import source  # noqa: E402


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


class PhraseExplanationTest(unittest.TestCase):
    def test_dense_policy_minimum_scales_with_translation_length(self):
        self.assertEqual(assemble.minimum_phrase_count("Go"), 1)
        self.assertEqual(assemble.minimum_phrase_count("one two three"), 2)
        self.assertEqual(assemble.minimum_phrase_count("one two three four five six"), 2)
        self.assertEqual(assemble.minimum_phrase_count("one two three four five six seven"), 3)
        self.assertEqual(assemble.minimum_phrase_count("one two three four five six seven eight nine"), 3)

    def authored_names(self):
        return sorted(name for name in os.listdir(assemble.AUTHORED) if name.endswith(".json"))

    def test_every_authored_chapter_passes_validation(self):
        names = self.authored_names()
        self.assertTrue(names, "nothing has been authored yet")
        for name in names:
            surah = int(name[:3])
            _, problems = assemble.build_surah(surah)
            self.assertEqual(problems, [], "surah %d: %s" % (surah, problems))

    def test_published_data_matches_the_authored_source(self):
        for name in self.authored_names():
            surah = int(name[:3])
            expected, problems = assemble.build_surah(surah)
            self.assertEqual(problems, [])
            path = os.path.join(ROOT, "data", "pairs_%03d.json" % surah)
            with open(path, encoding="utf-8") as handle:
                published = json.load(handle)
            self.assertEqual(published, expected)

    def test_only_authored_chapters_have_published_pair_data(self):
        authored = {"pairs_%s.json" % name[:3] for name in self.authored_names()}
        published = {
            name for name in os.listdir(os.path.join(ROOT, "data"))
            if name.startswith("pairs_") and name.endswith(".json")
        }
        self.assertEqual(published, authored)

    def test_every_authored_chapter_covers_all_verses(self):
        for name in self.authored_names():
            surah = int(name[:3])
            authored = read_json(os.path.join(assemble.AUTHORED, name))
            chapter = source.read_chapter(surah)
            self.assertEqual(set(authored["verses"]), set(chapter), "surah %d" % surah)

    def test_phrase_pieces_are_exact_and_cover_each_translation(self):
        for name in self.authored_names():
            surah = int(name[:3])
            chapter = source.read_chapter(surah)
            authored = read_json(os.path.join(assemble.AUTHORED, name))
            for ayah, verse in authored["verses"].items():
                modern = chapter[ayah]["en"]
                cursor = 0
                pieces = []
                for phrase in verse["phrases"]:
                    piece = phrase["translation"]
                    start = modern.find(piece, cursor)
                    self.assertGreaterEqual(start, 0, "%d:%s is missing or out of order" % (surah, piece))
                    self.assertFalse(any(char.isalnum() for char in modern[cursor:start]))
                    cursor = start + len(piece)
                    pieces.append(piece)
                self.assertFalse(any(char.isalnum() for char in modern[cursor:]))
                self.assertTrue(pieces)

    def test_phrases_have_only_translation_and_substantive_paragraphs(self):
        for name in self.authored_names():
            surah = int(name[:3])
            published = read_json(os.path.join(ROOT, "data", "pairs_%03d.json" % surah))
            for verse in published["verses"].values():
                for phrase in verse["phrases"]:
                    self.assertEqual(set(phrase), {"translation", "explanation"})
                    self.assertNotIn("\n", phrase["explanation"])
                    words = len(phrase["explanation"].split())
                    self.assertGreaterEqual(words, 30, phrase["translation"])
                    self.assertLessEqual(words, 85, phrase["translation"])


if __name__ == "__main__":
    unittest.main()
