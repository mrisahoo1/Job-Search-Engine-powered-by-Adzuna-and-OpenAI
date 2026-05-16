from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.services.llm import personalize_json
from backend.services.models import FitEvaluation, JobPosting, ResumeDraft, to_jsonable


def create_resume_draft(resume_text: str, job: JobPosting, evaluation: FitEvaluation, instructions: str = '') -> ResumeDraft:
    llm = personalize_json(
        (
            'You are a senior technical resume editor. Return only valid JSON with keys: '
            'draftText as a complete tailored resume string, changeSummary as an array of complete sentence strings, '
            'and warnings as an array of complete sentence strings. Tailor the resume to the specific job description, '
            'preserve only truthful facts from the supplied resume, and do not invent employers, dates, certifications, degrees, or tools.'
        ),
        {'resume': resume_text, 'job': to_jsonable(job), 'evaluation': to_jsonable(evaluation), 'instructions': instructions},
    )
    if llm is not None:
        draft_text = _text_value(llm.get('draftText') or llm.get('draft_text'))
        if not draft_text:
            raise ValueError('LLM returned an empty tailored resume draft.')
        return ResumeDraft(
            id=f'draft:{job.id}:{abs(hash(resume_text + job.id))}',
            job_id=job.id,
            base_resume_text=resume_text,
            draft_text=draft_text,
            change_summary=_text_list(llm.get('changeSummary') or llm.get('change_summary')) or [f'Tailored the resume for {job.title} at {job.company}.'],
            warnings=_text_list(llm.get('warnings')),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    matched = evaluation.matched_skills[:6]
    missing = evaluation.missing_skills
    job_keywords = ', '.join(job.tags[:6] or matched or [job.title])
    emphasis = ', '.join(matched) if matched else 'the closest truthful evidence from the resume'
    draft_text = (
        f'{job.title} target CV for {job.company}\n\n'
        f'Professional Summary\n- Candidate positioning for {job.company}: emphasize {emphasis}.\n'
        f'- Role context from JD: {job.description[:420]}\n\n'
        f'Curated Resume Content\n{resume_text.strip()}\n\n'
        f'Keyword Alignment\n- Include only truthful evidence related to: {job_keywords}.'
    )
    if instructions:
        draft_text += f'\n\nUser Instructions\n- {instructions}'
    return ResumeDraft(
        id=f'draft:{job.id}:{abs(hash(resume_text + job.id))}', job_id=job.id, base_resume_text=resume_text, draft_text=draft_text.strip(),
        change_summary=[
            f'Repositioned the CV for {job.title} at {job.company}.',
            f'Used JD-specific context from {job.company}: {job.description[:120]}...',
            f'Highlighted matched evidence: {emphasis}.',
            'Kept unsupported requirements out of the draft.',
        ],
        warnings=[f'{skill} appears in the JD but was not found in the resume. Add only if truthful.' for skill in missing],
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in (_text_value(entry) for entry in value) if item]
    text = _text_value(value)
    return [text] if text else []


def _text_value(value: Any) -> str:
    if value is None:
        return ''
    if isinstance(value, (dict, list)):
        return ''
    return str(value).strip()
