from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.agents.sourcing_agent import SourcingAgent
from backend.services.models import SearchPreference, to_jsonable


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self._send_json({}, 204)

    def do_POST(self):
        try:
            length = int(self.headers.get('content-length', '0'))
            payload = json.loads(self.rfile.read(length).decode('utf-8') or '{}')
            resume_text = str(payload.get('resumeText') or '').strip()
            if not resume_text:
                self._send_json({'message': 'Resume text is required before searching.'}, 400)
                return
            preferences = _preferences_from_payload(payload.get('preferences') or {})
            response = SourcingAgent().run(resume_text, preferences)
            self._send_json(to_jsonable(response), 200)
        except Exception as exc:
            self._send_json({'message': str(exc) or 'Search failed.'}, 500)

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


def _preferences_from_payload(payload: dict) -> SearchPreference:
    return SearchPreference(
        query=str(payload.get('query') or 'software engineer'),
        region=str(payload.get('region') or payload.get('regionId') or 'eu_uk'),
        countries=[str(item) for item in payload.get('countries') or []],
        remote_only=bool(payload.get('remoteOnly') or payload.get('remote_only') or False),
        visa_sponsorship=str(payload.get('visaSponsorship') or payload.get('visa_sponsorship') or 'preferred'),
        sources=[str(item) for item in payload.get('sources') or ['deep', 'official']],
        official_companies=[str(item) for item in payload.get('officialCompanies') or payload.get('official_companies') or ['bmw', 'example-greenhouse']],
        search_mode=str(payload.get('searchMode') or payload.get('search_mode') or 'live'),
    )
