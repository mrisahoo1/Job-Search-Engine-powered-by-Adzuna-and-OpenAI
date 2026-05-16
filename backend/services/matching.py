from __future__ import annotations

from backend.services.models import CandidateProfile, FitEvaluation, JobPosting, Recommendation, SearchPreference
from backend.services.resume import extract_known_skills


def evaluate_job_match(profile: CandidateProfile, job: JobPosting, preferences: SearchPreference) -> FitEvaluation:
    job_tags = ' '.join(job.tags)
    job_text = f'{job.title} {job.description} {job_tags}'
    job_skills = extract_known_skills(job_text)
    matched = [skill for skill in job_skills if skill in profile.extracted_skills]
    missing = [skill for skill in job_skills if skill not in profile.extracted_skills]

    score = 20
    score += min(40, len(matched) * 10)
    score += int(_title_overlap(profile, job) * 15)
    score += _remote_score(job, preferences)
    score += _visa_score(job, preferences)
    score += _seniority_score(profile, job)
    score -= min(18, len(missing) * 4)
    score = max(0, min(100, round(score)))

    return FitEvaluation(
        job_id=job.id,
        score=score,
        confidence=_confidence_for(profile, job, len(matched)),
        recommendation=_recommendation_for(score),
        matched_skills=matched,
        missing_skills=missing,
        strengths=_strengths(matched, job, preferences),
        risks=_risks(missing, job, profile, preferences),
        signal_notes=[_signal_note('Remote', job.remote), _signal_note('Visa sponsorship', job.visa_sponsorship)],
    )


def _title_overlap(profile: CandidateProfile, job: JobPosting) -> float:
    title = job.title.lower()
    if any(target.lower() in title for target in profile.target_titles):
        return 1.0
    if any(word in title for word in ['full stack', 'software', 'backend', 'frontend']) and any(word in profile.resume_text.lower() for word in ['full stack', 'software', 'backend', 'frontend']):
        return 0.7
    return 0.0


def _remote_score(job: JobPosting, preferences: SearchPreference) -> int:
    if preferences.remote_only and job.remote != 'yes':
        return -12
    if job.remote == 'yes':
        return 8
    if job.remote == 'unknown':
        return 0
    return -4


def _visa_score(job: JobPosting, preferences: SearchPreference) -> int:
    if preferences.visa_sponsorship == 'required':
        return 12 if job.visa_sponsorship == 'yes' else -20
    if preferences.visa_sponsorship == 'preferred':
        if job.visa_sponsorship == 'yes':
            return 10
        if job.visa_sponsorship == 'no':
            return -10
    return 0


def _seniority_score(profile: CandidateProfile, job: JobPosting) -> int:
    resume_senior = 'senior' in profile.resume_text.lower() or 'lead' in profile.resume_text.lower()
    job_senior = 'senior' in job.title.lower() or 'lead' in job.title.lower()
    if resume_senior and job_senior:
        return 8
    if not job_senior:
        return 4
    return -4


def _confidence_for(profile: CandidateProfile, job: JobPosting, matches: int):
    if profile.confidence == 'low' or len(job.description) < 80:
        return 'low'
    if matches >= 3 and profile.confidence == 'high':
        return 'high'
    return 'medium'


def _recommendation_for(score: int) -> Recommendation:
    if score >= 75:
        return 'strong-fit'
    if score >= 55:
        return 'possible-fit'
    if score >= 35:
        return 'stretch'
    return 'low-fit'


def _strengths(matched: list[str], job: JobPosting, preferences: SearchPreference) -> list[str]:
    strengths: list[str] = []
    if matched:
        strengths.append(f"Matched skills: {', '.join(matched[:5])}.")
    if job.remote == 'yes':
        strengths.append('Remote signal found for the role.')
    if preferences.visa_sponsorship != 'any' and job.visa_sponsorship == 'yes':
        strengths.append('Visa sponsorship or relocation support is explicitly signaled.')
    if 'senior' in job.title.lower() or 'lead' in job.title.lower():
        strengths.append('Seniority appears aligned with experienced candidate positioning.')
    return strengths or ['Some overlap found, but evidence is limited.']


def _risks(missing: list[str], job: JobPosting, profile: CandidateProfile, preferences: SearchPreference) -> list[str]:
    risks: list[str] = []
    if missing:
        risks.append(f"Missing or weak evidence: {', '.join(missing[:5])}.")
    if preferences.visa_sponsorship != 'any' and job.visa_sponsorship != 'yes':
        risks.append('Role states sponsorship is unavailable.' if job.visa_sponsorship == 'no' else 'Visa sponsorship is not stated.')
    if preferences.remote_only and job.remote != 'yes':
        risks.append('Remote requirement is not clearly satisfied.')
    if profile.confidence == 'low':
        risks.append('Resume is sparse, so fit confidence is low.')
    return risks or ['No major gaps detected from available job text.']


def _signal_note(label: str, signal: str) -> str:
    if signal == 'yes':
        return f'{label} signal found.'
    if signal == 'no':
        return f'{label} appears unavailable.'
    return f'{label} not stated.'
