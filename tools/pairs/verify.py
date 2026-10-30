#!/usr/bin/env python3
"""Run the full phrase-authoring verification gate.

Automated checks validate structure, source-translation coverage, Arabic-span
coverage under `tabari-v2`, formatting, and that every explanation is as long
as its material deserves under the policy its chapter declares: a fixed 45-85
words for `sense-v1`, a target measured from Tafsīr al-Ṭabarī for `tabari-v2`.
They cannot prove that a human read the complete commentary or judged the
English and phrase boundaries. The required confirmation flag records that
human review was completed for this authoring run.

Usage after every authoring/editing run:
    python3 tools/pairs/verify.py --confirm-human-review
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def run(label: str, command: list[str], cwd: str = ROOT) -> bool:
    print("\n== %s ==" % label, flush=True)
    result = subprocess.run(command, cwd=cwd)
    if result.returncode:
        print("FAILED: %s (exit %d)" % (label, result.returncode), file=sys.stderr)
        return False
    print("PASSED: %s" % label)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirm-human-review",
        action="store_true",
        help="confirm full-commentary-first reading and human review of natural splits and simple, accurate English",
    )
    args = parser.parse_args()
    if not args.confirm_human_review:
        parser.error(
            "human review is required; after reading the full commentary for each edited verse, "
            "review meaning, natural boundaries, simple English, evidence, uncertainty, and that "
            "each explanation is as long as its material deserves (45-85 words under sense-v1, "
            "the target digest.py measures under tabari-v2), then rerun with --confirm-human-review"
        )

    checks = [
        ("authored and published data validation", [sys.executable, os.path.join(HERE, "assemble.py"), "--check"], ROOT),
        (
            "phrase-authoring unit tests",
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            HERE,
        ),
    ]
    success = True
    for label, command, cwd in checks:
        success = run(label, command, cwd) and success
    if not success:
        return 1

    print(
        "\nVERIFIED: automated checks passed and human-review confirmation was supplied. "
        "Generated data is ready to publish with assemble.py."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
