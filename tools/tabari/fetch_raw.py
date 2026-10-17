"""Download the raw HTML of tafseerquran.com tafsir pages.

Used to inspect the page markup before writing the extractor, and kept as the
cache layer for the importer: every page that has been fetched once is stored
on disk, so a re-run never hits the site again.

    python3 tools/tabari/fetch_raw.py --pages 1:1,105:1-5 --out work/tabari/raw
"""

import argparse
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import fetch, parse_surah_spec, surah_verse_counts, tafsir_url  # noqa: E402

_print_lock = threading.Lock()


def page_path(out_dir, surah, ayah):
    return os.path.join(out_dir, "%03d_%03d.html" % (surah, ayah))


def targets(spec, counts):
    """Expand a spec into (surah, ayah) pairs.

    A spec of '1' means the whole surah; '1:3' means ayah 3 of surah 1;
    '105:1-5' means ayahs 1 to 5 of surah 105.
    """
    pairs = []
    for part in str(spec).split(","):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            surah_text, ayah_text = part.split(":", 1)
            surah = int(surah_text)
            for ayah in parse_surah_spec(ayah_text):
                pairs.append((surah, ayah))
        else:
            surah = int(part)
            for ayah in range(1, counts[surah] + 1):
                pairs.append((surah, ayah))
    return pairs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", required=True, help="e.g. 1,105 or 1:3,105:1-5")
    parser.add_argument("--out", default="work/tabari/raw")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument("--refetch", action="store_true", help="ignore cached pages")
    args = parser.parse_args()

    counts = surah_verse_counts()
    pairs = targets(args.pages, counts)
    os.makedirs(args.out, exist_ok=True)

    todo = [p for p in pairs if args.refetch or not os.path.exists(page_path(args.out, *p))]
    print("%d page(s) requested, %d to fetch" % (len(pairs), len(todo)), flush=True)

    done = [0]
    failures = []
    lock = threading.Lock()

    def worker(pair):
        surah, ayah = pair
        target = page_path(args.out, surah, ayah)
        try:
            html = fetch(tafsir_url(surah, ayah))
        except Exception as exc:  # noqa: BLE001 - reported below
            with lock:
                failures.append((surah, ayah, str(exc)))
            return
        if html is None:
            with lock:
                failures.append((surah, ayah, "not found"))
            return
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(html)
        with lock:
            done[0] += 1
            if done[0] % 50 == 0 or done[0] == len(todo):
                print("  fetched %d/%d" % (done[0], len(todo)), flush=True)

    threads = []
    for pair in todo:
        thread = threading.Thread(target=worker, args=(pair,))
        thread.start()
        threads.append(thread)
        time.sleep(args.delay)
        if len(threads) >= args.workers:
            threads.pop(0).join()

    for thread in threads:
        thread.join()

    print("done: %d fetched, %d failed" % (done[0], len(failures)), flush=True)
    for surah, ayah, reason in failures[:20]:
        print("  FAILED %d:%d - %s" % (surah, ayah, reason), flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
