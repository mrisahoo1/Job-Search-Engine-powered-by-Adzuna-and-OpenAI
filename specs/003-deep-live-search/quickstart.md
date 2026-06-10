# Quickstart: Deep Live Job Search

## Environment

Optional backend environment variables:

```text
BRAVE_SEARCH_API_KEY=
DEEP_SEARCH_MAX_RESULTS=60
DEEP_CRAWL_MAX_PAGES=12
DEEP_SEARCH_QUERY_COUNT=6
```

The feature works without `BRAVE_SEARCH_API_KEY` by using no-key public job sources and official configured sources.

## Backend Verification

```powershell
npm run test:backend
```

Expected: backend tests pass, including deep-search extraction, role filtering, and source enablement.

## Frontend Verification

```powershell
npm run test:frontend
npm run build
```

Expected: frontend tests and production build pass.

## Manual Smoke Test

1. Upload or use a resume.
2. Keep region as EU + UK.
3. Select Live Search and enable Deep Search.
4. Search for `generative ai engineer`.
5. Note result count and top 10 titles.
6. Search for `data engineer`.
7. Confirm the top results materially differ and source statuses explain which providers were used.
8. Select a job, tailor the resume, and download the tailored draft.

## Smoke Evidence

Pre-Tavily deep search smoke:
- generative ai engineer: 8 results from public feeds only
- data engineer: 4 results from public feeds only
- backend engineer: 3 results from public feeds only

Tavily-enabled deep search smoke:
- generative ai engineer: 13 results, including Tavily-discovered AI engineer listing/search pages plus Remotive and Arbeitnow jobs
- data engineer: 9 results, including Tavily-discovered data engineer listing pages plus feed results
- backend engineer: 4 results, still weaker and should be improved with Brave or more ATS-specific crawling later

Verification completed:
- npm run test:backend
- npm run test:frontend
- npm run build
