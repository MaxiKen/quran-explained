"""Tests for the phrase-by-phrase pairing.

    cd tools/pairs && python3 -m unittest discover -s tests

The pairing is written by reading the commentary. These tests hold it to the
rules the reader relies on: a phrase is plain modern English, a part is a
paragraph that exists, the paragraphs run in the order they are read, and the
Arabic of a phrase is the Arabic of the verse.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'pairs'))

import source  # noqa: E402
import assemble  # noqa: E402


class AuthoredTest(unittest.TestCase):
    """The authored files must hold to the rules."""

    def authored(self):
        names = sorted(n for n in os.listdir(assemble.AUTHORED) if n.endswith('.json'))
        self.assertTrue(names, 'nothing is authored yet')
        for name in names:
            surah = int(name[:3])
            data, problems = assemble.build_surah(surah)
            self.assertEqual(problems, [], 'surah %d: %s' % (surah, problems))

    def test_every_authored_surah_is_clean(self):
        self.authored()

    def test_the_published_file_is_the_authored_file(self):
        names = sorted(n for n in os.listdir(assemble.AUTHORED) if n.endswith('.json'))
        for name in names:
            surah = int(name[:3])
            data, _ = assemble.build_surah(surah)
            published = json.load(open(os.path.join(ROOT, 'data', 'pairs_%03d.json' % surah), encoding='utf-8'))
            self.assertEqual(published['verses'], data['verses'])


class ReadingTest(unittest.TestCase):
    """The reading the pairing is made from."""

    def test_the_paragraphs_are_the_ones_the_reader_sees(self):
        tafsir = json.load(open(os.path.join(ROOT, 'data', 'tafsir_001.json'), encoding='utf-8'))
        passage = tafsir['sets']['tabari']['blocks'][tafsir['verses']['1']['tabari']]
        paragraphs = source.paragraphs_of(passage)
        self.assertTrue(paragraphs)
        self.assertNotIn('---', paragraphs[0])

    def test_a_phrase_heading_is_recognised(self):
        self.assertTrue(source.is_phrase_opening('The exposition of His word: "I seek refuge" (aʿūdhu).'))
        self.assertFalse(source.is_phrase_opening('Abū Jaʿfar said: Seeking refuge means seeking protection.'))

    def test_the_two_spellings_of_arabic_meet(self):
        self.assertTrue(source.arabic_in('الرَّحْمَنِ الرَّحِيمِ', 'ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ'))
        self.assertTrue(source.arabic_in('أَرْسَلْنَاكَ', 'أَرۡسَلۡنَٰكَ'))
        self.assertFalse(source.arabic_in('الصَّرَاطَ', 'ٱلرَّحۡمَٰنِ'))


class PublishedTest(unittest.TestCase):
    """The published files must point at paragraphs that exist."""

    def test_the_parts_are_real_paragraphs(self):
        names = sorted(n for n in os.listdir(assemble.AUTHORED) if n.endswith('.json'))
        for name in names:
            surah = int(name[:3])
            published = json.load(open(os.path.join(ROOT, 'data', 'pairs_%03d.json' % surah), encoding='utf-8'))
            tafsir = json.load(open(os.path.join(ROOT, 'data', 'tafsir_%03d.json' % surah), encoding='utf-8'))
            for ayah, verse in published['verses'].items():
                count = len(source.paragraphs_of(
                    tafsir['sets']['tabari']['blocks'][tafsir['verses'][ayah]['tabari']]))
                for phrase in verse['phrases']:
                    self.assertTrue(phrase['parts'], '%d:%s has no part' % (surah, ayah))
                    for index in phrase['parts']:
                        self.assertTrue(0 <= index < count)


if __name__ == '__main__':
    unittest.main()
