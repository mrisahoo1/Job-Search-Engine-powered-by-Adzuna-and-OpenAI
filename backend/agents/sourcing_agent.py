from __future__ import annotations

from backend.services.models import SearchPreference, SearchResponse
from backend.services.search import search_jobs


class SourcingAgent:
    """Coordinates compliant source discovery for a candidate search."""

    def run(self, resume_text: str, preferences: SearchPreference) -> SearchResponse:
        return search_jobs(resume_text, preferences)
