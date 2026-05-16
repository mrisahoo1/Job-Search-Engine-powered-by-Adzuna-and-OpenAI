from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class LLMError(RuntimeError):
    pass


def personalize_json(system_prompt: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    if not api_key:
        return None
    body = json.dumps({
        'model': model,
        'input': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': json.dumps(payload)},
        ],
        'text': {'format': {'type': 'json_object'}},
    }).encode('utf-8')
    request = urllib.request.Request(
        'https://api.openai.com/v1/responses',
        data=body,
        method='POST',
        headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
        text = _extract_text(result)
        if not text:
            raise LLMError('LLM returned no text content.')
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            raise LLMError('LLM returned JSON that was not an object.')
        return parsed
    except urllib.error.HTTPError as exc:
        raise LLMError(f'LLM personalization failed with HTTP {exc.code}. Check OPENAI_API_KEY and OPENAI_MODEL.') from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise LLMError('LLM personalization failed because the OpenAI request could not complete.') from exc
    except json.JSONDecodeError as exc:
        raise LLMError('LLM personalization returned invalid JSON.') from exc


def _extract_text(result: dict[str, Any]) -> str:
    if isinstance(result.get('output_text'), str):
        return result['output_text']
    chunks: list[str] = []
    for item in result.get('output', []) or []:
        for content in item.get('content', []) or []:
            if content.get('type') in {'output_text', 'text'} and isinstance(content.get('text'), str):
                chunks.append(content['text'])
    return ''.join(chunks).strip()
