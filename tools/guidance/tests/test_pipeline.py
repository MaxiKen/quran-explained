"""Tests for the guidance pipeline. Run from the repository root:

    python3 -m unittest discover -s tools/guidance/tests -v
    # or
    python3 -m pytest tools/guidance/tests -q

Everything runs offline: the end-to-end test uses the mock provider and
writes into a temporary work directory.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(TOOLS))
sys.path.insert(0, TOOLS)

from common import build_jobs, chapter_meta, fold, load_chapter, parse_surah_selection  # noqa: E402
from generate import load_system_prompt, parse_output, render_user  # noqa: E402
from verify import blocks_for_surah, extract_anchors, verbatim_runs, verify_entries  # noqa: E402

EXEMPLARS = os.path.join(TOOLS, 'prompts', 'exemplars')


def translations(surah: int) -> dict[int, str]:
    return {int(k): v['en'] for k, v in load_chapter(surah)['verses'].items()}


def exemplar(name: str) -> dict:
    return parse_output(open(os.path.join(EXEMPLARS, name), encoding='utf-8').read())


def run(*args: str, cwd: str = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True)


class PackTests(unittest.TestCase):
    def test_every_verse_in_exactly_one_job(self):
        for surah in (1, 2, 55, 112):
            jobs = build_jobs(surah)
            kinds = {j.kind for j in jobs}
            self.assertIn('intro', kinds)
            seen = []
            for j in jobs:
                if j.kind == 'verses':
                    seen.extend(j.verses)
                    self.assertLessEqual(len(j.verses), 8)
                    self.assertEqual(j.verses, list(range(j.verses[0], j.verses[-1] + 1)))
            self.assertEqual(sorted(seen), list(range(1, chapter_meta()[surah]['verses'] + 1)))
            self.assertEqual(len(seen), len(set(seen)))

    def test_job_blocks_touch_their_verses(self):
        for j in build_jobs(112):
            for b in j.blocks:
                if j.kind == 'verses':
                    self.assertTrue(set(b.verses) & set(j.verses), f'{j.id}: block {b.source} {b.range}')

    def test_selection_parser(self):
        self.assertEqual(parse_surah_selection('1,112-114'), [1, 112, 113, 114])
        self.assertEqual(len(parse_surah_selection('all')), 114)


class ShareTests(unittest.TestCase):
    """Passage blocks are attributed to the verses they actually discuss."""

    def test_ibn_kathir_passage_is_split_by_verse_quotes(self):
        b = next(x for x in blocks_for_surah(55) if x['source'] == 'ibn-kathir' and x['range'] == '55:1-13')
        total = len(b['text'].split())
        self.assertTrue(b['located'])
        self.assertGreater(b['intro_words'], 200)          # 'The Introduction to Surat Ar-Rahman'
        self.assertAlmostEqual(sum(b['shares'].values()) + b['intro_words'], total, delta=2)
        self.assertTrue(60 <= b['shares'][13] <= 250, b['shares'])   # the refrain paragraph
        self.assertGreater(b['shares'][6], b['shares'][13])          # an-najm has a long discussion

    def test_refrain_block_counts_fully_for_each_verse(self):
        b = next(x for x in blocks_for_surah(55) if x['source'] == 'mukhtasar' and x['range'].startswith('55:13,'))
        total = len(b['text'].split())
        self.assertEqual(set(b['shares'].values()), {float(total)})

    def test_single_verse_block_is_whole(self):
        b = next(x for x in blocks_for_surah(55) if x['source'] == 'jalalayn' and x['range'] == '55:13')
        self.assertEqual(b['shares'], {13: float(len(b['text'].split()))})

    def test_opening_single_verse_block_separates_intro(self):
        b = next(x for x in blocks_for_surah(1) if x['source'] == 'ibn-kathir' and x['range'] == '1:1')
        self.assertGreater(b['intro_words'], 1000)
        self.assertAlmostEqual(b['shares'][1] + b['intro_words'], len(b['text'].split()), delta=2)

    def test_jobs_carry_material_words(self):
        job = next(j for j in build_jobs(55) if j.id == '055-009-013')
        self.assertEqual(sorted(job.material_words), [9, 10, 11, 12, 13])
        self.assertTrue(200 <= job.material_words[13] <= 600, job.material_words)
        self.assertIn('Material about this verse', render_user(job))


class PromptTests(unittest.TestCase):
    def test_system_prompt_contains_exemplars_and_rules(self):
        sp = load_system_prompt()
        self.assertIn('<<<VERSE', sp)
        self.assertIn('Phrase by phrase', sp)
        self.assertIn('Example: Qur\'an 1:2', sp)
        self.assertIn('Example: Qur\'an 112:1', sp)
        self.assertIn('Example: Qur\'an 55:13', sp)

    def test_user_prompt_quotes_translation_and_material(self):
        job = next(j for j in build_jobs(112) if j.kind == 'verses')
        user = render_user(job)
        self.assertIn('## 112:1', user)
        self.assertIn('He is Allah', user)
        self.assertIn('## Text 1', user)
        self.assertNotIn('ibn-kathir', user.lower().split('## text 1')[0])


class ParseTests(unittest.TestCase):
    def test_round_trip(self):
        raw = ('<<<VERSE 112:1>>>\nBody one.\n<<<END>>>\n<<<VERSE 112:2>>>\nBody two.\n<<<END>>>\n'
               '<<<NOTES>>>\nleft out: nothing\n')
        out = parse_output(raw)
        self.assertEqual(out['verses'], {1: 'Body one.', 2: 'Body two.'})
        self.assertIn('left out', out['notes'])
        self.assertIsNone(out['intro'])

    def test_intro(self):
        out = parse_output('<<<INTRO 112>>>\nAn introduction.\n<<<END>>>')
        self.assertEqual(out['intro'], 'An introduction.')
        self.assertEqual(out['verses'], {})


class ExemplarTests(unittest.TestCase):
    """The hand-written exemplars must pass the gates they teach."""

    def check(self, name: str, surah: int, verse: int, own_only: bool):
        entry = exemplar(name)['verses'][verse]
        blocks = [b for b in blocks_for_surah(surah) if verse in b['verses']]
        if own_only:
            blocks = [b for b in blocks if b['verses'] == [verse]]
        rep = verify_entries(surah, {verse: entry}, blocks, translations(surah))['verses'][verse]
        self.assertEqual(rep['errors'], [], rep)
        return rep

    def test_001_002_is_ok(self):
        rep = self.check('001_002.md', 1, 2, own_only=False)
        self.assertEqual(rep['status'], 'ok', rep)
        self.assertGreater(rep['coverage'], 0.85)

    def test_112_001_has_no_errors(self):
        rep = self.check('112_001.md', 112, 1, own_only=False)
        self.assertNotEqual(rep['status'], 'fail', rep)
        # shared 112:1-4 material lives in the sibling entries and the intro,
        # so coverage is only meaningful against the verse's own blocks
        entry = exemplar('112_001.md')['verses'][1]
        own = [b for b in blocks_for_surah(112) if b['verses'] == [1]]
        rep = verify_entries(112, {1: entry}, own, translations(112))['verses'][1]
        self.assertGreater(rep['coverage'], 0.7, rep)

    def test_055_013_is_ok_against_its_own_blocks(self):
        rep = self.check('055_013.md', 55, 13, own_only=True)
        self.assertEqual(rep['status'], 'ok', rep)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.entry = exemplar('112_001.md')['verses'][1]
        self.blocks = [b for b in blocks_for_surah(112) if 1 in b['verses']]
        self.tr = translations(112)

    def report(self, text: str) -> dict:
        return verify_entries(112, {1: text}, self.blocks, self.tr)['verses'][1]

    def test_clean_entry_has_no_errors(self):
        self.assertEqual(self.report(self.entry)['errors'], [])

    def test_arabic_script_fails(self):
        rep = self.report(self.entry.replace('He is Allah', 'He is Allah (قل هو الله)'))
        self.assertTrue(any('Arabic' in e for e in rep['errors']), rep['errors'])

    def test_naming_a_source_fails(self):
        rep = self.report(self.entry + '\n\nIbn Kathir explains that this is so.')
        self.assertTrue(any('names a source' in e or 'source' in e for e in rep['errors']), rep['errors'])

    def test_missing_translation_quote_fails(self):
        rep = self.report(self.entry.replace('He is Allah—One ˹and Indivisible˺', 'God is the single one'))
        self.assertTrue(any('translation' in e for e in rep['errors']), rep['errors'])

    def test_missing_structure_fails(self):
        rep = self.report(self.entry.replace('### In short', '### Finally'))
        self.assertTrue(any('In short' in e for e in rep['errors']), rep['errors'])

    def test_verbatim_run_fails(self):
        src = next(b for b in self.blocks if b['source'] == 'tazkirul')['text']
        words = [w for w in src.split() if w.isascii() and '"' not in w][:40]
        rep = self.report(self.entry + '\n\n' + ' '.join(words))
        self.assertTrue(any('verbatim' in e for e in rep['errors']), rep['errors'])

    def test_short_verbatim_run_flags(self):
        src = next(b for b in self.blocks if b['source'] == 'tazkirul')['text']
        words = [w for w in src.split() if w.isascii() and '"' not in w][:14]
        rep = self.report(self.entry + '\n\n' + ' '.join(words))
        self.assertEqual(rep['errors'], [])
        self.assertTrue(any('verbatim' in w for w in rep['warnings']), rep['warnings'])

    def test_unknown_collector_fails(self):
        rep = self.report(self.entry + '\n\nThis was recorded by Ibn Majah with a sound chain.')
        self.assertTrue(any('collector' in e for e in rep['errors']), rep['errors'])

    def test_em_dash_outside_quote_flags(self):
        rep = self.report(self.entry + '\n\nThis is a test — of the dash.')
        self.assertEqual(rep['errors'], [])
        self.assertTrue(any('dash' in w for w in rep['warnings']), rep['warnings'])

    def test_stray_marker_fails(self):
        rep = self.report(self.entry + '\n<<<END>>>')
        self.assertTrue(rep['errors'], rep)


class VariantTests(unittest.TestCase):
    """Spelling variants, possessives and long quoted passages must not be
    reported as fabrication or copying."""

    def setUp(self):
        self.entry = exemplar('112_001.md')['verses'][1]
        self.blocks = [b for b in blocks_for_surah(112) if 1 in b['verses']]
        self.tr = translations(112)

    def report(self, text: str, blocks=None) -> dict:
        return verify_entries(112, {1: text}, blocks or self.blocks, self.tr)['verses'][1]

    def test_collector_spelling_variant_is_not_a_fabrication(self):
        blocks = [dict(b) for b in self.blocks]
        blocks[0] = dict(blocks[0], text=blocks[0]['text'] + ' Ibn Marduwyah recorded it in his Tafsir.')
        rep = self.report(self.entry + '\n\nIbn Mardawayh recorded it too.', blocks)
        self.assertFalse(any('collector' in e for e in rep['errors']), rep['errors'])

    def test_possessive_does_not_hide_a_name(self):
        self.assertEqual(fold("Umm Salamah's hadith"), fold('Umm Salamah hadith'))
        self.assertEqual(fold("the Prophet's ﷺ recitation"), fold('the Prophet ﷺ recitation'))

    def test_long_quoted_quran_passage_with_reference_is_exempt(self):
        a = ' '.join(f'word{i}' for i in range(60))
        self.assertEqual(verbatim_runs('"' + a + '" (2:255)', 'zero ' + a + ' end', 12), [])
        self.assertTrue(verbatim_runs('"' + a + '"', 'zero ' + a + ' end', 12), 'a long quote without a reference still counts')

    def test_cross_reference_with_spaces_counts(self):
        blocks = [dict(b) for b in self.blocks]
        blocks[0] = dict(blocks[0], text=blocks[0]['text'] + ' As the Qur\'an says (68 : 33).')
        rep = self.report(self.entry + '\n\nThe same point is made in 68:33.', blocks)
        self.assertFalse(any('68:33' in e for e in rep['errors']), rep['errors'])

    def test_imam_shafii_is_not_a_banned_name(self):
        rep = self.report(self.entry + '\n\nAsh-Shāfiʿī held that it is recited aloud.')
        self.assertFalse(any('names a source' in e for e in rep['errors']), rep['errors'])
        rep = self.report(self.entry + '\n\nMufti Muhammad Shafi held the same.')
        self.assertTrue(any('names a source' in e for e in rep['errors']), rep['errors'])


class IngestTests(unittest.TestCase):
    def test_ingest_stores_a_complete_output_and_refuses_an_incomplete_one(self):
        from ingest import ingest
        tmp = tempfile.mkdtemp()
        try:
            jobs_dir = os.path.join(tmp, 'jobs')
            out_dir = os.path.join(tmp, 'out')
            subprocess.run([sys.executable, os.path.join(HERE, '..', 'pack.py'), '--surahs', '112',
                            '--out', jobs_dir, '--no-intro'], check=True, capture_output=True)
            job = json.load(open(os.path.join(jobs_dir, '112.json')))[0]
            verses = job['verses']
            text = ''.join(f'<<<VERSE 112:{v}>>>\nentry {v}\n<<<END>>>\n' for v in verses)
            path = ingest(job['id'], text, jobs_dir=jobs_dir, out_dir=out_dir, model='test')
            rec = json.load(open(path))
            self.assertEqual(rec['status'], 'ok')
            self.assertEqual(sorted(map(int, rec['verses'])), sorted(verses))
            partial = ''.join(f'<<<VERSE 112:{v}>>>\nentry {v}\n<<<END>>>\n' for v in verses[:-1])
            with self.assertRaises(SystemExit):
                ingest(job['id'], partial, jobs_dir=jobs_dir, out_dir=out_dir, model='test')
        finally:
            shutil.rmtree(tmp)


class StatusTests(unittest.TestCase):
    """status.py derives progress from data/ only and picks the first pending job in order."""

    def test_next_job_follows_published_state(self):
        from status import next_job, published, split_parts
        tmp = tempfile.mkdtemp()
        try:
            data_dir = os.path.join(tmp, 'data')
            jobs_dir = os.path.join(tmp, 'jobs')
            os.makedirs(data_dir)
            self.assertEqual(published(112, data_dir), ({}, False))
            # nothing published -> the introduction comes first
            job = next_job(order=[112], data_dir=data_dir, jobs_dir=jobs_dir)
            self.assertIsNotNone(job)
            self.assertEqual((job.surah, job.kind), (112, 'intro'))
            # intro published, verses not -> the first verse job
            payload = {'surah': 112, 'intro': 'intro text', 'verses': {}}
            with open(os.path.join(data_dir, 'guidance_112.json'), 'w', encoding='utf-8') as f:
                json.dump(payload, f)
            job = next_job(order=[112], data_dir=data_dir, jobs_dir=jobs_dir)
            self.assertEqual((job.kind, job.verses[0]), ('verses', 1))
            payload['verses'] = {str(v): {'text': 'x', 'status': 'ok'} for v in range(1, 5)}
            with open(os.path.join(data_dir, 'guidance_112.json'), 'w', encoding='utf-8') as f:
                json.dump(payload, f)
            self.assertIsNone(next_job(order=[112], data_dir=data_dir, jobs_dir=jobs_dir))
            parts = split_parts('a' * 100 + '\n' + 'b' * 100 + '\n' + 'c' * 100, chunk=150)
            self.assertEqual(len(parts), 3)
            self.assertTrue(all(len(p) <= 151 for p in parts))
        finally:
            shutil.rmtree(tmp)


class AnchorTests(unittest.TestCase):
    def test_sources_are_not_anchors(self):
        anchors = extract_anchors('Ibn Kathir said that Al-Qurtubi and Tafsir Al-Jalalayn agree. Qatadah said so too.')
        keys = ' '.join(anchors)
        self.assertNotIn('kathir', keys)
        self.assertNotIn('qurtubi', keys)
        self.assertIn('qatadah', keys)

    def test_fold_unifies_spellings(self):
        self.assertEqual(fold('Jābir b. ʿAbd Allāh'), fold('Jabir ibn Abdullah'))
        self.assertEqual(fold('Abu Hurayrah'), fold('Abū Hurayrah'))
        self.assertEqual(fold('ʿAbd al-Raḥmān'), fold('Abdur-Rahman'))

    def test_verbatim_runs(self):
        a = 'one two three four five six seven eight nine ten eleven twelve thirteen fourteen'
        runs = verbatim_runs(a, 'zero ' + a + ' end', 12)
        self.assertTrue(runs and runs[0][0] >= 12, runs)
        runs = verbatim_runs('"' + a + '"', 'zero ' + a + ' end', 12)
        self.assertEqual(runs, [], 'quoted text is exempt')


class EndToEndTests(unittest.TestCase):
    """pack -> generate (mock) -> verify -> audit (dry) -> assemble on surah 112."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='guidance-test-')
        cls.jobs = os.path.join(cls.tmp, 'jobs')
        cls.out = os.path.join(cls.tmp, 'out')
        cls.reports = os.path.join(cls.tmp, 'reports')
        cls.data = os.path.join(cls.tmp, 'data')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_pipeline(self):
        g = os.path.join(TOOLS, '')
        r = run(g + 'pack.py', '--surahs', '112', '--out', self.jobs)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.jobs, '112.json')))

        r = run(g + 'generate.py', '--surahs', '112', '--dry-run', '--jobs', self.jobs, '--out', self.out)
        self.assertEqual(r.returncode, 0, r.stderr)
        outs = sorted(os.listdir(os.path.join(self.out, '112')))
        self.assertEqual(outs, ['112-001-004.json', '112-intro.json'])
        o = json.load(open(os.path.join(self.out, '112', '112-001-004.json'), encoding='utf-8'))
        self.assertEqual(o['status'], 'ok')
        self.assertEqual(sorted(map(int, o['verses'])), [1, 2, 3, 4])

        r = run(g + 'verify.py', '--source', 'work', '--surahs', '112', '--jobs', self.jobs, '--out', self.out,
                '--reports', self.reports)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rep = json.load(open(os.path.join(self.reports, '112.json'), encoding='utf-8'))
        self.assertEqual(sorted(map(int, rep['verses'])), [1, 2, 3, 4])
        for v in rep['verses'].values():
            self.assertNotEqual(v['status'], 'fail', v)

        r = run(g + 'audit.py', '--surahs', '112', '--dry-run', '--jobs', self.jobs, '--out', self.out)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

        r = run(g + 'assemble.py', '--surahs', '112', '--jobs', self.jobs, '--out', self.out,
                '--data-dir', self.data, '--replace')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        payload = json.load(open(os.path.join(self.data, 'guidance_112.json'), encoding='utf-8'))
        self.assertEqual(payload['surah'], 112)
        self.assertEqual(payload['label'], 'Plain-English commentary')
        self.assertEqual(sorted(map(int, payload['verses'])), [1, 2, 3, 4])
        v1 = payload['verses']['1']
        for key in ('text', 'draws_on', 'words', 'status', 'coverage'):
            self.assertIn(key, v1)
        self.assertTrue(payload['intro'])
        # minified single line
        raw = open(os.path.join(self.data, 'guidance_112.json'), encoding='utf-8').read()
        self.assertEqual(raw.count('\n'), 1)

        r = run(g + 'verify.py', '--source', 'data', '--surahs', '112', '--data-dir', self.data,
                '--reports', self.reports)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == '__main__':
    unittest.main()
