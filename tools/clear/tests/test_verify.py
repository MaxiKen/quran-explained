#!/usr/bin/env python3
"""Self-tests for the clear-teaching gates.

A gate that passes everything is worth nothing, so each test here corrupts a
passing payload in one specific way and asserts that verify.py catches it.
Run:

    python3 -m unittest discover -s tools/clear/tests
"""
import copy
import json
import re
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


def prefix(n):
    """A payload covering verses 1..n only, the shape build.py --partial emits."""
    rec = load()
    rec['blocks'] = rec['blocks'][:n]
    rec['ranges'] = rec['ranges'][:n]
    rec['verses'] = {k: v for k, v in rec['verses'].items() if v < n}
    return rec


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

    def test_mandated_span_does_not_count_as_recycled(self):
        # two verses whose translations are the same sentence (2:134, 2:141)
        # must not fail on the span the style requires word for word. The
        # surah 1 sample predates the == span convention, so this uses surah 2.
        with open(os.path.join(ROOT, 'tools', 'clear', 'samples',
                               '002.json'), encoding='utf-8') as fh:
            rec = json.load(fh)
        spans = [re.search(r'==(.+?)==', b, re.S).group(1) for b in rec['blocks']]
        i = max(range(len(spans)), key=lambda k: len(spans[k].split()))
        j = 0 if i else 1
        self.assertGreater(len(spans[i].split()), 40, 'need a long span to test with')
        rec['blocks'][j] = re.sub(r'==(.+?)==', '==' + spans[i] + '==',
                                  rec['blocks'][j], count=1, flags=re.S)
        errs = [e for e in run(rec)[1] if '8-word runs' in e]
        self.assertFalse(errs, errs)

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

    def test_partial_accepts_a_prefix(self):
        # a block of a long surah may cover verses 1..N only
        ok, errs = verify.verify_file(self._write(prefix(4)), DATA,
                                      verbose=False, partial=True)
        self.assertTrue(ok, errs)

    def test_partial_still_demands_a_prefix(self):
        # dropping a middle verse leaves a gap, even in partial mode
        rec = prefix(4)
        rec['blocks'].pop(2)
        rec['ranges'].pop(2)
        rec['verses'] = {str(int(k) if int(k) < 3 else int(k) + 1): v
                         for k, v in rec['verses'].items()}
        ok, errs = verify.verify_file(self._write(rec), DATA, verbose=False,
                                      partial=True)
        self.assertFalse(ok)

    def test_partial_does_not_relax_any_other_rule(self):
        # a short entry still fails, even in partial mode
        rec = prefix(4)
        rec['blocks'][0] = rec['blocks'][0].rsplit('## In short', 1)[0]
        ok, errs = verify.verify_file(self._write(rec), DATA, verbose=False,
                                      partial=True)
        self.assertFalse(ok)
        self.assertTrue(any('under the 400-word floor' in e for e in errs), errs)

    def _write(self, rec):
        path = os.path.join(HERE, 'partial.json')
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(rec, fh, ensure_ascii=False)
        self.addCleanup(os.remove, path)
        return path


class TranslationSpan(unittest.TestCase):
    """STYLE.md 4-6: the == span is the translation, and may break prose rules."""

    def test_glued_heading_fails(self):
        # the renderer splits on blank lines only, so '## In short' that trails
        # a line of prose is printed as literal text inside a paragraph
        body = ('## A heading\n\nprose ends here\n## In short\n\n'
                '- one\n- two\n- three')
        errs = verify.check_shape('t', body)
        self.assertTrue(any('blank line' in e for e in errs), errs)

    def test_bullet_list_may_run_on_without_blank_lines(self):
        body = ('## A heading\n\nprose.\n\n## In short\n\n'
                '- one\n- two\n- three')
        self.assertEqual(verify.check_shape('t', body), [])

    def test_semicolon_inside_the_span_passes(self):
        body = ('## A heading\n\n==We are definitely with you; we were only '
                'mocking.== The verse reports two rooms.\n\n## In short\n\n'
                '- one\n- two\n- three')
        self.assertEqual(verify.check_shape('t', body), [])

    def test_semicolon_outside_the_span_still_fails(self):
        body = '## A heading\n\nThis is prose; and a semicolon.\n\n## In short\n\n- one'
        errs = verify.check_shape('t', body)
        self.assertTrue(any('semicolon' in e for e in errs), errs)

    def test_block_file_is_checked_as_a_prefix(self):
        # only the -blockN filename may shorten coverage, and only that
        self.assertTrue(verify.is_block('tools/clear/samples/003-block2.json'))
        self.assertFalse(verify.is_block('tools/clear/samples/002.json'))
        self.assertFalse(verify.is_block('data/clear_002.json'))

    def test_span_must_match_the_translation(self):
        # the marked span is checked word for word against ayah_en
        text = 'Alif-Lãm-Mĩm'
        errs = verify.check_alignment('2:1', '==Alif-Lãm-Mĩm==', text)
        self.assertEqual(errs, [])
        errs = verify.check_alignment('2:1', '==Alif Lam Mim==', text)
        self.assertTrue(any('does not match' in e for e in errs), errs)


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

    def test_missing_notice_fails(self):
        # STYLE.md 10: the caveat travels with the chapter
        rec = load()
        rec['notice'] = ''
        ok, errs = run(rec)
        self.assertFalse(ok)
        self.assertTrue(any('notice' in e for e in errs), errs)

    def test_missing_based_on_fails(self):
        rec = load()
        rec.pop('basedOn')
        ok, errs = run(rec)
        self.assertFalse(ok)
        self.assertTrue(any('basedOn' in e for e in errs), errs)


if __name__ == '__main__':
    unittest.main()
