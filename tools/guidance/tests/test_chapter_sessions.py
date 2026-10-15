"""Chapter selection and deferred full-verification orchestration regressions."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import finish
import status


class ChapterSessionTests(unittest.TestCase):
    def test_status_selects_only_requested_chapter(self):
        with patch.object(sys, 'argv', ['status.py', '--next', '--surah', '18']), \
                patch.object(status, 'next_job', return_value=None) as next_job, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(status.main(), 0)
        self.assertEqual(next_job.call_args.kwargs['order'], [18])
        self.assertIn('chapter 18 is fully published', output.getvalue())

    def test_invalid_chapter_rejected(self):
        with patch.object(sys, 'argv', ['status.py', '--next', '--surah', '115']), \
                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
            status.main()
        self.assertEqual(exc.exception.code, 2)

    def run_finish(self, entry_status):
        with tempfile.NamedTemporaryFile(suffix='.md') as raw:
            report = {'intro': {'status': entry_status, 'words': 10}}
            with patch.object(sys, 'argv', ['finish.py', '018-intro', '--file', raw.name, '--no-commit']), \
                    patch.object(finish, 'run', return_value=subprocess.CompletedProcess([], 0, '', '')) as run, \
                    patch.object(finish, 'read_json', return_value=report), \
                    patch.object(status, 'next_job', return_value=None) as next_job, \
                    contextlib.redirect_stdout(io.StringIO()) as output:
                result = finish.main()
            return result, run.call_args_list, next_job, output.getvalue()

    def test_finish_never_runs_full_data_check_and_stays_in_chapter(self):
        result, calls, next_job, output = self.run_finish('ok')
        self.assertEqual(result, 0)
        commands = [call.args[0] for call in calls]
        verifies = [cmd for cmd in commands if any(str(v).endswith('verify.py') for v in cmd)]
        self.assertEqual(len(verifies), 1)
        self.assertEqual(verifies[0][verifies[0].index('--source') + 1], 'work')
        next_job.assert_called_once_with(order=[18])
        self.assertIn('single final verification and file manifest', output)

    def test_failure_stops_before_assembly(self):
        result, calls, next_job, _ = self.run_finish('fail')
        self.assertEqual(result, 1)
        self.assertFalse(any(any(str(v).endswith('assemble.py') for v in call.args[0]) for call in calls))
        next_job.assert_not_called()


if __name__ == '__main__':
    unittest.main()
