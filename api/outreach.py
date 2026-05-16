from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.tailor import _evaluation_from_payload, _job_from_payload, _read_payload
from backend.services.models import to_jsonable
from backend.services.outreach import create_outreach_drafts, infer_candidate_context


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self._send_json({}, 204)

    def do_POST(self):
        try:
            payload = _read_payload(self)
            resume_text = str(payload.get('resumeText') or '')
            inferred_name, inferred_headline = infer_candidate_context(resume_text)
            drafts = create_outreach_drafts(
                candidate_name=str(payload.get('candidateName') or inferred_name),
                candidate_headline=str(payload.get('candidateHeadline') or inferred_headline),
                job=_job_from_payload(payload.get('job') or {}),
                evaluation=_evaluation_from_payload(payload.get('evaluation') or {}),
                resume_text=resume_text,
            )
            self._send_json(to_jsonable(drafts), 200)
        except Exception as exc:
            self._send_json({'message': str(exc) or 'Outreach drafting failed.'}, 500)

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
