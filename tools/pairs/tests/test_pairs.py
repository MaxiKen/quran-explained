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
import digest  # noqa: E402
import source  # noqa: E402


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


class PhraseExplanationTest(unittest.TestCase):
    def authored_names(self):
        return sorted(name for name in os.listdir(assemble.AUTHORED) if name.endswith(".json"))

    def test_every_authored_chapter_passes_validation(self):
        names = self.authored_names()
        # An empty authoring set is valid while a chapter is being started over.
        self.assertIsInstance(names, list)
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
            if os.path.exists(path):
                with open(path, encoding="utf-8") as handle:
                    published = json.load(handle)
                self.assertEqual(published, expected)

    def test_only_authored_chapters_have_published_pair_data(self):
        authored = {"pairs_%s.json" % name[:3] for name in self.authored_names()}
        published = {
            name for name in os.listdir(os.path.join(ROOT, "data"))
            if name.startswith("pairs_") and name.endswith(".json")
        }
        self.assertLessEqual(published, authored)

    def test_every_authored_chapter_covers_all_verses(self):
        for name in self.authored_names():
            surah = int(name[:3])
            authored = read_json(os.path.join(assemble.AUTHORED, name))
            chapter = source.read_chapter(surah)
            self.assertTrue(set(authored["verses"]).issubset(set(chapter)), "surah %d" % surah)

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

    def test_phrases_have_only_the_fields_their_policy_allows(self):
        for name in self.authored_names():
            surah = int(name[:3])
            authored = read_json(os.path.join(assemble.AUTHORED, name))
            policy = authored.get("split_policy") or assemble.POLICY_LEGACY
            allowed = {"translation", "explanation"}
            if policy == assemble.POLICY_TABARI:
                # the Arabic piece is what the source is measured against
                allowed.add("ar")
            for verse in authored["verses"].values():
                for phrase in verse["phrases"]:
                    self.assertEqual(set(phrase), allowed, "surah %d" % surah)

    def test_legacy_phrases_stay_in_the_fixed_band(self):
        """sense-v1 chapters keep the band they were written under."""
        for name in self.authored_names():
            authored = read_json(os.path.join(assemble.AUTHORED, name))
            if (authored.get("split_policy") or assemble.POLICY_LEGACY) != assemble.POLICY_LEGACY:
                continue
            for verse in authored["verses"].values():
                for phrase in verse["phrases"]:
                    self.assertNotIn("\n", phrase["explanation"])
                    words = len(phrase["explanation"].split())
                    self.assertGreaterEqual(words, 45, phrase["translation"])
                    self.assertLessEqual(words, 85, phrase["translation"])

    def test_tabari_phrases_match_the_length_their_material_deserves(self):
        """tabari-v2 chapters are measured against Ṭabarī, not against a band."""
        checked = 0
        for name in self.authored_names():
            surah = int(name[:3])
            authored = read_json(os.path.join(assemble.AUTHORED, name))
            if (authored.get("split_policy") or assemble.POLICY_LEGACY) != assemble.POLICY_TABARI:
                continue
            tafsir, verses, _ = digest.load_surah(surah)
            for ayah, verse in authored["verses"].items():
                measured = digest.measure(digest.verse_passage(tafsir, ayah), verses[ayah]["ar"])
                spans = digest.phrase_spans([p["ar"] for p in verse["phrases"]], verses[ayah]["ar"])
                for phrase, span in zip(verse["phrases"], spans):
                    target = digest.budget(measured, span)
                    words = len(" ".join(phrase["explanation"].split()).split())
                    problem = digest.length_problem(words, target, "%d:%s" % (surah, ayah))
                    self.assertIsNone(problem, problem)
                    self.assertGreaterEqual(words, digest.FLOOR_WORDS)
                    checked += 1
        self.assertGreater(checked, 0, "no tabari-v2 chapter was measured")

    def test_tabari_phrases_name_the_arabic_they_explain(self):
        """The Arabic spans are exact, consecutive and cover the verse once."""
        for name in self.authored_names():
            surah = int(name[:3])
            authored = read_json(os.path.join(assemble.AUTHORED, name))
            if (authored.get("split_policy") or assemble.POLICY_LEGACY) != assemble.POLICY_TABARI:
                continue
            _, verses, _ = digest.load_surah(surah)
            for ayah, verse in authored["verses"].items():
                spans = digest.phrase_spans([p["ar"] for p in verse["phrases"]], verses[ayah]["ar"])
                self.assertEqual(len(spans), len(verse["phrases"]))
                self.assertEqual(spans[0][0], 0)
                self.assertEqual(spans[-1][1], len(verses[ayah]["ar"].split()) - 1)
                for (low, high), next_span in zip(spans, spans[1:]):
                    self.assertEqual(high + 1, next_span[0], "%d:%s" % (surah, ayah))


if __name__ == "__main__":
    unittest.main()
