"""Tests for the house style and the authoring tools.

    cd tools/pairs && python3 -m unittest discover -s tests
"""

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools", "pairs"))
sys.path.insert(0, os.path.join(ROOT, "tools", "pairs", "authoring"))

import assemble  # noqa: E402
import curve  # noqa: E402
import digest  # noqa: E402
import style  # noqa: E402
from authoring import author  # noqa: E402


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def effective_policy(authored, verse):
    return (verse.get("split_policy")
            or authored.get("split_policy")
            or assemble.POLICY_LEGACY)


class ProseStyleTest(unittest.TestCase):
    def test_arabic_script_is_not_allowed(self):
        self.assertTrue(style.prose_problems("The word means mercy in Arabic: رحمة", "p"))
        self.assertFalse(style.prose_problems("The word means mercy in Arabic", "p"))

    def test_a_dash_or_a_semicolon_is_not_allowed(self):
        self.assertTrue(style.prose_problems("The sense is clear \u2014 and plain", "p"))
        self.assertTrue(style.prose_problems("The sense is clear \u2013 and plain", "p"))
        self.assertTrue(style.prose_problems("The sense is clear; the rest follows", "p"))
        self.assertFalse(style.prose_problems("The sense is clear, as it is said", "p"))

    def test_a_sentence_starts_with_a_capital_letter(self):
        self.assertTrue(style.prose_problems("the sense is clear", "p"))
        self.assertFalse(style.prose_problems("The sense is clear", "p"))

    def test_paragraphs_are_separated_by_a_blank_line(self):
        self.assertFalse(style.prose_problems("First part.\n\nSecond part.", "p"))
        self.assertTrue(style.prose_problems("First part.\nSecond part.", "p"))

    def test_an_empty_paragraph_is_a_problem(self):
        self.assertTrue(style.prose_problems("\n\nFirst part.", "p"))
        self.assertFalse(style.prose_problems("First part.\n\n\nSecond part.", "p"))


class OneVoiceTest(unittest.TestCase):
    def test_a_named_source_is_a_problem(self):
        for text in ("A report from Ibn Abbas agrees.",
                     "Said ibn Jubayr gives this reading.",
                     "The view of al-Zuhri is preferred.",
                     "This is what al-Tabari says.",
                     "The statement is that of Umar."):
            self.assertTrue(style.name_problems(text, "p"), text)

    def test_a_figure_in_the_story_may_be_named(self):
        for text in ("Some said it was Uzayr.",
                     "It was said that this man was al-Khidr.",
                     "Others said it was the argument between him and Nimrod.",
                     "The passage recalls Musaylima, the liar who claimed it."):
            self.assertFalse(style.name_problems(text, "p"), text)

    def test_the_one_voice_rule_can_be_turned_off(self):
        self.assertTrue(style.style_problems("A report from Ibn Abbas agrees.", "p"))
        self.assertFalse(style.style_problems("A report from Ibn Abbas agrees.", "p",
                                              one_voice=False))


class StyleOverTheCorpusTest(unittest.TestCase):
    def tabari_phrases(self):
        for name in sorted(os.listdir(assemble.AUTHORED)):
            if not name.endswith(".json"):
                continue
            surah = int(name[:3])
            authored = read_json(os.path.join(assemble.AUTHORED, name))
            for ayah, verse in authored["verses"].items():
                if effective_policy(authored, verse) != assemble.POLICY_TABARI:
                    continue
                for index, phrase in enumerate(verse["phrases"], 1):
                    yield surah, ayah, index, phrase["explanation"]

    def test_no_tabari_explanation_breaks_the_house_style(self):
        checked = 0
        for surah, ayah, index, text in self.tabari_phrases():
            where = "%d:%s phrase %d" % (surah, ayah, index)
            self.assertEqual(style.style_problems(text, where), [], where)
            checked += 1
        self.assertGreater(checked, 0)

    def test_no_tabari_explanation_names_a_source(self):
        for surah, ayah, index, text in self.tabari_phrases():
            where = "%d:%s phrase %d" % (surah, ayah, index)
            self.assertEqual(style.name_problems(text, where), [], where)


class CurveTest(unittest.TestCase):
    def test_the_curve_is_the_target_plus_a_tenth(self):
        self.assertEqual(curve.desired(0), 121)
        self.assertEqual(curve.desired(4.03), 121)
        self.assertEqual(curve.desired(12.0), 198)
        self.assertEqual(curve.desired(20.13), 332)

    def test_the_margin_grows_with_the_curve(self):
        self.assertEqual(curve.tolerance(121), 14)
        self.assertEqual(curve.tolerance(1210), 145)

    def test_there_is_no_ceiling(self):
        """A phrase that runs long is reporting material, not padding."""
        want = curve.desired(12.0)
        self.assertTrue(curve.off_curve(5000, want))
        self.assertNotIn("max_words", digest.budget([], (0, 0)))


class AuthoringToolTest(unittest.TestCase):
    def test_a_published_batch_passes_the_writer(self):
        authored = read_json(os.path.join(assemble.AUTHORED, "002.json"))
        batch = {"surah": 2, "verses": {"1": authored["verses"]["1"]["phrases"]}}
        self.assertEqual(author.check_batch(2, batch), [])

    def test_a_named_source_is_refused(self):
        authored = read_json(os.path.join(assemble.AUTHORED, "002.json"))
        phrases = [dict(p) for p in authored["verses"]["1"]["phrases"]]
        phrases[0]["explanation"] = "A report from Ibn Abbas says this. " + phrases[0]["explanation"]
        batch = {"surah": 2, "verses": {"1": phrases}}
        problems = author.check_batch(2, batch)
        self.assertTrue(any("names a source" in p for p in problems), problems)

    def test_a_short_explanation_is_refused(self):
        authored = read_json(os.path.join(assemble.AUTHORED, "002.json"))
        phrases = [dict(p) for p in authored["verses"]["1"]["phrases"]]
        phrases[0]["explanation"] = "A short note."
        batch = {"surah": 2, "verses": {"1": phrases}}
        problems = author.check_batch(2, batch)
        self.assertTrue(any("short for its material" in p for p in problems), problems)


if __name__ == "__main__":
    unittest.main()
