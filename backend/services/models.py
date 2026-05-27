from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

Signal = Literal['yes', 'no', 'unknown']
Confidence = Literal['high', 'medium', 'low']
Recommendation = Literal['strong-fit', 'possible-fit', 'stretch', 'low-fit']
VisaPreference = Literal['required', 'preferred', 'any']
ProspectStatus = Literal['new', 'reviewing', 'tailored', 'outreach-drafted', 'applied', 'interviewing', 'rejected', 'archived']


@dataclass(slots=True)
class CandidateProfile:
    resume_text: str
    extracted_skills: list[str]
    experience_signals: list[str]
    target_titles: list[str]
    preferred_countries: list[str]
    remote_preference: Literal['remote', 'hybrid', 'onsite', 'any']
    visa_preference: VisaPreference
    confidence: Confidence


@dataclass(slots=True)
class SearchPreference:
    query: str = 'software engineer'
    region: str = 'eu_uk'
    countries: list[str] = field(default_factory=lambda: ['Germany', 'Netherlands', 'Ireland', 'France', 'Spain', 'United Kingdom'])
    remote_only: bool = False
    visa_sponsorship: VisaPreference = 'preferred'
    sources: list[str] = field(default_factory=lambda: ['deep', 'official'])
    official_companies: list[str] = field(default_factory=lambda: ['bmw', 'example-greenhouse'])
    search_mode: str = 'live'


@dataclass(slots=True)
class JobPosting:
    id: str
    source_id: str
    source_name: str
    title: str
    company: str
    location: str
    country: str
    remote: Signal
    visa_sponsorship: Signal
    description: str
    tags: list[str]
    apply_url: str
    fetched_at: str
    posted_at: str | None = None


@dataclass(slots=True)
class FitEvaluation:
    job_id: str
    score: int
    confidence: Confidence
    recommendation: Recommendation
    matched_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    risks: list[str]
    signal_notes: list[str]


@dataclass(slots=True)
class SearchResult:
    job: JobPosting
    evaluation: FitEvaluation


@dataclass(slots=True)
class SourceStatus:
    source_id: str
    status: Literal['available', 'degraded', 'disabled', 'unsupported']
    message: str


@dataclass(slots=True)
class SearchResponse:
    results: list[SearchResult]
    source_statuses: list[SourceStatus]
    fetched_at: str


@dataclass(slots=True)
class ResumeDraft:
    id: str
    job_id: str
    base_resume_text: str
    draft_text: str
    change_summary: list[str]
    warnings: list[str]
    created_at: str


@dataclass(slots=True)
class OutreachDraft:
    id: str
    job_id: str
    channel: Literal['linkedin', 'email', 'text']
    target_persona: str
    contact_hint: str
    message: str
    review_status: Literal['draft', 'copied', 'approved', 'rejected'] = 'draft'
    subject: str | None = None


def to_camel(value: str) -> str:
    parts = value.split('_')
    return parts[0] + ''.join(part.title() for part in parts[1:])


def to_jsonable(value):
    if hasattr(value, '__dataclass_fields__'):
        return {to_camel(key): to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {to_camel(str(key)): to_jsonable(item) for key, item in value.items()}
    return value
