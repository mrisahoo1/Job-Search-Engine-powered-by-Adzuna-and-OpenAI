from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.models import FitEvaluation, JobPosting, to_jsonable
from backend.services.resume_tailor import create_resume_draft


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self._send_json({}, 204)

    def do_POST(self):
        try:
            payload = _read_payload(self)
            resume_text = str(payload.get('resumeText') or '').strip()
            job = _job_from_payload(payload.get('job') or {})
            evaluation = _evaluation_from_payload(payload.get('evaluation') or {})
            instructions = str(payload.get('instructions') or '')
            draft = create_resume_draft(resume_text, job, evaluation, instructions)
            self._send_json(to_jsonable(draft), 200)
        except Exception as exc:
            self._send_json({'message': str(exc) or 'Resume tailoring failed.'}, 500)

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


def _read_payload(request: BaseHTTPRequestHandler) -> dict:
    length = int(request.headers.get('content-length', '0'))
    return json.loads(request.rfile.read(length).decode('utf-8') or '{}')


def _job_from_payload(data: dict) -> JobPosting:
    return JobPosting(
        id=str(data.get('id') or ''),
        source_id=str(data.get('sourceId') or data.get('source_id') or ''),
        source_name=str(data.get('sourceName') or data.get('source_name') or ''),
        title=str(data.get('title') or ''),
        company=str(data.get('company') or ''),
        location=str(data.get('location') or ''),
        country=str(data.get('country') or ''),
        remote=str(data.get('remote') or 'unknown'),
        visa_sponsorship=str(data.get('visaSponsorship') or data.get('visa_sponsorship') or 'unknown'),
        description=str(data.get('description') or ''),
        tags=[str(item) for item in data.get('tags') or []],
        apply_url=str(data.get('applyUrl') or data.get('apply_url') or ''),
        fetched_at=str(data.get('fetchedAt') or data.get('fetched_at') or ''),
        posted_at=data.get('postedAt') or data.get('posted_at'),
    )


def _evaluation_from_payload(data: dict) -> FitEvaluation:
    return FitEvaluation(
        job_id=str(data.get('jobId') or data.get('job_id') or ''),
        score=int(data.get('score') or 0),
        confidence=str(data.get('confidence') or 'low'),
        recommendation=str(data.get('recommendation') or 'low-fit'),
        matched_skills=[str(item) for item in data.get('matchedSkills') or data.get('matched_skills') or []],
        missing_skills=[str(item) for item in data.get('missingSkills') or data.get('missing_skills') or []],
        strengths=[str(item) for item in data.get('strengths') or []],
        risks=[str(item) for item in data.get('risks') or []],
        signal_notes=[str(item) for item in data.get('signalNotes') or data.get('signal_notes') or []],
    )
