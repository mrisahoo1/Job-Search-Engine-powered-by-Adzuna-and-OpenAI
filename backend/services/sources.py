from __future__ import annotations

import html
import json
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from backend.services.models import JobPosting, SearchPreference, SourceStatus
from backend.services.regions import normalize_region
from backend.services.signals import detect_country, detect_remote_signal, detect_visa_signal

SourceFetcher = Callable[[SearchPreference], 'SourceResult']

ADZUNA_DEFAULT_RESULTS_PER_PAGE = 50
ADZUNA_DEFAULT_MAX_RESULTS = 500


class SourceResult:
    def __init__(self, source_id: str, jobs: list[JobPosting], status: SourceStatus):
        self.source_id = source_id
        self.jobs = jobs
        self.status = status


@dataclass(slots=True)
class OfficialCompanySource:
    source_id: str
    name: str
    kind: str
    url: str
    board_token: str | None = None


OFFICIAL_COMPANIES: dict[str, OfficialCompanySource] = {
    'bmw': OfficialCompanySource('official:bmw', 'BMW Careers', 'career_hint', 'https://www.bmwgroup.jobs/'),
    'example-greenhouse': OfficialCompanySource('official:example-greenhouse', 'Greenhouse Example Board', 'greenhouse', 'https://boards-api.greenhouse.io/v1/boards/vaulttec/jobs?content=true', 'vaulttec'),
    'stripe': OfficialCompanySource('official:stripe', 'Stripe Careers', 'greenhouse', 'https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true', 'stripe'),
}


def live_sources() -> list[SourceFetcher]:
    return [fetch_arbeitnow, fetch_remotive, fetch_official_companies, seeded_source]


def adzuna_sources() -> list[SourceFetcher]:
    return [fetch_adzuna]


def build_adzuna_url(
    preferences: SearchPreference,
    app_id: str,
    app_key: str,
    page: int = 1,
    results_per_page: int = ADZUNA_DEFAULT_RESULTS_PER_PAGE,
) -> str:
    country_code = _adzuna_country(preferences.region)
    params = urllib.parse.urlencode({
        'app_id': app_id,
        'app_key': app_key,
        'what': preferences.query,
        'results_per_page': results_per_page,
        'content-type': 'application/json',
    })
    return f'https://api.adzuna.com/v1/api/jobs/{country_code}/search/{page}?{params}'


def official_company_sources(company_ids: list[str]) -> list[OfficialCompanySource]:
    return [OFFICIAL_COMPANIES[item] for item in company_ids if item in OFFICIAL_COMPANIES]


def fetch_arbeitnow(preferences: SearchPreference) -> SourceResult:
    if preferences.region not in {'eu_uk', 'remote_global'}:
        return SourceResult('arbeitnow', [], SourceStatus('arbeitnow', 'disabled', 'Arbeitnow is Europe-focused and skipped for this region.'))
    params = {}
    if preferences.query:
        params['search'] = preferences.query
    if preferences.visa_sponsorship == 'required':
        params['visa_sponsorship'] = 'true'
    url = 'https://www.arbeitnow.com/api/job-board-api'
    if params:
        url += '?' + urllib.parse.urlencode(params)
    payload = _read_json(url)
    items = payload.get('data', []) if isinstance(payload, dict) else payload if isinstance(payload, list) else []
    fetched_at = _now()
    jobs = [job for index, item in enumerate(items) if (job := normalize_arbeitnow_job(item, index, fetched_at))]
    return SourceResult('arbeitnow', jobs, SourceStatus('arbeitnow', 'available', f'{len(jobs)} jobs returned'))


def fetch_remotive(preferences: SearchPreference) -> SourceResult:
    params = {}
    if preferences.query:
        params['search'] = preferences.query
    url = 'https://remotive.com/api/remote-jobs'
    if params:
        url += '?' + urllib.parse.urlencode(params)
    payload = _read_json(url)
    items = payload.get('jobs', []) if isinstance(payload, dict) else []
    fetched_at = _now()
    jobs = [job for index, item in enumerate(items) if (job := normalize_remotive_job(item, index, fetched_at))]
    return SourceResult('remotive', jobs, SourceStatus('remotive', 'available', f'{len(jobs)} remote jobs returned'))


def fetch_adzuna(preferences: SearchPreference) -> SourceResult:
    app_id = os.getenv('ADZUNA_APP_ID')
    app_key = os.getenv('ADZUNA_APP_KEY')
    if not app_id or not app_key:
        return SourceResult('adzuna', [], SourceStatus('adzuna', 'disabled', 'Adzuna credentials not configured.'))

    results_per_page = _env_int('ADZUNA_RESULTS_PER_PAGE', ADZUNA_DEFAULT_RESULTS_PER_PAGE, minimum=1, maximum=50)
    max_results = _env_int('ADZUNA_MAX_RESULTS', ADZUNA_DEFAULT_MAX_RESULTS, minimum=0, maximum=5000)
    fetched_at = _now()
    jobs: list[JobPosting] = []
    total_count = 0
    page = 1
    pages_fetched = 0

    while max_results == 0 or len(jobs) < max_results:
        try:
            payload = _read_json(build_adzuna_url(preferences, app_id, app_key, page=page, results_per_page=results_per_page))
        except Exception as exc:
            if jobs:
                total_label = total_count if total_count else len(jobs)
                return SourceResult(
                    'adzuna',
                    jobs,
                    SourceStatus('adzuna', 'degraded', f'{len(jobs)} of {total_label} jobs returned before page {page} failed: {exc}'),
                )
            raise

        pages_fetched += 1
        if page == 1:
            total_count = _int_value(payload.get('count'))
        items = payload.get('results', []) if isinstance(payload, dict) else []
        if not items:
            break

        remaining = len(items) if max_results == 0 else max_results - len(jobs)
        for item in items[:remaining]:
            job = normalize_adzuna_job(item, len(jobs), fetched_at)
            if job:
                jobs.append(job)

        if max_results and len(jobs) >= max_results:
            break
        if len(items) < results_per_page:
            break
        if total_count and page * results_per_page >= total_count:
            break
        page += 1

    total_label = total_count if total_count else len(jobs)
    if total_label > len(jobs):
        message = f'{len(jobs)} of {total_label} jobs returned across {pages_fetched} pages. Set ADZUNA_MAX_RESULTS higher to fetch more.'
    else:
        message = f'{len(jobs)} of {total_label} jobs returned across {pages_fetched} pages.'
    return SourceResult('adzuna', jobs, SourceStatus('adzuna', 'available', message))


def fetch_official_companies(preferences: SearchPreference) -> SourceResult:
    selected = official_company_sources(preferences.official_companies)
    fetched_at = _now()
    jobs: list[JobPosting] = []
    statuses: list[str] = []
    for source in selected:
        if source.kind == 'greenhouse':
            try:
                payload = _read_json(source.url)
                items = payload.get('jobs', []) if isinstance(payload, dict) else []
                jobs.extend([job for index, item in enumerate(items) if (job := normalize_greenhouse_job(source, item, index, fetched_at))])
                statuses.append(f'{source.name}: queried')
            except Exception as exc:
                statuses.append(f'{source.name}: degraded ({exc})')
        else:
            jobs.extend(_official_hint_jobs(source, preferences, fetched_at))
            statuses.append(f'{source.name}: official careers link added')
    return SourceResult('official', jobs, SourceStatus('official', 'available', '; '.join(statuses) if statuses else 'No official company sources selected'))


def seeded_source(preferences: SearchPreference) -> SourceResult:
    fetched_at = _now()
    return SourceResult('seeded', _seeded_jobs(preferences, fetched_at), SourceStatus('seeded', 'available', 'Query-sensitive fallback examples available'))


def normalize_arbeitnow_job(item: dict[str, Any], index: int, fetched_at: str) -> JobPosting | None:
    title = _string(item.get('title'))
    company = _string(item.get('company_name') or item.get('company'))
    location = _string(item.get('location'))
    raw_url = _string(item.get('url') or item.get('apply_url') or item.get('slug'))
    if not title or not company or not raw_url:
        return None
    description = _strip_html(_string(item.get('description')))
    apply_url = raw_url if raw_url.startswith('http') else f'https://www.arbeitnow.com/jobs/{raw_url}'
    location_text = f'{location} {description}'
    return JobPosting(
        id=f"arbeitnow:{_string(item.get('slug') or item.get('id')) or index}", source_id='arbeitnow', source_name='Arbeitnow', title=title, company=company,
        location=location, country=detect_country(location_text), remote=_signal_from_value(item.get('remote')) or detect_remote_signal(location_text),
        visa_sponsorship=_signal_from_value(item.get('visa_sponsorship')) or detect_visa_signal(description), description=description,
        tags=_array(item.get('tags') or item.get('job_types') or item.get('skills')), posted_at=_string(item.get('created_at') or item.get('date')) or None,
        apply_url=apply_url, fetched_at=fetched_at,
    )


def normalize_remotive_job(item: dict[str, Any], index: int, fetched_at: str) -> JobPosting | None:
    title = _string(item.get('title'))
    company = _string(item.get('company_name') or item.get('company'))
    location = _string(item.get('candidate_required_location') or item.get('location') or 'Remote')
    apply_url = _string(item.get('url'))
    if not title or not company or not apply_url:
        return None
    description = _strip_html(_string(item.get('description')))
    tags = _array(item.get('tags') or item.get('category'))
    return JobPosting(
        id=f"remotive:{_string(item.get('id')) or index}", source_id='remotive', source_name='Remotive', title=title, company=company,
        location=location, country=detect_country(location), remote='yes', visa_sponsorship=detect_visa_signal(description + ' ' + ' '.join(tags)),
        description=description, tags=tags, posted_at=_string(item.get('publication_date')) or None, apply_url=apply_url, fetched_at=fetched_at,
    )


def normalize_adzuna_job(item: dict[str, Any], index: int, fetched_at: str) -> JobPosting | None:
    title = _string(item.get('title'))
    company = _string((item.get('company') or {}).get('display_name') if isinstance(item.get('company'), dict) else item.get('company'))
    apply_url = _string(item.get('redirect_url'))
    if not title or not company or not apply_url:
        return None
    location, country_text = _adzuna_location(item.get('location'))
    description = _strip_html(_string(item.get('description')))
    signal_text = f'{country_text} {description}'
    return JobPosting(
        id=f"adzuna:{_string(item.get('id')) or index}", source_id='adzuna', source_name='Adzuna', title=title, company=company,
        location=location, country=detect_country(country_text), remote=detect_remote_signal(signal_text), visa_sponsorship=detect_visa_signal(description),
        description=description, tags=[], posted_at=_string(item.get('created')) or None, apply_url=apply_url, fetched_at=fetched_at,
    )


def _adzuna_location(value: Any) -> tuple[str, str]:
    if isinstance(value, dict):
        display = _string(value.get('display_name'))
        area = ' '.join(_array(value.get('area')))
        return display, f'{display} {area}'.strip()
    location = _string(value)
    return location, location


def normalize_greenhouse_job(source: OfficialCompanySource, item: dict[str, Any], index: int, fetched_at: str) -> JobPosting | None:
    title = _string(item.get('title'))
    apply_url = _string(item.get('absolute_url'))
    if not title or not apply_url:
        return None
    location = _string((item.get('location') or {}).get('name') if isinstance(item.get('location'), dict) else item.get('location'))
    description = _strip_html(_string(item.get('content')))
    return JobPosting(
        id=f'{source.source_id}:{_string(item.get("id")) or index}', source_id=source.source_id, source_name=source.name,
        title=title, company=source.name.replace(' Careers', '').replace('Greenhouse Example Board', 'Greenhouse Example'), location=location,
        country=detect_country(location), remote=detect_remote_signal(f'{location} {description}'), visa_sponsorship=detect_visa_signal(description),
        description=description or f'Official {source.name} posting. Open the apply link for the complete job description.', tags=[],
        posted_at=_string(item.get('updated_at')) or None, apply_url=apply_url, fetched_at=fetched_at,
    )


def _official_hint_jobs(source: OfficialCompanySource, preferences: SearchPreference, fetched_at: str) -> list[JobPosting]:
    query = urllib.parse.quote(preferences.query)
    return [JobPosting(
        id=f'{source.source_id}:careers-search', source_id=source.source_id, source_name=source.name,
        title=f'{preferences.query.title()} roles at {source.name.replace(" Careers", "")}', company=source.name.replace(' Careers', ''),
        location=', '.join(preferences.countries) or 'Global / Remote', country=preferences.countries[0] if preferences.countries else '', remote='unknown', visa_sponsorship='unknown',
        description=f'Official company careers source. Open the link and search for "{preferences.query}". This is included as a compliant official-site source when no public API is available.',
        tags=['official careers', preferences.query], posted_at=None, apply_url=f'{source.url}?q={query}', fetched_at=fetched_at,
    )]


def _seeded_jobs(preferences: SearchPreference, fetched_at: str) -> list[JobPosting]:
    region = normalize_region({'region': preferences.region})
    query = preferences.query.lower()
    if 'product' in query:
        title = 'Product Manager, AI Hiring Workflows'
        tags = ['Product Analytics', 'APIs', 'Stakeholder Communication']
        description = 'Product strategy, analytics, stakeholder communication, experimentation, and AI workflow delivery.'
    elif 'backend' in query:
        title = 'Backend Engineer, Job Platform'
        tags = ['Node.js', 'APIs', 'PostgreSQL', 'Testing']
        description = 'Backend APIs, PostgreSQL, distributed systems, testing, and deployment ownership.'
    else:
        title = 'Senior Full Stack Engineer'
        tags = ['TypeScript', 'React', 'Node.js', 'PostgreSQL']
        description = 'TypeScript, React, Node.js, APIs, PostgreSQL, accessibility, testing, and product-minded engineering.'
    country = region.countries[0] if region.countries else 'Remote'
    location = f'{country} / Remote' if country else 'Remote / Global'
    return [JobPosting(
        id=f'seeded:{preferences.region}:{re.sub(r"[^a-z0-9]+", "-", query).strip("-") or "job"}', source_id='seeded', source_name='Seeded Query Examples',
        title=title, company='Northstar Labs' if preferences.region == 'eu_uk' else 'Atlas Careers', location=location, country=country if country != 'Remote' else '',
        remote='yes', visa_sponsorship='yes' if preferences.region in {'eu_uk', 'remote_global'} else 'unknown',
        description=f'{description} Region focus: {region.label}. Visa and relocation support depends on role.', tags=tags,
        posted_at=fetched_at, apply_url=f'https://www.google.com/search?q={urllib.parse.quote(preferences.query + " " + region.label + " jobs official careers")}', fetched_at=fetched_at,
    )]


def _adzuna_country(region: str) -> str:
    return {'india': 'in', 'us': 'us', 'australia': 'au', 'eu_uk': 'gb', 'remote_global': 'gb'}.get(region, 'gb')


def _read_json(url: str) -> Any:
    request = urllib.request.Request(url, headers={'User-Agent': 'job-search-curation-agent/0.2'})
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.loads(response.read().decode('utf-8'))


def _strip_html(value: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]*>', ' ', html.unescape(value))).strip()


def _string(value: Any) -> str:
    return str(value).strip() if isinstance(value, (str, int, float, bool)) else ''


def _array(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_string(item) for item in value if _string(item)]
    string_value = _string(value)
    return [string_value] if string_value else []


def _signal_from_value(value: Any):
    if isinstance(value, bool):
        return 'yes' if value else 'no'
    string_value = _string(value).lower()
    if string_value in {'true', 'yes', 'remote'}:
        return 'yes'
    if string_value in {'false', 'no'}:
        return 'no'
    return None


def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(value, maximum))


def _int_value(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
