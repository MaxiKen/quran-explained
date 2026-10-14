"""LLM provider adapters over plain HTTPS (no SDKs).

    provider = make_provider('anthropic', model='claude-sonnet-4-5')
    res = provider.complete(system, user, max_tokens=32000)
    res.text, res.stop_reason ('stop' | 'length' | 'other'), res.usage

Keys come from the environment: ANTHROPIC_API_KEY, OPENAI_API_KEY,
GEMINI_API_KEY (or GOOGLE_API_KEY). The 'mock' provider needs none and is
used by the dry run and the tests.
"""
from __future__ import annotations

import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

DEFAULT_MODELS = {
    'anthropic': 'claude-sonnet-4-5',
    'openai': 'gpt-5',
    'gemini': 'gemini-2.5-pro',
    'mock': 'mock',
}

RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 529}


@dataclass
class Result:
    text: str
    stop_reason: str
    usage: dict = field(default_factory=dict)
    model: str = ''
    raw_status: int = 200


class ProviderError(RuntimeError):
    pass


def _post_json(url: str, headers: dict, body: dict, timeout: int, attempts: int = 6) -> tuple[int, dict]:
    data = json.dumps(body).encode('utf-8')
    last_err = None
    for attempt in range(attempts):
        req = urllib.request.Request(url, data=data, method='POST',
                                     headers={'Content-Type': 'application/json', **headers})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            payload = e.read().decode('utf-8', 'replace')
            if e.code in RETRY_STATUS and attempt < attempts - 1:
                retry_after = e.headers.get('retry-after')
                wait = float(retry_after) if retry_after and retry_after.replace('.', '', 1).isdigit() \
                    else min(90, (2 ** attempt) * 2 + random.uniform(0, 1.5))
                time.sleep(wait)
                last_err = ProviderError(f'HTTP {e.code}: {payload[:400]}')
                continue
            raise ProviderError(f'HTTP {e.code}: {payload[:800]}') from None
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            last_err = ProviderError(f'network: {e}')
            if attempt < attempts - 1:
                time.sleep(min(90, (2 ** attempt) * 2 + random.uniform(0, 1.5)))
                continue
            raise last_err
    raise last_err or ProviderError('unreachable')


class Provider:
    name = 'base'

    def __init__(self, model: str, timeout: int = 900):
        self.model = model
        self.timeout = timeout

    def complete(self, system: str, user: str, *, max_tokens: int = 32000, temperature: float = 0.4) -> Result:
        raise NotImplementedError


class Anthropic(Provider):
    name = 'anthropic'
    URL = 'https://api.anthropic.com/v1/messages'

    def complete(self, system, user, *, max_tokens=32000, temperature=0.4):
        key = os.environ.get('ANTHROPIC_API_KEY')
        if not key:
            raise ProviderError('ANTHROPIC_API_KEY is not set')
        body = {
            'model': self.model,
            'max_tokens': max_tokens,
            'temperature': temperature,
            # the system prompt is identical for every job: cache it
            'system': [{'type': 'text', 'text': system, 'cache_control': {'type': 'ephemeral'}}],
            'messages': [{'role': 'user', 'content': user}],
        }
        status, data = _post_json(self.URL, {
            'x-api-key': key, 'anthropic-version': '2023-06-01',
        }, body, self.timeout)
        text = ''.join(part.get('text', '') for part in data.get('content', []) if part.get('type') == 'text')
        stop = data.get('stop_reason')
        usage = data.get('usage', {})
        return Result(text=text, stop_reason={'end_turn': 'stop', 'stop_sequence': 'stop', 'max_tokens': 'length'}.get(stop, 'other'),
                      usage={'input': usage.get('input_tokens', 0) + usage.get('cache_read_input_tokens', 0) + usage.get('cache_creation_input_tokens', 0),
                             'cached': usage.get('cache_read_input_tokens', 0),
                             'output': usage.get('output_tokens', 0)},
                      model=data.get('model', self.model), raw_status=status)


class OpenAI(Provider):
    name = 'openai'
    URL = 'https://api.openai.com/v1/chat/completions'

    def complete(self, system, user, *, max_tokens=32000, temperature=0.4):
        key = os.environ.get('OPENAI_API_KEY')
        if not key:
            raise ProviderError('OPENAI_API_KEY is not set')
        reasoning_family = bool(re.match(r'^(gpt-5|o\d)', self.model))
        body = {
            'model': self.model,
            'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
            'max_completion_tokens': max_tokens,
        }
        if reasoning_family:
            body['reasoning_effort'] = os.environ.get('OPENAI_REASONING_EFFORT', 'low')
        else:
            body['temperature'] = temperature
        status, data = _post_json(self.URL, {'Authorization': f'Bearer {key}'}, body, self.timeout)
        choice = (data.get('choices') or [{}])[0]
        text = (choice.get('message') or {}).get('content') or ''
        finish = choice.get('finish_reason')
        usage = data.get('usage', {})
        return Result(text=text, stop_reason={'stop': 'stop', 'length': 'length'}.get(finish, 'other'),
                      usage={'input': usage.get('prompt_tokens', 0),
                             'cached': (usage.get('prompt_tokens_details') or {}).get('cached_tokens', 0),
                             'output': usage.get('completion_tokens', 0)},
                      model=data.get('model', self.model), raw_status=status)


class Gemini(Provider):
    name = 'gemini'
    URL = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'

    def complete(self, system, user, *, max_tokens=32000, temperature=0.4):
        key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not key:
            raise ProviderError('GEMINI_API_KEY is not set')
        body = {
            'systemInstruction': {'parts': [{'text': system}]},
            'contents': [{'role': 'user', 'parts': [{'text': user}]}],
            'generationConfig': {'maxOutputTokens': max_tokens, 'temperature': temperature},
        }
        budget = os.environ.get('GEMINI_THINKING_BUDGET')
        if budget is not None:
            body['generationConfig']['thinkingConfig'] = {'thinkingBudget': int(budget)}
        status, data = _post_json(self.URL.format(model=self.model), {'x-goog-api-key': key}, body, self.timeout)
        cands = data.get('candidates') or [{}]
        parts = (cands[0].get('content') or {}).get('parts') or []
        text = ''.join(p.get('text', '') for p in parts if 'text' in p)
        finish = cands[0].get('finishReason')
        usage = data.get('usageMetadata', {})
        return Result(text=text, stop_reason={'STOP': 'stop', 'MAX_TOKENS': 'length'}.get(finish, 'other'),
                      usage={'input': usage.get('promptTokenCount', 0),
                             'cached': usage.get('cachedContentTokenCount', 0),
                             'output': usage.get('candidatesTokenCount', 0)},
                      model=self.model, raw_status=status)


class Mock(Provider):
    """Produces structurally valid entries from the job text itself so the
    whole pipeline can be exercised without a key. The prose is placeholder
    prose; the gates still run on it."""
    name = 'mock'

    def complete(self, system, user, *, max_tokens=32000, temperature=0.4):
        from mock_writer import write_mock  # local import: keeps providers.py free of pipeline imports
        text = write_mock(user)
        return Result(text=text, stop_reason='stop',
                      usage={'input': len(system + user) // 4, 'cached': len(system) // 4, 'output': len(text) // 4},
                      model='mock')


def make_provider(name: str, model: str | None = None, timeout: int = 900) -> Provider:
    name = (name or 'mock').lower()
    model = model or DEFAULT_MODELS.get(name)
    cls = {'anthropic': Anthropic, 'openai': OpenAI, 'gemini': Gemini, 'mock': Mock}.get(name)
    if not cls:
        raise ProviderError(f'unknown provider {name!r}; choose anthropic | openai | gemini | mock')
    return cls(model, timeout=timeout)
