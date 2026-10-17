"""Import Tafsir al-Tabari from tafseerquran.com.

For every ayah the site publishes one passage of the English translation of
Jami al-bayan an tawil ay al-Quran, and — behind a collapsed "Show original
Arabic" panel — the Arabic text of the same commentary. This script fetches
those pages, extracts both, and writes one JSON file per surah in the shape
the reader uses for its tafsir payload:

    data/tafsir_NNN.json
      { "surah": 1, "lang": "en", "dir": "ltr",
        "source": "Tafsīr al-Ṭabarī", "primary": "tabari",
        "sources": [ { "id": "tabari", "label": ..., "author": ... } ],
        "notice": "...",
        "arabicSource": { "id": "tabariAr", "label": ..., "author": ... },
        "sets": { "tabari":    { "ranges": ["1:1", ...], "blocks": ["..."] },
                  "tabariAr":  { "ranges": ["1:1", ...], "blocks": ["..."] } },
        "verses": { "1": { "tabari": 0, "tabariAr": 0 }, ... } }

Tafsīr al-Ṭabarī is the reader's tafsir: the English translation is the
commentary the reader shows, and the Arabic original sits below it as the
text of record. The site itself says the Arabic is always authoritative.

Page structure (checked against the live site): every passage is rendered as

    <div class="...">Full English translation of Tabari's text</div>
    <div class="text-base"> <p>...</p> <p>...</p> ... </div>

followed by a collapsed panel

    <details><summary>Show original Arabic</summary>
    <div dir="rtl" lang="ar" class="font-arabic ..."> ... </div></details>

then the previous/next ayah links and the site footer. Only the text-base
container is the English passage and only the rtl/ar container is the Arabic
original, so each is taken on its own and nothing else is.

The site is crawled politely: a handful of workers, a short delay between
requests, retries with backoff, and every fetched page is cached on disk so a
re-run does not hit the site again.
"""

import argparse
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import fetch, repo_root, surah_verse_counts, tafsir_url  # noqa: E402

# --- Source metadata -------------------------------------------------------

SOURCE = {
    "id": "tabari",
    "label": "Tafsīr al-Ṭabarī",
    "author": "Imām Abū Jaʿfar Muḥammad ibn Jarīr al-Ṭabarī (d. 310 AH) · English translation",
}

ARABIC_SOURCE = {
    "id": "tabariAr",
    "label": "The Arabic original",
    "author": "Tafsīr al-Ṭabarī · the Arabic text of the commentary",
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

LABEL = "Full English translation of Tabari"
PASSAGE_CONTAINER = re.compile(r'<div class="text-base">')


class BlockCollector(HTMLParser):
    """Collect the block-level elements of a fragment, in document order.

    Only leaf blocks are kept: a wrapper element that contains block-level
    children is skipped, because its text is the concatenation of theirs.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []          # list of (tag, text)
        self._stack = []          # open block elements: [tag, parts, has_block_child]
        self._skip_depth = 0
        self._pending = []        # inline text of the current block

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
        if tag == "br":
            self._pending.append("\n")
            return
        if tag in BLOCK_TAGS:
            self._flush_inline()
            self._stack.append([tag, [], False])

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            if self._skip_depth:
                self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag == "br":
            return
        if tag in BLOCK_TAGS and self._stack:
            # text collected since the last tag belongs to the element that is
            # closing, so it has to be flushed before the element is popped
            self._flush_inline()
            depth = None
            for index in range(len(self._stack) - 1, -1, -1):
                if self._stack[index][0] == tag:
                    depth = index
                    break
            if depth is None:
                return
            while len(self._stack) > depth:
                element = self._stack.pop()
                if not element[2]:
                    self.blocks.append((element[0], "".join(element[1])))
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
            if not element[2]:
                self.blocks.append((element[0], "".join(element[1])))


def normalise(text):
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


def find_div_body(html, start, pattern):
    """Return the inner HTML of the first <div> matching `pattern` after `start`.

    The closing tag is found by counting <div> and </div>, so nested divs
    inside the container do not end it early.
    """
    match = pattern.search(html, start)
    if not match:
        return None
    return div_body(html, match)


def div_body(html, match):
    """Return the inner HTML of the <div> opened by `match`."""
    index = match.end()
    depth = 1
    while index < len(html):
        open_at = html.find("<div", index)
        close_at = html.find("</div>", index)
        if close_at == -1:
            return None
        if open_at != -1 and open_at < close_at:
            depth += 1
            index = open_at + 4
            continue
        depth -= 1
        index = close_at + 6
        if depth == 0:
            return html[match.end():index - 6]
    return None


def find_container(html, start):
    """Return the content of the <div class="text-base"> that starts after `start`."""
    return find_div_body(html, start, PASSAGE_CONTAINER)


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
        if out and out[-1] and line:
            out.append("")
        out.append(line)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return unescape_markdown(text.strip())


# The site keeps its text in markdown and renders it without handling the
# escapes, so the published page shows them: the section divider of the
# printed edition arrives as "\* \* \*", a quotation mark as "\" and a
# footnote reference as "\[other\]". The words are untouched; only the
# escapes are resolved here, and a divider becomes a horizontal rule.
SEPARATOR_LINE = re.compile(r"^[\s\\*\-]+$")
MARKDOWN_ESCAPE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!>~|'\"])")


def unescape_markdown(text):
    """Resolve the markdown escapes the site leaves in the published text."""
    # one passage in the corpus has its paragraph break written out as the
    # two characters \n; it is a line break, so it becomes one
    text = text.replace("\\n", "\n")
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if len(stripped) >= 3 and SEPARATOR_LINE.match(stripped):
            lines.append("---")
            continue
        lines.append(MARKDOWN_ESCAPE.sub(r"\1", line))
    return "\n".join(lines)


def extract_passage(html):
    """Return the English passage of an ayah page, or None when it has none."""
    labels = [match.start() for match in re.finditer(re.escape(LABEL), html)]
    if not labels:
        return None

    passages = []
    for index, label_at in enumerate(labels):
        limit = labels[index + 1] if index + 1 < len(labels) else len(html)
        container = find_container(html, label_at)
        if container is None or html.find(container) > limit:
            continue
        collector = BlockCollector()
        collector.feed(container)
        collector.close()
        blocks = [
            (tag, text)
            for tag, text in collector.blocks
            if normalise(text)
        ]
        if not blocks:
            continue
        passages.append(blocks_to_markdown(blocks))

    if not passages:
        return None
    return "\n\n".join(passages)


# The Arabic original sits behind a collapsed panel on every page. The panel is
# marked by its summary, and the text itself is the right-to-left container
# inside it. The container's class list also carries a "text-base" token, so
# the English container is matched on its exact class attribute and the Arabic
# one on its dir/lang attributes — the two can never be confused.
ARABIC_LABEL = "Show original Arabic"
ARABIC_CONTAINER = re.compile(r"<div[^>]*>")


def find_arabic_div(html, start):
    """Return the match of the right-to-left Arabic container after `start`."""
    for match in ARABIC_CONTAINER.finditer(html, start):
        tag = match.group(0)
        if 'dir="rtl"' in tag and 'lang="ar"' in tag:
            return match
    return None


class TextCollector(HTMLParser):
    """Collect the text of a fragment, keeping its paragraph breaks.

    The Arabic panel holds plain text (or a couple of paragraphs), not the
    block structure the English passage is built from, so it is read as text.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self._skip += 1
        elif tag == "br":
            self.parts.append("\n")
        elif tag in BLOCK_TAGS:
            self.parts.append("\n\n")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            if self._skip:
                self._skip -= 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n\n")

    def handle_data(self, data):
        if self._skip:
            return
        self.parts.append(data)

    def text(self):
        raw = "".join(self.parts)
        paragraphs = []
        for part in re.split(r"\n\s*\n", raw):
            part = normalise(part)
            if part:
                paragraphs.append(part)
        return "\n\n".join(paragraphs)


def extract_arabic(html):
    """Return the Arabic original of an ayah page, or None when it has none."""
    marker = html.find(ARABIC_LABEL)
    if marker == -1:
        return None
    match = find_arabic_div(html, marker)
    if match is None:
        return None
    container = div_body(html, match)
    if not container:
        return None
    collector = TextCollector()
    collector.feed(container)
    collector.close()
    text = collector.text()
    return text or None


# --- Import ---------------------------------------------------------------

_print_lock = threading.Lock()


def page_path(raw_dir, surah, ayah):
    return os.path.join(raw_dir, "%03d_%03d.html" % (surah, ayah))


def read_page(surah, ayah, args):
    """Return the page HTML for an ayah, from the cache or from the site."""
    target = page_path(args.raw, surah, ayah)
    if os.path.exists(target) and not args.refetch:
        with open(target, "r", encoding="utf-8") as fh:
            return fh.read()
    html = fetch(tafsir_url(surah, ayah))
    if html is None:
        return None
    os.makedirs(args.raw, exist_ok=True)
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(html)
    time.sleep(args.delay)
    return html


def import_surah(surah, count, args):
    results = {}
    arabics = {}

    def one(ayah):
        try:
            html = read_page(surah, ayah, args)
        except Exception as exc:  # noqa: BLE001 - reported, not fatal
            return ayah, None, None, str(exc)
        if html is None:
            return ayah, None, None, "not found"
        text = extract_passage(html)
        arabic = extract_arabic(html) if text else None
        return ayah, text, arabic, None

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for ayah, text, arabic, error in pool.map(one, range(1, count + 1)):
            if text:
                results[ayah] = text
                if arabic:
                    arabics[ayah] = arabic
            elif error:
                with _print_lock:
                    print("  %d:%d - %s" % (surah, ayah, error), flush=True)
            else:
                with _print_lock:
                    print("  %d:%d - no passage on the page" % (surah, ayah), flush=True)

    missing = [ayah for ayah in range(1, count + 1) if ayah not in results]
    if missing:
        with _print_lock:
            print(
                "surah %d incomplete: %d/%d verses (%d missing)"
                % (surah, len(results), count, len(missing)),
                flush=True,
            )
        return {"status": "incomplete", "missing": missing, "verses": len(results)}

    without_arabic = [ayah for ayah in range(1, count + 1) if ayah not in arabics]
    if without_arabic:
        with _print_lock:
            print(
                "surah %d: %d verse(s) without the Arabic original: %s"
                % (surah, len(without_arabic), without_arabic[:10]),
                flush=True,
            )

    blocks = [results[ayah] for ayah in range(1, count + 1)]
    # a verse with no Arabic panel still gets an entry, so the reader can
    # show the English on its own without a hole in the mapping
    arabic_blocks = [arabics.get(ayah, "") for ayah in range(1, count + 1)]
    ranges = ["%d:%d" % (surah, ayah) for ayah in range(1, count + 1)]
    payload = {
        "surah": surah,
        "lang": "en",
        "dir": "ltr",
        "source": SOURCE["label"],
        "primary": SOURCE["id"],
        "sources": [SOURCE],
        "notice": NOTICE,
        "arabicSource": ARABIC_SOURCE,
        "sets": {
            "tabari": {"ranges": ranges, "blocks": blocks},
            "tabariAr": {"ranges": ranges, "blocks": arabic_blocks},
        },
        # the reader maps every verse to a block index per source
        "verses": {
            str(ayah): {"tabari": ayah - 1, "tabariAr": ayah - 1}
            for ayah in range(1, count + 1)
        },
    }
    path = os.path.join(args.out, "tafsir_%03d.json" % surah)
    os.makedirs(args.out, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
    with _print_lock:
        print(
            "surah %d ok: %d verses, %d with the Arabic original"
            % (surah, count, len(arabics)),
            flush=True,
        )
    return {
        "status": "ok",
        "verses": count,
        "arabic": len(arabics),
        "bytes": os.path.getsize(path),
    }


def migrate_file(path):
    """Rewrite a data file written with a flat verse map into the nested one.

    The first import wrote `verses: { "1": 0 }`; the reader expects the map
    to name the source it belongs to, so it is rewritten as
    `verses: { "1": { "tabari": 0 } }`. Files that are already nested are left
    alone.
    """
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    changed = False
    verses = payload.get("verses", {})
    for ayah in list(verses.keys()):
        value = verses[ayah]
        if isinstance(value, int):
            verses[ayah] = {"tabari": value}
            changed = True
    if changed:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
    return changed


def normalise_file(path):
    """Resolve the markdown escapes in an already imported data file."""
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    changed = False
    for source, source_set in (payload.get("sets") or {}).items():
        blocks = source_set.get("blocks", [])
        for index, text in enumerate(blocks):
            fixed = unescape_markdown(text)
            if fixed != text:
                blocks[index] = fixed
                changed = True
    if changed:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default="tools/tabari/plan.json")
    parser.add_argument("--out", default="data")
    parser.add_argument("--raw", default="work/tabari/raw")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--refetch", action="store_true")
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="rewrite existing data files into the current shape and stop",
    )
    parser.add_argument(
        "--normalise",
        action="store_true",
        help="resolve the markdown escapes in existing data files and stop",
    )
    args = parser.parse_args()

    root = repo_root()
    os.chdir(root)

    if args.normalise:
        changed = []
        for name in sorted(os.listdir(args.out)):
            if name.startswith(("tabari_", "tafsir_")) and name.endswith(".json"):
                if normalise_file(os.path.join(args.out, name)):
                    changed.append(name)
        print("normalised %d file(s)" % len(changed))
        for name in changed:
            print("  " + name)
        return 0

    if args.migrate:
        changed = []
        for name in sorted(os.listdir(args.out)):
            if name.startswith(("tabari_", "tafsir_")) and name.endswith(".json"):
                if migrate_file(os.path.join(args.out, name)):
                    changed.append(name)
        print("migrated %d file(s)" % len(changed))
        for name in changed:
            print("  " + name)
        return 0

    with open(args.plan, "r", encoding="utf-8") as fh:
        plan = json.load(fh)
    surahs = [int(value) for value in plan.get("surahs", [])]
    counts = surah_verse_counts(root)
    for surah in surahs:
        if surah not in counts:
            raise SystemExit("unknown surah %d" % surah)

    print("importing %d surah(s) into %s" % (len(surahs), args.out), flush=True)
    results = {}
    for surah in surahs:
        results[surah] = import_surah(surah, counts[surah], args)

    report = os.path.join("work", "tabari", "report.json")
    os.makedirs(os.path.dirname(report), exist_ok=True)
    with open(report, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    ok = sum(1 for value in results.values() if value["status"] == "ok")
    print("done: %d/%d surahs complete" % (ok, len(surahs)), flush=True)
    # A surah that is still incomplete is reported, not treated as a crash:
    # the surahs that did import are still committed, and the missing ones
    # can be imported on a later run.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
