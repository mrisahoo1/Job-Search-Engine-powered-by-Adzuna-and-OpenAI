from __future__ import annotations

import base64
import binascii
import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.models import to_jsonable
from backend.services.resume_file_parser import parse_resume_file


def parse_resume_payload(payload: dict[str, Any]) -> dict[str, Any]:
    file_name = str(payload.get('fileName') or 'resume.txt').strip() or 'resume.txt'
    data_url = str(payload.get('data') or '').strip()
    if not data_url:
        raise ValueError('Missing resume file data.')

    encoded = data_url.split(',', 1)[1] if ',' in data_url else data_url
    try:
        content = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError('Resume upload data was not valid base64.') from exc

    parsed = parse_resume_file(file_name, content)
    return to_jsonable(parsed)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self._send_json({}, 204)

    def do_POST(self):
        try:
            length = int(self.headers.get('content-length', '0'))
            payload = json.loads(self.rfile.read(length).decode('utf-8') or '{}')
            self._send_json(parse_resume_payload(payload), 200)
        except Exception as exc:
            self._send_json({'message': str(exc) or 'Resume parsing failed.'}, 400)

    def _send_json(self, payload, status: int):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if status != 204:
            self.wfile.write(body)
