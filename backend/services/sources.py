from __future__ import annotations

import hashlib
import html
import json
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any, Callable

from backend.services.models import JobPosting, SearchPreference, SourceStatus
from backend.services.regions import normalize_region
from backend.services.signals import detect_country, detect_remote_signal, detect_visa_signal

SourceFetcher = Callable[[SearchPreference], 'SourceResult']

ADZUNA_DEFAULT_RESULTS_PER_PAGE = 50
ADZUNA_DEFAULT_MAX_RESULTS = 500
DEEP_DEFAULT_MAX_RESULTS = 60
DEEP_DEFAULT_CRAWL_PAGES = 12
DEEP_DEFAULT_QUERY_COUNT = 6
MAX_PAGE_BYTES = 700000
PROTECTED_JOB_DOMAINS = ('linkedin.com', 'www.linkedin.com', 'naukri.com', 'www.naukri.com', 'instahyre.com', 'www.instahyre.com')
QUERY_STOP_WORDS = {'and', 'the', 'for', 'with', 'job', 'jobs', 'role', 'roles', 'remote', 'hybrid', 'onsite', 'senior', 'lead', 'staff', 'engineer', 'developer', 'manager', 'software', 'full', 'stack', 'india', 'europe', 'uk', 'us'}
ROLE_FAMILY_TITLE_TERMS = {'engineer', 'engineering', 'developer', 'architect', 'architekt', 'devops', 'software', 'full-stack', 'fullstack', 'platform', 'sre'}


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


@dataclass(slots=True)
class DiscoveredJobLink:
    url: str
    title: str
    description: str
    source_id: str
    source_name: str
    link_only: bool = False


OFFICIAL_COMPANIES: dict[str, OfficialCompanySource] = {
    'bmw': OfficialCompanySource('official:bmw', 'BMW Careers', 'career_hint', 'https://www.bmwgroup.jobs/'),
    'example-greenhouse': OfficialCompanySource('official:example-greenhouse', 'Greenhouse Example Board', 'greenhouse', 'https://boards-api.greenhouse.io/v1/boards/vaulttec/jobs?content=true', 'vaulttec'),
    'stripe': OfficialCompanySource('official:stripe', 'Stripe Careers', 'greenhouse', 'https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true', 'stripe'),
}


def live_sources() -> list[SourceFetcher]:
    return [fetch_deep_live, fetch_arbeitnow, fetch_remotive, fetch_official_companies, seeded_source]


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


def fetch_deep_live(preferences: SearchPreference) -> SourceResult:
    fetched_at = _now()
    max_results = _env_int('DEEP_SEARCH_MAX_RESULTS', DEEP_DEFAULT_MAX_RESULTS, minimum=5, maximum=200)
    crawl_limit = _env_int('DEEP_CRAWL_MAX_PAGES', DEEP_DEFAULT_CRAWL_PAGES, minimum=0, maximum=40)
    jobs: list[JobPosting] = []
    messages: list[str] = []
    status = 'available'

    feed_jobs, feed_messages = _fetch_deep_public_feeds(preferences, fetched_at)
    jobs.extend(feed_jobs)
    messages.extend(feed_messages)

    discovered, discovery_messages = _discover_deep_links(preferences)
    messages.extend(discovery_messages)

    crawled = 0
    protected = 0
    snippet_jobs = 0
    for link in discovered:
        if len(jobs) >= max_results:
            break
        if link.link_only or is_protected_job_domain(link.url):
            protected += 1
            snippet = _job_from_discovered_link(link, preferences, fetched_at)
            if snippet and _job_matches_query(snippet, preferences):
                jobs.append(snippet)
                snippet_jobs += 1
            continue
        if crawled >= crawl_limit:
            continue
        try:
            page = _read_text(link.url)
        except Exception:
            status = 'degraded'
            continue
        crawled += 1
        job = _extract_job_from_html(link.url, page, link.source_id, link.source_name, fetched_at, fallback=link)
        if job and _job_matches_query(job, preferences):
            jobs.append(job)

    jobs = _dedupe_deep_jobs(jobs)[:max_results]
    if protected:
        messages.append(f'{protected} Tavily/search links used as snippet-only results')
    if crawled:
        messages.append(f'{crawled} public pages crawled')
    if snippet_jobs:
        messages.append(f'{snippet_jobs} snippet-only links added')
    if not jobs and status == 'available':
        status = 'degraded'
    return SourceResult('deep', jobs, SourceStatus('deep', status, '; '.join(messages) if messages else 'Deep search found no public results.'))


def normalize_remoteok_job(item: dict[str, Any], index: int, fetched_at: str) -> JobPosting | None:
    title = _string(item.get('position') or item.get('title'))
    company = _string(item.get('company'))
    raw_url = _string(item.get('url') or item.get('apply_url'))
    if not title or not company:
        return None
    if not raw_url:
        raw_url = f"https://remoteok.com/remote-jobs/{_string(item.get('id'))}"
    description = _strip_html(_string(item.get('description') or item.get('summary')))
    location = _string(item.get('location') or 'Remote')
    tags = _array(item.get('tags'))
    return JobPosting(
        id=f"remoteok:{_string(item.get('id')) or index}", source_id='remoteok', source_name='RemoteOK', title=title, company=company,
        location=location, country=detect_country(location), remote='yes', visa_sponsorship=detect_visa_signal(description + ' ' + ' '.join(tags)),
        description=description, tags=tags, posted_at=_string(item.get('date') or item.get('epoch')) or None,
        apply_url=raw_url, fetched_at=fetched_at,
    )


def _fetch_deep_public_feeds(preferences: SearchPreference, fetched_at: str) -> tuple[list[JobPosting], list[str]]:
    messages: list[str] = []
    jobs: list[JobPosting] = []
    for label, fetcher in [
        ('RemoteOK', _fetch_remoteok_feed),
        ('Remotive', lambda prefs, now: fetch_remotive(prefs).jobs),
        ('Arbeitnow', lambda prefs, now: fetch_arbeitnow(prefs).jobs),
    ]:
        try:
            fetched = fetcher(preferences, fetched_at)
            matched = [job for job in fetched if _job_matches_query(job, preferences)]
            jobs.extend(matched)
            messages.append(f'{label}: {len(matched)} matched from {len(fetched)} public feed jobs')
        except Exception as exc:
            messages.append(f'{label}: degraded ({exc})')
    return jobs, messages


def _fetch_remoteok_feed(preferences: SearchPreference, fetched_at: str) -> list[JobPosting]:
    payload = _read_json('https://remoteok.com/api')
    items = payload if isinstance(payload, list) else []
    return [job for index, item in enumerate(items) if isinstance(item, dict) and (job := normalize_remoteok_job(item, index, fetched_at))]

def _discover_deep_links(preferences: SearchPreference) -> tuple[list[DiscoveredJobLink], list[str]]:
    messages: list[str] = []
    links: list[DiscoveredJobLink] = []
    query_count = _env_int('DEEP_SEARCH_QUERY_COUNT', DEEP_DEFAULT_QUERY_COUNT, minimum=1, maximum=12)
    queries = _deep_discovery_queries(preferences)[:query_count]

    tavily_key = os.getenv('TAVILY_API_KEY')
    if tavily_key:
        try:
            tavily_links = _discover_with_tavily(queries, tavily_key)
            links.extend(tavily_links)
            messages.append(f'Tavily discovery/extraction: {len(tavily_links)} public links discovered')
        except Exception as exc:
            messages.append(f'Tavily discovery degraded ({exc})')
    else:
        messages.append('Tavily discovery disabled: add TAVILY_API_KEY for broader web crawling')

    brave_key = os.getenv('BRAVE_SEARCH_API_KEY')
    if brave_key:
        try:
            brave_links = _discover_with_brave(queries, brave_key)
            links.extend(brave_links)
            messages.append(f'Brave discovery: {len(brave_links)} public links discovered')
        except Exception as exc:
            messages.append(f'Brave discovery degraded ({exc})')
    else:
        messages.append('Brave discovery disabled: add BRAVE_SEARCH_API_KEY for backup web crawling')

    google_key = os.getenv('GOOGLE_API_KEY')
    google_cx = os.getenv('GOOGLE_CSE_ID')
    if google_key and google_cx:
        try:
            google_links = _discover_with_google(queries, google_key, google_cx)
            links.extend(google_links)
            messages.append(f'Google discovery: {len(google_links)} public links discovered')
        except Exception as exc:
            messages.append(f'Google discovery degraded ({exc})')
    else:
        messages.append('Google discovery disabled: add GOOGLE_API_KEY and GOOGLE_CSE_ID for secondary web crawling')

    return _dedupe_links(links), messages


def _deep_discovery_queries(preferences: SearchPreference) -> list[str]:
    region = normalize_region({'region': preferences.region})
    place = ', '.join(preferences.countries[:3]) or region.label or 'remote'
    base = f'"{preferences.query}" {place} jobs'
    remote = ' remote' if preferences.remote_only else ''
    visa = ' visa sponsorship relocation' if preferences.visa_sponsorship in {'required', 'preferred'} else ''
    return [
        f'{base}{remote}{visa} apply',
        f'{base} official careers{remote}{visa}',
        f'site:boards.greenhouse.io {base}{remote}{visa}',
        f'site:jobs.lever.co {base}{remote}{visa}',
        f'site:ashbyhq.com {base}{remote}{visa}',
        f'site:workdayjobs.com {base}{remote}{visa}',
        f'site:wellfound.com/jobs {base}{remote}{visa}',
        f'site:remoteok.com {base}{remote}',
        f'site:linkedin.com/jobs/view {base}',
        f'site:naukri.com {preferences.query} {place}',
        f'site:instahyre.com {preferences.query} {place}',
    ]


def _discover_with_tavily(queries: list[str], api_key: str) -> list[DiscoveredJobLink]:
    links: list[DiscoveredJobLink] = []
    for query in queries:
        payload = {
            'query': query,
            'search_depth': 'basic',
            'topic': 'general',
            'max_results': 10,
            'include_answer': False,
            'include_raw_content': 'text',
            'include_images': False,
        }
        request = urllib.request.Request(
            'https://api.tavily.com/search',
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'job-search-curation-agent/0.3',
            },
            method='POST',
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            result_payload = json.loads(response.read().decode('utf-8'))
        for item in result_payload.get('results', []) if isinstance(result_payload, dict) else []:
            url = _string(item.get('url'))
            if not url:
                continue
            title = _strip_html(_string(item.get('title')))
            content = _strip_html(_string(item.get('raw_content') or item.get('content')))
            if not _is_likely_job_result(url, title, content):
                continue
            links.append(DiscoveredJobLink(
                url=url,
                title=title,
                description=content,
                source_id='tavily',
                source_name='Tavily Search',
                link_only=True,
            ))
    return links


def _discover_with_brave(queries: list[str], api_key: str) -> list[DiscoveredJobLink]:
    links: list[DiscoveredJobLink] = []
    for query in queries:
        params = urllib.parse.urlencode({'q': query, 'count': 10, 'search_lang': 'en'})
        request = urllib.request.Request(
            f'https://api.search.brave.com/res/v1/web/search?{params}',
            headers={'Accept': 'application/json', 'X-Subscription-Token': api_key, 'User-Agent': 'job-search-curation-agent/0.3'},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode('utf-8'))
        results = ((payload.get('web') or {}).get('results') or []) if isinstance(payload, dict) else []
        for item in results:
            url = _string(item.get('url'))
            if url:
                links.append(DiscoveredJobLink(url, _strip_html(_string(item.get('title'))), _strip_html(_string(item.get('description'))), 'brave', 'Brave Search', is_protected_job_domain(url)))
    return links


def _discover_with_google(queries: list[str], api_key: str, cse_id: str) -> list[DiscoveredJobLink]:
    links: list[DiscoveredJobLink] = []
    for query in queries:
        params = urllib.parse.urlencode({'q': query, 'key': api_key, 'cx': cse_id, 'num': 10})
        payload = _read_json(f'https://www.googleapis.com/customsearch/v1?{params}')
        for item in payload.get('items', []) if isinstance(payload, dict) else []:
            url = _string(item.get('link'))
            if url:
                links.append(DiscoveredJobLink(url, _strip_html(_string(item.get('title'))), _strip_html(_string(item.get('snippet'))), 'google-cse', 'Google Programmable Search', is_protected_job_domain(url)))
    return links

def _extract_job_from_html(url: str, page_html: str, source_id: str, source_name: str, fetched_at: str, fallback: DiscoveredJobLink | None = None) -> JobPosting | None:
    if _looks_blocked(page_html):
        return None
    json_job = _extract_json_ld_job(url, page_html, source_id, source_name, fetched_at)
    if json_job:
        return json_job
    parser = _VisibleTextParser()
    parser.feed(page_html[:MAX_PAGE_BYTES])
    title = parser.heading or _page_title(page_html) or (fallback.title if fallback else '')
    text = _clean_visible_text(' '.join(parser.text_parts))
    if len(text) < 80 and fallback:
        text = fallback.description
    if not title or len(text) < 40:
        return None
    company = _company_from_title(title) or _company_from_text(text) or (fallback.source_name if fallback else 'Unknown company')
    location = _location_from_text(text) or 'Not specified'
    signal_text = f'{title} {location} {text}'
    return JobPosting(
        id=f'{source_id}:{_stable_hash(url)}', source_id=source_id, source_name=source_name, title=_strip_title_noise(title), company=company,
        location=location, country=detect_country(signal_text), remote=detect_remote_signal(signal_text), visa_sponsorship=detect_visa_signal(signal_text),
        description=text[:5000], tags=['deep-search', 'public-page'], posted_at=_date_from_text(text), apply_url=url, fetched_at=fetched_at,
    )


def _extract_json_ld_job(url: str, page_html: str, source_id: str, source_name: str, fetched_at: str) -> JobPosting | None:
    for raw in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', page_html, flags=re.I | re.S):
        data = _safe_json_loads(html.unescape(raw.strip()))
        for item in _flatten_json_ld(data):
            if not _is_jobposting(item):
                continue
            title = _string(item.get('title'))
            description = _strip_html(_string(item.get('description')))
            if not title or len(description) < 30:
                continue
            company = _json_name(item.get('hiringOrganization')) or 'Unknown company'
            location = _json_location(item.get('jobLocation')) or _json_name(item.get('applicantLocationRequirements')) or 'Not specified'
            signal_text = f'{title} {company} {location} {description}'
            return JobPosting(
                id=f'{source_id}:{_stable_hash(url)}', source_id=source_id, source_name=source_name, title=title, company=company,
                location=location, country=detect_country(signal_text), remote=detect_remote_signal(signal_text), visa_sponsorship=detect_visa_signal(signal_text),
                description=description[:5000], tags=['deep-search', 'json-ld'], posted_at=_string(item.get('datePosted')) or None,
                apply_url=url, fetched_at=fetched_at,
            )
    return None


def _job_from_discovered_link(link: DiscoveredJobLink, preferences: SearchPreference, fetched_at: str) -> JobPosting | None:
    title = link.title or preferences.query.title()
    description = link.description
    if not title or len(description) < 20:
        return None
    signal_text = f'{title} {description}'
    return JobPosting(
        id=f'{link.source_id}:{_stable_hash(link.url)}', source_id=link.source_id, source_name=link.source_name, title=_strip_title_noise(title), company=_company_from_title(title) or _domain_label(link.url),
        location='Public search result', country=detect_country(signal_text), remote=detect_remote_signal(signal_text), visa_sponsorship=detect_visa_signal(signal_text),
        description=description, tags=['deep-search', 'snippet-only'], posted_at=None, apply_url=link.url, fetched_at=fetched_at,
    )


def is_protected_job_domain(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower().removeprefix('www.')
    return any(host == domain.removeprefix('www.') or host.endswith('.' + domain.removeprefix('www.')) for domain in PROTECTED_JOB_DOMAINS)


def _is_likely_job_result(url: str, title: str, content: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower().removeprefix('www.')
    path = parsed.path.lower()
    combined = f'{title} {content}'.lower()
    blocked_hosts = ('reddit.com', 'facebook.com', 'medium.com', 'youtube.com', 'universaladviser.com', 'zenvanriel.com')
    blocked_paths = ('/pulse/', '/blog/', '/news/', '/article/', '/articles/')
    blocked_title = ('guide', 'requirements update', 'market guide', 'immigrate', 'how to', 'advice')
    if any(host == blocked or host.endswith('.' + blocked) for blocked in blocked_hosts):
        return False
    if any(marker in path for marker in blocked_paths):
        return False
    if any(marker in title.lower() for marker in blocked_title):
        return False
    strong_domains = (
        'boards.greenhouse.io', 'jobs.lever.co', 'ashbyhq.com', 'workdayjobs.com', 'myworkdayjobs.com',
        'arbeitnow.com', 'remotive.com', 'remoteok.com', 'remoterocketship.com', 'wellfound.com',
        'linkedin.com', 'naukri.com', 'instahyre.com', 'indeed.com', 'ziprecruiter.com',
    )
    if any(host == domain or host.endswith('.' + domain) for domain in strong_domains):
        return 'job' in combined or 'apply' in combined or '/jobs' in path or '/job' in path
    if any(marker in path for marker in ['/jobs/', '/job/', '/careers/', '/career/', '/positions/', '/openings/']):
        return True
    return any(marker in title.lower() for marker in ['job application', 'open role', 'open roles'])


def _job_matches_query(job: JobPosting, preferences: SearchPreference) -> bool:
    terms = _query_terms(preferences.query)
    if not terms:
        return True
    raw_terms = [term for term in re.findall(r'[a-z0-9+#.]+', preferences.query.lower()) if len(term) > 1]
    title = job.title.lower()
    tags = ' '.join(job.tags).lower()
    description = job.description.lower()
    haystack = f'{title} {description} {tags}'
    family_requested = any(term in {'engineer', 'developer', 'architect', 'devops', 'sre'} for term in raw_terms)
    family_in_title = any(term in title for term in ROLE_FAMILY_TITLE_TERMS)
    if family_requested and not family_in_title:
        return False
    title_hits = sum(1 for term in terms if term in title or term in tags)
    total_hits = sum(1 for term in terms if term in haystack)
    if len(terms) == 1:
        term = terms[0]
        if term == 'data':
            return term in title or term in tags
        return term in title or term in tags or (family_in_title and description.count(term) >= 2)
    return (title_hits >= 1 and family_in_title) or total_hits >= len(terms)

def _query_terms(query: str) -> list[str]:
    raw_terms = [term for term in re.findall(r'[a-z0-9+#.]+', query.lower()) if len(term) > 1]
    focused = [term for term in raw_terms if term not in QUERY_STOP_WORDS]
    return focused or raw_terms[:3]


def _dedupe_links(links: list[DiscoveredJobLink]) -> list[DiscoveredJobLink]:
    seen: set[str] = set()
    deduped: list[DiscoveredJobLink] = []
    for link in links:
        key = _canonical_url(link.url)
        if key and key not in seen:
            seen.add(key)
            deduped.append(link)
    return deduped


def _dedupe_deep_jobs(jobs: list[JobPosting]) -> list[JobPosting]:
    seen: set[str] = set()
    deduped: list[JobPosting] = []
    for job in jobs:
        key = '|'.join([_normalize_key(job.title), _normalize_key(job.company), _normalize_key(job.location)])
        if not key.replace('|', ''):
            key = _canonical_url(job.apply_url)
        if key not in seen:
            seen.add(key)
            deduped.append(job)
    return deduped


def _read_text(url: str) -> str:
    request = urllib.request.Request(url, headers={'User-Agent': 'job-search-curation-agent/0.3', 'Accept': 'text/html,application/xhtml+xml'})
    with urllib.request.urlopen(request, timeout=10) as response:
        raw = response.read(MAX_PAGE_BYTES)
        charset = response.headers.get_content_charset() or 'utf-8'
        return raw.decode(charset, errors='replace')


def _stable_hash(value: str) -> str:
    return hashlib.sha1(value.encode('utf-8')).hexdigest()[:16]


def _canonical_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip('/'), '', '', ''))


def _normalize_key(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', value.lower()).strip()


def _safe_json_loads(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def _flatten_json_ld(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        graph = value.get('@graph')
        if isinstance(graph, list):
            return [item for item in graph if isinstance(item, dict)] + [value]
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _is_jobposting(item: dict[str, Any]) -> bool:
    kind = item.get('@type')
    if isinstance(kind, list):
        return any(_string(entry).lower() == 'jobposting' for entry in kind)
    return _string(kind).lower() == 'jobposting'


def _json_name(value: Any) -> str:
    if isinstance(value, dict):
        return _string(value.get('name'))
    if isinstance(value, list):
        return ', '.join(filter(None, [_json_name(item) for item in value]))
    return _string(value)


def _json_location(value: Any) -> str:
    if isinstance(value, list):
        return ', '.join(filter(None, [_json_location(item) for item in value]))
    if not isinstance(value, dict):
        return _string(value)
    address = value.get('address')
    if isinstance(address, dict):
        parts = [_string(address.get('addressLocality')), _string(address.get('addressRegion')), _string(address.get('addressCountry'))]
        return ', '.join([part for part in parts if part])
    return _json_name(value)

def _page_title(page_html: str) -> str:
    match = re.search(r'<title[^>]*>(.*?)</title>', page_html, flags=re.I | re.S)
    return _strip_html(match.group(1)) if match else ''


def _looks_blocked(page_html: str) -> bool:
    text = _strip_html(page_html[:5000]).lower()
    return any(marker in text for marker in ['captcha', 'bot check', 'access denied', 'enable javascript', 'verify you are human', 'sign in to view'])


def _clean_visible_text(value: str) -> str:
    value = re.sub(r'\b(Cookie|Cookies|Privacy Policy|Terms of Use|Accept all|Reject all)\b', ' ', value, flags=re.I)
    return re.sub(r'\s+', ' ', html.unescape(value)).strip()


def _strip_title_noise(value: str) -> str:
    title = re.split(r'\s[-|]\s(?:careers|jobs|job opening|greenhouse|lever|workday)', value, flags=re.I)[0]
    return title.strip()[:160]


def _company_from_title(title: str) -> str:
    for pattern in [r'\bat\s+([^|\-]+)', r'\|\s*([^|\-]+)$', r'-\s*([^|\-]+)$']:
        match = re.search(pattern, title, flags=re.I)
        if match:
            company = match.group(1).strip()
            if 2 <= len(company) <= 80:
                return company
    return ''


def _company_from_text(text: str) -> str:
    match = re.search(r'(?:Company|Hiring Organization)\s*[:\-]\s*([A-Z][A-Za-z0-9&., ]{2,80})', text)
    return match.group(1).strip() if match else ''


def _location_from_text(text: str) -> str:
    match = re.search(r'(?:Location|Office|Based in)\s*[:\-]\s*([A-Z][A-Za-z, /&\-]{2,100})', text)
    if match:
        return match.group(1).strip()
    for country in ['Germany', 'Netherlands', 'Ireland', 'France', 'Spain', 'Sweden', 'Denmark', 'United Kingdom', 'India', 'United States', 'Australia', 'Remote']:
        if country.lower() in text.lower():
            return country
    return ''


def _date_from_text(text: str) -> str | None:
    match = re.search(r'\b20\d{2}-\d{2}-\d{2}\b', text)
    return match.group(0) if match else None


def _domain_label(url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.lower().removeprefix('www.')
    return host.split('.')[0].replace('-', ' ').title() or 'Public Job Source'


class _VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts: list[str] = []
        self.heading = ''
        self._skip_depth = 0
        self._current_heading = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag.lower() in {'script', 'style', 'svg', 'noscript'}:
            self._skip_depth += 1
        self._current_heading = tag.lower() == 'h1'

    def handle_endtag(self, tag: str):
        if tag.lower() in {'script', 'style', 'svg', 'noscript'} and self._skip_depth:
            self._skip_depth -= 1
        if tag.lower() == 'h1':
            self._current_heading = False

    def handle_data(self, data: str):
        if self._skip_depth:
            return
        text = data.strip()
        if not text:
            return
        if self._current_heading and not self.heading:
            self.heading = text
        if len(text) > 1:
            self.text_parts.append(text)
