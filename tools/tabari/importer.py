"""Import the English Tafsir al-Tabari from tafseerquran.com.

For every ayah the site publishes one passage of the English translation of
Jami al-bayan an tawil ay al-Quran. This script fetches those pages, extracts
the passage text, and writes one JSON file per surah in the shape the reader
already uses for its tafsir payloads:

    data/tabari_NNN.json
      { "surah": 1, "lang": "en", "dir": "ltr",
        "sources": [ { "id": "tabari", "label": ..., "author": ... } ],
        "sets": { "tabari": { "ranges": ["1:1", ...], "blocks": ["...", ...] } },
        "verses": { "1": { "tabari": 0 }, "2": { "tabari": 1 }, ... } }

The reader merges the file into the surah's tafsir payload at load time, so
Tabari appears as one more source alongside the eight classical tafsirs.

The site is crawled politely: a modest number of workers, a short delay
between requests, retries with backoff, and every fetched page is cached on
disk so a re-run does not hit the site again.
"""

import argparse
import json
import os
import re
import sys
import threading
import time
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import fetch, repo_root, surah_verse_counts, tafsir_url  # noqa: E402

# --- Source metadata -------------------------------------------------------

SOURCE = {
    "id": "tabari",
    "label": "Tafsīr al-Ṭabarī",
    "author": "Imām Abū Jaʿfar Muḥammad ibn Jarīr al-Ṭabarī (d. 310 AH) · English translation",
}

# The site's own notice, kept with the text so the reader can show it.
NOTICE = (
    "The Arabic source text is always authoritative. This translation is a study aid "
    "and has not been verified by scholars — do not use it as a basis for religious "
    "proof or for deriving rulings (ahkam). When in doubt, always consult the Arabic "
    "text and a qualified scholar."
)

# --- HTML extraction -------------------------------------------------------

BLOCK_TAGS = {
    "p", "div", "section", "article", "main", "aside", "header", "footer", "nav",
    "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "ul", "ol", "pre",
    "figure", "figcaption", "table", "tr", "td", "th", "dl", "dt", "dd",
}
SKIP_TAGS = {"script", "style", "noscript", "svg", "template", "iframe"}


class BlockCollector(HTMLParser):
    """Collect the block-level elements of a page, in document order.

    Only leaf blocks are kept: a wrapper element that contains block-level
    children is skipped, because its text is the concatenation of theirs.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []          # list of (tag, text)
        self._stack = []          # open block elements: [tag, parts, has_block_child]
        self._skip_depth = 0
        self._pending = []        # inline text of the current block

    # -- helpers
    def _flush_inline(self):
        if self._stack:
            self._stack[-1][1].append("".join(self._pending))
        self._pending = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in ("br",):
            self._pending.append("\n")
            return
        if tag in BLOCK_TAGS:
            self._flush_inline()
            self._stack.append([tag, [], False])
        else:
            self._pending.append("")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            if self._skip_depth:
                self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag in ("br",):
            return
        if tag in BLOCK_TAGS and self._stack:
            # text collected since the last tag belongs to the element that is
            # closing, so it has to be flushed before the element is popped
            self._flush_inline()
            # close the innermost matching block
            depth = None
            for index in range(len(self._stack) - 1, -1, -1):
                if self._stack[index][0] == tag:
                    depth = index
                    break
            if depth is None:
                return
            while len(self._stack) > depth:
                element = self._stack.pop()
                text = "".join(element[1])
                if not element[2]:
                    self.blocks.append((element[0], text))
            if self._stack:
                self._stack[-1][2] = True

    def handle_data(self, data):
        if self._skip_depth:
            return
        self._pending.append(data)

    def close(self):
        super().close()
        self._flush_inline()
        while self._stack:
            element = self._stack.pop()
            text = "".join(element[1])
            if not element[2]:
                self.blocks.append((element[0], text))


# Markers that delimit the passage on the page.
PASSAGE_LABEL = re.compile(r"full english translation of tabari", re.I)
STOP_MARKERS = re.compile(
    r"^(read tabari|go to ayah|related passages|previous|next|back to|"
    r"share|feedback|©|all rights|privacy|terms)",
    re.I,
)


def normalise(text):
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


def blocks_to_markdown(blocks):
    """Turn the collected blocks into the markdown subset the reader renders."""
    lines = []
    for tag, raw in blocks:
        text = normalise(raw)
        if not text:
            continue
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = min(int(tag[1]) + 1, 5)
            lines.append("%s %s" % ("#" * level, text))
        elif tag == "li":
            lines.append("- %s" % text)
        elif tag == "blockquote":
            lines.append("> %s" % text)
        else:
            lines.append(text)
    out = []
    for line in lines:
        if out and out[-1] and out[-1][-1] not in "\n" and line:
            out.append("")
        out.append(line)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_passage(html):
    """Return the passage text of an ayah page, or None when it is not there."""
    collector = BlockCollector()
    collector.feed(html)
    collector.close()
    blocks = collector.blocks

    start = None
    for index, (tag, text) in enumerate(blocks):
        if PASSAGE_LABEL.search(normalise(text)):
            start = index + 1
            break
    if start is None:
        return None

    kept = []
    for tag, text in blocks[start:]:
        text = normalise(text)
        if not text:
            continue
        if STOP_MARKERS.match(text):
            break
        kept.append((tag, text))
    if not kept:
        return None
    return blocks_to_markdown(kept)


# --- Import ---------------------------------------------------------------

_print_lock = threading.Lock()


def page_path(raw_dir, surah, ayah):
    return os.path.join(raw_dir, "%03d_%03d.html" % (surah, ayah))


def import_surah(surah, count, args, results):
    blocks = []
    ranges = []
    verses = {}
    missing = []

    for ayah in range(1, count + 1):
        target = page_path(args.raw, surah, ayah)
        html = None
        if os.path.exists(target) and not args.refetch:
            with open(target, "r", encoding="utf-8") as fh:
                html = fh.read()
        else:
            try:
                html = fetch(tafsir_url(surah, ayah))
            except Exception as exc:  # noqa: BLE001 - reported, not fatal
                with _print_lock:
                    print("  fetch failed %d:%d - %s" % (surah, ayah, exc), flush=True)
                missing.append(ayah)
                continue
            if html is None:
                missing.append(ayah)
                continue
            os.makedirs(args.raw, exist_ok=True)
            with open(target, "w", encoding="utf-8") as fh:
                fh.write(html)
            time.sleep(args.delay)

        text = extract_passage(html)
        if not text:
            missing.append(ayah)
            continue
        index = len(blocks)
        blocks.append(text)
        ranges.append("%d:%d" % (surah, ayah))
        verses[str(ayah)] = index

    if missing or len(verses) != count:
        results[surah] = {"status": "incomplete", "missing": missing, "verses": len(verses)}
        with _print_lock:
            print(
                "surah %d incomplete: %d/%d verses (%d missing)"
                % (surah, len(verses), count, len(missing)),
                flush=True,
            )
        return

    payload = {
        "surah": surah,
        "lang": "en",
        "dir": "ltr",
        "source": SOURCE,
        "notice": NOTICE,
        "sets": {"tabari": {"ranges": ranges, "blocks": blocks}},
        "verses": verses,
    }
    path = os.path.join(args.out, "tabari_%03d.json" % surah)
    os.makedirs(args.out, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
    results[surah] = {"status": "ok", "verses": len(verses), "bytes": os.path.getsize(path)}
    with _print_lock:
        print("surah %d ok: %d verses" % (surah, len(verses)), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default="tools/tabari/plan.json")
    parser.add_argument("--out", default="data")
    parser.add_argument("--raw", default="work/tabari/raw")
    parser.add_argument("--delay", type=float, default=0.3)
    parser.add_argument("--refetch", action="store_true")
    args = parser.parse_args()

    root = repo_root()
    os.chdir(root)
    with open(args.plan, "r", encoding="utf-8") as fh:
        plan = json.load(fh)
    surahs = [int(s) for s in plan.get("surahs", [])]
    counts = surah_verse_counts(root)
    for surah in surahs:
        if surah not in counts:
            raise SystemExit("unknown surah %d" % surah)

    print("importing %d surah(s) into %s" % (len(surahs), args.out), flush=True)
    results = {}
    for surah in surahs:
        import_surah(surah, counts[surah], args, results)

    report = os.path.join("work", "tabari", "report.json")
    os.makedirs(os.path.dirname(report), exist_ok=True)
    with open(report, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    ok = sum(1 for value in results.values() if value["status"] == "ok")
    print("done: %d/%d surahs complete" % (ok, len(surahs)), flush=True)
    return 0 if ok == len(surahs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
