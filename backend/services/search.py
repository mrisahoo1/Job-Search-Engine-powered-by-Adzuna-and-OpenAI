from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable
import re

from backend.services.matching import evaluate_job_match
from backend.services.models import JobPosting, SearchPreference, SearchResponse, SearchResult, SourceStatus
from backend.services.regions import normalize_region
from backend.services.resume import extract_resume_profile
from backend.services.sources import SourceFetcher, SourceResult, adzuna_sources, live_sources


def search_jobs(resume_text: str, preferences: SearchPreference, sources: Iterable[SourceFetcher] | None = None) -> SearchResponse:
    profile = extract_resume_profile(resume_text)
    if not profile.resume_text or (profile.confidence == 'low' and not profile.extracted_skills):
        raise ValueError('Add more resume detail before running a match search.')

    region = normalize_region({'region': preferences.region})
    if not preferences.countries and region.countries:
        preferences.countries = region.countries

    source_pool = list(sources) if sources is not None else (adzuna_sources() if preferences.search_mode == 'adzuna' else live_sources())
    selected_sources = [source for source in source_pool if _source_enabled(source, preferences)]
    jobs: list[JobPosting] = []
    statuses: list[SourceStatus] = []
    for index, source in enumerate(selected_sources, start=1):
        try:
            result: SourceResult = source(preferences)
            jobs.extend(result.jobs)
            statuses.append(result.status)
        except Exception as exc:
            statuses.append(SourceStatus(f'source-{index}', 'degraded', str(exc) or 'Source failed'))

    filtered = _filter_jobs(_dedupe_jobs(jobs), preferences)
    results = [SearchResult(job, evaluate_job_match(profile, job, preferences)) for job in filtered]
    results.sort(key=lambda result: (_query_relevance(result.job, preferences), result.evaluation.score), reverse=True)
    return SearchResponse(results=results, source_statuses=statuses, fetched_at=datetime.now(timezone.utc).isoformat())


def _source_enabled(source: SourceFetcher, preferences: SearchPreference) -> bool:
    name = getattr(source, '__name__', '')
    if not preferences.sources:
        return True
    if name.startswith('fetch_arbeitnow'):
        return 'arbeitnow' in preferences.sources
    if name.startswith('fetch_remotive'):
        return 'remotive' in preferences.sources
    if name.startswith('fetch_adzuna'):
        return 'adzuna' in preferences.sources
    if name.startswith('fetch_official'):
        return 'official' in preferences.sources
    if name.startswith('seeded'):
        return 'seeded' in preferences.sources
    return True


def _dedupe_jobs(jobs: list[JobPosting]) -> list[JobPosting]:
    seen: dict[str, JobPosting] = {}
    for job in jobs:
        seen.setdefault(_dedupe_key(job), job)
    return list(seen.values())


def _dedupe_key(job: JobPosting) -> str:
    semantic_key = '|'.join(_normalize_key(part) for part in (job.title, job.company, job.location))
    if semantic_key.count('|') == 2 and semantic_key.replace('|', ''):
        return semantic_key
    return _normalize_key(job.apply_url.split('?', 1)[0]) or _normalize_key(job.id)


def _filter_jobs(jobs: list[JobPosting], preferences: SearchPreference) -> list[JobPosting]:
    filtered: list[JobPosting] = []
    for job in jobs:
        if preferences.remote_only and job.remote != 'yes':
            continue
        if preferences.visa_sponsorship == 'required' and job.visa_sponsorship != 'yes':
            continue
        if preferences.countries and job.country and job.country not in preferences.countries and preferences.region != 'remote_global':
            continue
        filtered.append(job)
    return filtered


def _query_relevance(job: JobPosting, preferences: SearchPreference) -> int:
    terms = [term.lower() for term in preferences.query.split() if len(term) > 2]
    tags = ' '.join(job.tags)
    haystack = f'{job.title} {job.description} {tags}'.lower()
    return sum(1 for term in terms if term in haystack)


def _normalize_key(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', value.lower()).strip()
