"""Tests for the phrase-by-phrase pairing.

    cd tools/pairs && python3 -m unittest discover -s tests

The pairing must never say anything the reader's own translation does not
contain, and it must never point at a part of the commentary that is not
there. Those two rules are what the tests below check, over the whole
corpus as well as in examples.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'pairs'))

import build  # noqa: E402


class ClauseTest(unittest.TestCase):
    def test_a_sentence_is_its_own_phrase(self):
        clauses = build.split_clauses('Allah! There is no god but Him.')
        self.assertEqual([c['text'] for c in clauses],
                         ['Allah!', 'There is no god but Him.'])

    def test_a_comma_inside_a_list_does_not_break_the_phrase(self):
        text = 'There is no god ˹worthy of worship˺ except Him, the Ever-Living, All-Sustaining.'
        clauses = build.split_clauses(text)
        self.assertEqual(len(clauses), 1)
        self.assertEqual(clauses[0]['text'], text)

    def test_a_dash_breaks_the_phrase(self):
        clauses = build.split_clauses('There is no doubt about it—a guide for those mindful')
        self.assertEqual(len(clauses), 2)

    def test_the_pieces_are_the_whole_text(self):
        text = 'When My servants ask you ˹O Prophet˺ about Me: I am truly near. So let them respond.'
        pieces = ''.join(c['text'] for c in build.split_clauses(text))
        for word in ('When', 'My', 'servants', 'truly', 'near', 'respond'):
            self.assertIn(word, pieces)


class SpellingTest(unittest.TestCase):
    def test_british_and_american_meet(self):
        self.assertEqual(
            [t[2] for t in build.tokenize('favours')],
            [t[2] for t in build.tokenize('favors')])

    def test_stop_words_are_dropped(self):
        words = [t[2] for t in build.tokenize('the book of Allah')]
        self.assertEqual(words, ['book', 'allah'])


class ArabicTest(unittest.TestCase):
    def test_the_two_orthographies_meet(self):
        uthmani = 'إِنَّآ أَرۡسَلۡنَٰكَ بِٱلۡحَقِّ'
        imla = 'إِنَّا أَرْسَلْنَاكَ بِالْحَقِّ'
        self.assertIn(build.normalise_arabic(imla), build.normalise_arabic(uthmani))

    def test_the_dagger_alef_is_the_alef(self):
        self.assertEqual(build.normalise_arabic('نَٰكَ'), build.normalise_arabic('نَاكَ'))


class PairingTest(unittest.TestCase):
    def test_the_intercession_paragraph_lands_on_the_intercession_phrase(self):
        tafsir = json.load(open(os.path.join(ROOT, 'data', 'tafsir_002.json'), encoding='utf-8'))
        passage = tafsir['sets']['tabari']['blocks'][tafsir['verses']['255']['tabari']]
        modern = build.read_chapter(2)['255']['en']
        phrases = build.pair_verse(modern, '', passage)
        by_text = {p['text']: p for p in phrases}
        intercession = by_text['Who could possibly intercede with Him without His permission?']
        self.assertTrue(intercession['parts'])
        paragraphs = build.paragraphs_of(passage)
        first = paragraphs[intercession['parts'][0]]
        self.assertIn('intercedes', first)

    def test_a_phrase_is_the_readers_own_words(self):
        tafsir = json.load(open(os.path.join(ROOT, 'data', 'tafsir_002.json'), encoding='utf-8'))
        passage = tafsir['sets']['tabari']['blocks'][tafsir['verses']['255']['tabari']]
        modern = build.read_chapter(2)['255']['en']
        for phrase in build.pair_verse(modern, '', passage):
            self.assertIn(phrase['text'], modern)

    def test_the_parts_are_real_paragraphs(self):
        tafsir = json.load(open(os.path.join(ROOT, 'data', 'tafsir_002.json'), encoding='utf-8'))
        passage = tafsir['sets']['tabari']['blocks'][tafsir['verses']['255']['tabari']]
        modern = build.read_chapter(2)['255']['en']
        count = len(build.paragraphs_of(passage))
        for phrase in build.pair_verse(modern, '', passage):
            for index in phrase['parts']:
                self.assertTrue(0 <= index < count)


class CorpusTest(unittest.TestCase):
    """The published files must hold to the same rules."""

    SURAH = 2

    def test_the_file_is_what_the_builder_makes(self):
        path = os.path.join(ROOT, 'data', 'pairs_%03d.json' % self.SURAH)
        published = json.load(open(path, encoding='utf-8'))
        rebuilt = build.build_surah(self.SURAH)
        self.assertEqual(published['verses'].keys(), rebuilt['verses'].keys())
        for ayah, verse in published['verses'].items():
            self.assertEqual(verse['phrases'], rebuilt['verses'][ayah]['phrases'])

    def test_every_phrase_is_the_readers_own_words(self):
        path = os.path.join(ROOT, 'data', 'pairs_%03d.json' % self.SURAH)
        published = json.load(open(path, encoding='utf-8'))
        chapter = build.read_chapter(self.SURAH)
        tafsir = json.load(open(os.path.join(ROOT, 'data', 'tafsir_%03d.json' % self.SURAH), encoding='utf-8'))
        for ayah, verse in published['verses'].items():
            modern = chapter[ayah]['en']
            count = len(build.paragraphs_of(
                tafsir['sets']['tabari']['blocks'][tafsir['verses'][ayah]['tabari']]))
            for phrase in verse['phrases']:
                self.assertIn(phrase['text'], modern)
                for index in phrase['parts']:
                    self.assertTrue(0 <= index < count)


if __name__ == '__main__':
    unittest.main()
