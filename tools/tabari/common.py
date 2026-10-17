"""Shared helpers for the Tafsir al-Tabari (English) importer.

The text is imported from https://tafseerquran.com/en/tafsir/<surah>/<ayah>,
the complete English translation of Jami al-bayan an tawil ay al-Quran that
the site's owner maintains and has given this project permission to use. The
site publishes the text under an open licence and allows crawling of the
tafsir pages (robots.txt: "Allow: /", with only /auth/ and /api/ excluded).

Standard library only: the importer runs on a GitHub Actions runner, on a
developer machine, or anywhere else with plain Python 3.9+.
"""

import os
import random
import re
import time
import urllib.error
import urllib.request

BASE = "https://tafseerquran.com"
TAFSIR_PATH = "/en/tafsir/{surah}/{ayah}"

# Identify the importer honestly. The site's owner knows about and approved
# this import; see tools/tabari/README.md for the permission note.
USER_AGENT = (
    "quran-explained-tabari-import/1.0 "
    "(+https://github.com/MaxiKen/quran-explained; contact: project maintainer)"
)

# A surah's page holds one passage per verse, but the passage may be long
# (Al-Baqarah 2:255 is several thousand words), so the cap is generous.
MAX_BYTES = 8 * 1024 * 1024

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def repo_root():
    return REPO_ROOT


def surah_verse_counts(root=None):
    """Verse count per surah, read from the reader's own chapter metadata."""
    root = root or repo_root()
    path = os.path.join(root, "js", "chapters-meta.js")
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    counts = {}
    for match in re.finditer(
        r"\{\s*number:\s*(\d+),.*?verses:\s*(\d+)\s*,", text
    ):
        counts[int(match.group(1))] = int(match.group(2))
    if len(counts) != 114:
        raise RuntimeError(
            "expected 114 surahs in js/chapters-meta.js, found %d" % len(counts)
        )
    return counts


def tafsir_url(surah, ayah, lang="en"):
    return BASE + TAFSIR_PATH.format(surah=surah, ayah=ayah).replace("/en/", "/%s/" % lang, 1)


def fetch(url, tries=4, timeout=45, pause=1.5):
    """GET a URL and return the decoded body, with retries and backoff."""
    last = None
    for attempt in range(tries):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise RuntimeError("response larger than %d bytes" % MAX_BYTES)
            return raw.decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001 - retried below
            last = exc
            code = getattr(exc, "code", None)
            if code in (400, 404):
                return None
            if attempt + 1 < tries:
                time.sleep(pause * (2 ** attempt) + random.random() * 0.5)
    raise RuntimeError("failed to fetch %s: %s" % (url, last))


def parse_surah_spec(spec):
    """'1' -> [1]; '1,2,5-7' -> [1, 2, 5, 6, 7]."""
    out = []
    for part in str(spec).split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            out.extend(range(int(start), int(end) + 1))
        else:
            out.append(int(part))
    return sorted(set(out))
