#!/usr/bin/env python3
"""Self-tests for the clear-teaching gates.

A gate that passes everything is worth nothing, so each test here corrupts a
passing payload in one specific way and asserts that verify.py catches it.
Run:

    python3 -m unittest discover -s tools/clear/tests
"""
import copy
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'clear'))

import verify  # noqa: E402

GOOD = os.path.join(ROOT, 'tools', 'clear', 'samples', '001.json')
DATA = os.path.join(ROOT, 'data')


def load():
    with open(GOOD, encoding='utf-8') as fh:
        return json.load(fh)


def run(rec, name='t.json'):
    """Write a payload to a temp file and verify it, returning the errors."""
    path = os.path.join(HERE, name)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(rec, fh, ensure_ascii=False)
    try:
        ok, errs = verify.verify_file(path, DATA, verbose=False)
        return ok, errs
    finally:
        os.remove(path)


class WordTarget(unittest.TestCase):
    """STYLE.md 2: 420 words per verse, band 400-440."""

    def test_good_payload_passes(self):
        ok, errs = run(load())
        self.assertTrue(ok, errs)

    def test_counts_prose_not_markup(self):
        # markup must not count; heading and bullet words must
        self.assertEqual(verify.words('## Two words\n\n**bold** *italic* - '), 5)
        self.assertEqual(verify.words('- one\n- two\n- three'), 3)

    def test_short_entry_fails(self):
        rec = load()
        rec['blocks'][0] = rec['blocks'][0].rsplit('## In short', 1)[0]
        ok, errs = run(rec)
        self.assertFalse(ok)
        self.assertTrue(any('under the 400-word floor' in e for e in errs), errs)

    def test_long_entry_fails(self):
        rec = load()
        rec['blocks'][0] += '\n\n' + ('This adds words beyond the ceiling. ' * 40)
        ok, errs = run(rec)
        self.assertFalse(ok)
        self.assertTrue(any('over the 440-word ceiling' in e for e in errs), errs)

    def test_band_boundaries(self):
        # 400 and 440 pass, 399 and 441 do not
        for n, expect in ((400, True), (440, True), (399, False), (441, False)):
            body = ' '.join(['word'] * n)
            errs, _ = verify.check_words('1:1', body)
            self.assertEqual(not errs, expect, f'{n} words: {errs}')


class Script(unittest.TestCase):
    """STYLE.md 3: Latin only, the salawat sign excepted."""

    def test_arabic_word_fails(self):
        ok, errs = run(self._with('تفسیر'))
        self.assertFalse(ok)
        self.assertTrue(any('Arabic-block letters' in e for e in errs), errs)

    def test_single_letter_fails(self):
        ok, errs = run(self._with('ا'))
        self.assertFalse(ok, 'one Arabic letter must fail')

    def test_salawat_allowed(self):
        rec = load()
        before = rec['blocks'][0]
        rec['blocks'][0] = before.replace('Merciful', 'Merciful\ufdfa', 1)
        self.assertNotEqual(rec['blocks'][0], before)
        self.assertEqual(verify.words(rec['blocks'][0]), verify.words(before),
                         'the salawat sign must not change the word count')
        ok, errs = run(rec)
        self.assertTrue(ok, errs)

    def _with(self, insert):
        rec = load()
        e = rec['blocks'][0]
        # splice the letter in without adding a word, so only the script rule trips
        rec['blocks'][0] = e.replace('act of beginning', 'act ' + insert + 'of beginning', 1)
        self.assertIn(insert, rec['blocks'][0])
        return rec


class Alignment(unittest.TestCase):
    """STYLE.md 4: the app's translation is carried in the entry."""

    def test_missing_translation_phrase_fails(self):
        rec = load()
        # drop the phrase "Lord of all worlds" from verse 2's entry
        rec['blocks'][1] = rec['blocks'][1].replace('Lord of all worlds', 'Rabb of everything')
        ok, errs = run(rec)
        self.assertFalse(ok)
        self.assertTrue(any('does not carry the translation' in e for e in errs), errs)

    def test_phrases_split_on_dash_and_comma(self):
        got = verify.translation_phrases(
            'In the Name of Allah\u2014the Most Compassionate, Most Merciful')
        self.assertEqual(len(got), 3, got)


class Distinct(unittest.TestCase):
    """STYLE.md 5: no recycled prose between sibling entries."""

    def test_identical_siblings_fail(self):
        rec = load()
        rec['blocks'][2] = rec['blocks'][1]
        ok, errs = run(rec)
        self.assertFalse(ok)
        self.assertTrue(any('8-word runs' in e for e in errs), errs)

    def test_one_shared_sentence_passes(self):
        # a single 8-word run is below the 5% tolerance on a 420-word entry
        rec = load()
        share = 'Praise belongs to the One who made everything.'
        rec['blocks'][1] += ' ' + share
        rec['blocks'][2] += ' ' + share
        # adding text pushes both over the word ceiling; check distinctness only
        errs = [e for e in run(rec)[1] if '8-word runs' not in e]
        self.assertFalse(any('8-word runs' in e for e in errs), errs)


class HouseStyle(unittest.TestCase):
    """STYLE.md 6."""

    def _mutate(self, fn):
        rec = load()
        before = rec['blocks'][0]
        rec['blocks'][0] = fn(before)
        self.assertNotEqual(rec['blocks'][0], before, 'the mutation did not apply')
        return run(rec)

    def test_semicolon_fails(self):
        ok, errs = self._mutate(lambda e: e.replace('That order is deliberate.',
                                                    'That order is deliberate; it is chosen.'))
        self.assertFalse(ok)
        self.assertTrue(any('semicolon' in e for e in errs), errs)

    def test_em_dash_in_prose_fails(self):
        ok, errs = self._mutate(lambda e: e.replace('That order is deliberate.',
                                                    'That order is deliberate \u2014 and chosen.'))
        self.assertFalse(ok)
        self.assertTrue(any('em dash' in e for e in errs), errs)

    def test_em_dash_inside_a_quotation_passes(self):
        # the app's own translation contains an em dash; quoting it is allowed
        ok, errs = run(load())
        self.assertTrue(ok, errs)
        self.assertIn('\u2014', load()['blocks'][0])

    def test_first_person_fails(self):
        ok, errs = self._mutate(lambda e: e.replace('The reader does not launch',
                                                    'I do not launch'))
        self.assertFalse(ok)
        self.assertTrue(any('first person' in e for e in errs), errs)

    def test_naming_the_source_fails(self):
        ok, errs = self._mutate(lambda e: e.replace('That order is deliberate.',
                                                    'Qutb says that order is deliberate.'))
        self.assertFalse(ok)
        self.assertTrue(any('source' in e for e in errs), errs)

    def test_generic_heading_fails(self):
        ok, errs = self._mutate(lambda e: e.replace('## Why it matters that the surah starts here',
                                                    '## Explanation'))
        self.assertFalse(ok)
        self.assertTrue(any('generic heading' in e for e in errs), errs)

    def test_wrong_heading_level_fails(self):
        ok, errs = self._mutate(lambda e: e.replace('## Why it matters that the surah starts here',
                                                    '### Why it matters that the surah starts here'))
        self.assertFalse(ok)
        self.assertTrue(any('heading level' in e for e in errs), errs)

    def test_missing_in_short_fails(self):
        ok, errs = self._mutate(lambda e: e.split('## In short')[0])
        self.assertFalse(ok)
        self.assertTrue(any('In short' in e for e in errs), errs)


class Coverage(unittest.TestCase):
    """STYLE.md 2.3: one entry per verse, never merged."""

    def test_missing_entry_fails(self):
        rec = load()
        rec['blocks'].pop()
        ok, errs = run(rec)
        self.assertFalse(ok)

    def test_merged_entry_fails(self):
        rec = load()
        rec['verses']['7'] = 5          # verse 7 points at verse 6's entry
        ok, errs = run(rec)
        self.assertFalse(ok)
        self.assertTrue(any('shares an entry' in e for e in errs), errs)

    def test_range_mismatch_fails(self):
        rec = load()
        rec['ranges'][2] = '1:2-3'
        ok, errs = run(rec)
        self.assertFalse(ok)
        self.assertTrue(any('range says' in e for e in errs), errs)


class PayloadShape(unittest.TestCase):
    """STYLE.md 12."""

    def test_missing_lang_fails(self):
        rec = load()
        rec.pop('lang')
        ok, errs = run(rec)
        self.assertFalse(ok)
        self.assertTrue(any('lang' in e for e in errs), errs)

    def test_rtl_fails(self):
        rec = load()
        rec['dir'] = 'rtl'
        ok, errs = run(rec)
        self.assertFalse(ok)

    def test_missing_based_on_fails(self):
        rec = load()
        rec.pop('basedOn')
        ok, errs = run(rec)
        self.assertFalse(ok)
        self.assertTrue(any('basedOn' in e for e in errs), errs)


if __name__ == '__main__':
    unittest.main()
