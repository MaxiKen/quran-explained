"""The 'mock' provider's writer: turns a job prompt into structurally valid
placeholder entries so the pipeline can be exercised end to end without an
API key. It is deliberately dull prose. It exists for plumbing tests only."""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify import extract_anchors  # noqa: E402


def _phrases(translation: str) -> list[str]:
    t = translation.strip()
    parts = [p.strip(' ,;:.!?') for p in re.split(r'[,:;.!?—]|\s[-–]\s', t) if p.strip(' ,;:.!?')]
    return parts or [t]


def _entry(ref: str, translation: str, anchors: list[str]) -> str:
    phrases = _phrases(translation)
    quote = translation.strip()
    lines = [
        f'This verse says "{quote}". It stands in its surah as one step in the argument the passage makes, '
        f'and it is addressed to everyone who reads it. The entry below walks through its wording and gathers '
        f'what is said about it.',
        '',
        '### Phrase by phrase',
        '',
    ]
    for p in phrases:
        lines.append(f'**"{p}"** This phrase carries the plain sense of the words as the translation gives them.')
        lines.append('')
    if anchors:
        lines.append('### What else the verse teaches')
        lines.append('')
        for a in anchors[:400]:
            lines.append(f'- The material mentions {a}.')
        lines.append('')
    lines += ['### In short', '', f'- The verse says "{quote}".', '- Its wording is explained phrase by phrase above.']
    text = '\n'.join(lines)
    # the mock must obey the same rules as a real model
    text = text.replace('—', ',').replace(';', ',')
    text = re.sub(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDF9\uFDFB-\uFDFF\uFE70-\uFEFF]+', '', text)
    text = re.sub(r'\bthe material mentions\b', 'Mentioned here:', text)
    return text


def write_mock(user: str) -> str:
    m = re.search(r'^Write the introduction to Surah (\d+)', user, re.M)
    material = user.split('# The material', 1)[-1]
    if m:
        s = m.group(1)
        anchors = list(extract_anchors(material).values())
        body = ['This surah opens the reader to its themes and sets out its central message in a few movements.', '',
                '### What the surah covers', '']
        for a in anchors[:200]:
            body.append(f'- Mentioned here: {a}.')
        body += ['', '### In short', '', '- The surah has a clear central message.', '- Its themes follow one another in order.']
        text = '\n'.join(body).replace(';', ',').replace('—', ',')
        return f'<<<INTRO {s}>>>\n{text}\n<<<END>>>\n\n<<<NOTES>>>\nnone\n<<<END>>>\n'
    out = []
    matches = list(re.finditer(r'^## (\d+):(\d+)\n(?:.*\n)*?Translation: "(.*?)"\s*$', user, re.M))
    anchors = list(extract_anchors(material).values())
    for i, vm in enumerate(matches):
        ref = f'{vm.group(1)}:{vm.group(2)}'
        share = anchors[i::max(1, len(matches))]  # distribute the material, as a real entry set would
        out.append(f'<<<VERSE {ref}>>>\n{_entry(ref, vm.group(3), share)}\n<<<END>>>\n')
    out.append('<<<NOTES>>>\nnone\n<<<END>>>\n')
    return '\n'.join(out)
