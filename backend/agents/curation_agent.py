from __future__ import annotations

from backend.services.models import FitEvaluation, JobPosting, ResumeDraft
from backend.services.resume_tailor import create_resume_draft
from backend.services.outreach import create_outreach_drafts


class CurationAgent:
    """Creates truthful application materials for a selected job."""

    def tailor_resume(self, resume_text: str, job: JobPosting, evaluation: FitEvaluation, instructions: str = '') -> ResumeDraft:
        return create_resume_draft(resume_text, job, evaluation, instructions)

    def draft_outreach(self, candidate_name: str, candidate_headline: str, job: JobPosting, evaluation: FitEvaluation):
        return create_outreach_drafts(candidate_name, candidate_headline, job, evaluation)
