#!/usr/bin/env python3
"""What can a workflow get from GitHub Models with the workflow's own token?

    GITHUB_TOKEN=… python3 tools/probe_models.py

GitHub Models is served at models.github.ai, which the sandbox cannot reach;
a GitHub Actions runner can. This asks the free hosted models a question in
the shape the pairing pipeline will use, prints the rate-limit headers, and
writes the answer to work/raw/probe-models.txt so it can be read back from
the branch.

No provider key is involved: the workflow's own token is enough.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

URL = 'https://models.github.ai/inference/chat/completions'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'work', 'raw', 'probe-models.txt')

MODELS = ['openai/gpt-4o-mini', 'meta-llama/Llama-3.3-70B-Instruct']

SYSTEM = (
    'You split a Qur\'an verse into phrases and say which part of a commentary '
    'explains each phrase. Answer with JSON only.'
)

USER = """Modern English translation of the verse:
This is the Book! There is no doubt about it—a guide for those mindful of Allah

The Arabic of the verse:
ذَٰلِكَ الْكِتَابُ لَا رَيْبَ فِيهِ ۛ هُدًى لِّلْمُتَّقِينَ

The commentary, as numbered parts:
[0] The explanation of the saying of Allah, the Exalted: That is the Book (dhālika al-kitāb) — the meaning of it is: this is the Book.
[1] There is no doubt (lā rayb) in it — and the meaning of that is: there is no doubt in it, and no confusion in it.
[2] It is a guide (hudan) for the mindful (al-muttaqīn) — the mindful are those who avoid the forbidden and perform the obligations.

Answer with JSON of this shape and nothing else:
{"phrases":[{"text":"a verbatim span of the modern English","arabic":"the Arabic of that span, verbatim","parts":[0]}]}"""


def call(token: str, model: str, system: str, user: str, max_tokens: int = 1500) -> tuple[int, dict, str]:
    body = {
        'model': model,
        'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
        'temperature': 0.1,
        'max_tokens': max_tokens,
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode('utf-8'),
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return resp.status, dict(resp.headers), resp.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers or {}), exc.read().decode('utf-8', 'replace')
    except Exception as exc:  # network, timeout
        return 0, {}, 'ERROR: %s' % exc


def main() -> int:
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not token:
        print('no GITHUB_TOKEN in the environment')
        return 1
    lines = []
    for model in MODELS:
        status, headers, text = call(token, model, SYSTEM, USER)
        limits = {k: v for k, v in headers.items() if k.lower().startswith('x-ratelimit')}
        lines.append('== %s -> HTTP %s' % (model, status))
        lines.append('   rate limits: %s' % (json.dumps(limits) if limits else '(none returned)'))
        if status == 200:
            try:
                data = json.loads(text)
                content = data['choices'][0]['message']['content']
                lines.append('   answer: %s' % content[:1800].replace('\n', ' '))
                lines.append('   usage: %s' % json.dumps(data.get('usage', {})))
            except Exception:
                lines.append('   raw: %s' % text[:600].replace('\n', ' '))
        else:
            lines.append('   raw: %s' % text[:600].replace('\n', ' '))
        lines.append('')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    sys.exit(main())
