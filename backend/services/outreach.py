from __future__ import annotations

import re
from urllib.parse import quote
from typing import Any

from backend.services.llm import personalize_json
from backend.services.models import FitEvaluation, JobPosting, OutreachDraft, to_jsonable


def create_outreach_drafts(
    candidate_name: str,
    candidate_headline: str,
    job: JobPosting,
    evaluation: FitEvaluation,
    resume_text: str = '',
) -> list[OutreachDraft]:
    llm = personalize_json(
        (
            'You are a concise job-search outreach assistant. Return only valid JSON with key drafts as an array. '
            'Create one LinkedIn message and one email draft when possible. Each draft must include channel, targetPersona, '
            'contactHint, subject, and message. Use the specific resume evidence, job description, company, role, remote, and visa signals. '
            'Do not write generic templates and do not invent relationships, referrals, or experience.'
        ),
        {
            'candidateName': candidate_name,
            'candidateHeadline': candidate_headline,
            'resume': resume_text[:5000],
            'job': to_jsonable(job),
            'evaluation': to_jsonable(evaluation),
        },
    )
    if llm is not None:
        drafts = _drafts_from_llm(llm, job)
        if not drafts:
            raise ValueError('LLM returned no usable outreach drafts.')
        return drafts

    top_skills = ', '.join(evaluation.matched_skills[:3]) or 'relevant product engineering experience'
    gap_context = ', '.join(evaluation.missing_skills[:2]) or 'no major gaps from the available JD'
    visa_context = next((note for note in evaluation.signal_notes if 'Visa' in note), 'Visa sponsorship not stated.')
    remote_context = next((note for note in evaluation.signal_notes if 'Remote' in note), 'Remote status not stated.')
    contact_hint = _contact_hint(job.company, job.title)
    why_this_role = f'{job.title} at {job.company} stands out because the JD emphasizes {job.description[:150]}'
    return [
        OutreachDraft(
            id=f'outreach:{job.id}:linkedin', job_id=job.id, channel='linkedin', target_persona='Recruiter or hiring manager', contact_hint=contact_hint,
            message=(
                f'Hi, I found the {job.title} opening at {job.company}. I am {candidate_name}, {candidate_headline}, '
                f'with direct overlap in {top_skills}. {remote_context} {visa_context} I noticed the role focuses on {job.description[:110]}... '
                f'Could you point me to the best person to discuss fit and sponsorship/relocation details?'
            ),
        ),
        OutreachDraft(
            id=f'outreach:{job.id}:email', job_id=job.id, channel='email', target_persona='Recruiting team', contact_hint=contact_hint,
            subject=f'{candidate_name} - {job.title} fit for {job.company}',
            message=(
                f'Hello {job.company} team,\n\n'
                f'I am {candidate_name}, {candidate_headline}. {why_this_role}.\n\n'
                f'My strongest overlap is {top_skills}. I would be transparent that {gap_context} may need discussion, but the core role looks aligned with my background. '
                f'{remote_context} {visa_context}\n\n'
                f'I would appreciate guidance on the best application path or the right person to contact for this opening.\n\nBest,\n{candidate_name}'
            ),
        ),
    ]


def infer_candidate_context(resume_text: str) -> tuple[str, str]:
    lines = [line.strip(' -\t') for line in resume_text.splitlines() if line.strip(' -\t')]
    if not lines:
        return 'Candidate', 'software engineer'

    name = next((line for line in lines[:4] if _looks_like_name(line)), 'Candidate')
    try:
        name_index = lines.index(name)
    except ValueError:
        name_index = -1
    headline = next((line for line in lines[name_index + 1:name_index + 5] if _looks_like_headline(line)), 'software engineer')
    return name, headline


def _drafts_from_llm(llm: dict[str, Any], job: JobPosting) -> list[OutreachDraft]:
    raw_drafts = llm.get('drafts')
    if isinstance(raw_drafts, dict):
        raw_drafts = [raw_drafts]
    if not isinstance(raw_drafts, list):
        return []

    drafts: list[OutreachDraft] = []
    for index, item in enumerate(raw_drafts):
        if not isinstance(item, dict):
            continue
        message = _text_value(item.get('message'))
        if not message:
            continue
        channel = item.get('channel') if item.get('channel') in {'linkedin', 'email', 'text'} else 'linkedin'
        drafts.append(OutreachDraft(
            id=f'outreach:{job.id}:{channel}:{index}',
            job_id=job.id,
            channel=channel,
            target_persona=_text_value(item.get('targetPersona') or item.get('target_persona')) or 'Recruiter or hiring manager',
            contact_hint=_text_value(item.get('contactHint') or item.get('contact_hint')) or _contact_hint(job.company, job.title),
            subject=_text_value(item.get('subject')) or None,
            message=message,
        ))
    return drafts


def _looks_like_name(line: str) -> bool:
    if any(token in line.lower() for token in {'engineer', 'developer', 'manager', 'resume', 'cv', '@', 'http'}):
        return False
    words = line.split()
    return 1 < len(words) <= 4 and all(re.match(r"^[A-Za-z][A-Za-z'.-]*$", word) for word in words)


def _looks_like_headline(line: str) -> bool:
    lower = line.lower()
    return any(token in lower for token in {'engineer', 'developer', 'architect', 'manager', 'analyst', 'scientist', 'designer', 'consultant'})


def _text_value(value: Any) -> str:
    if value is None or isinstance(value, (dict, list)):
        return ''
    return str(value).strip()


def _contact_hint(company: str, title: str) -> str:
    query = quote(f'{company} recruiter {title} LinkedIn')
    return f'Use official company careers pages or LinkedIn people search: https://www.linkedin.com/search/results/people/?keywords={query}'
