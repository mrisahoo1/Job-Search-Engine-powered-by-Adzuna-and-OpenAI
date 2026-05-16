# Job Search Curation Agent

A backend-first job prospect assembly app for real-time job search, resume fit scoring, tailored CV drafts, outreach drafts, and prospect tracking.

## Architecture

```text
backend/   Python agents and services for sourcing, matching, parsing, tailoring, outreach
api/       Thin Vercel Python Function adapters
frontend/  React/Vite workbench UI
specs/     Spec-kit specification, plan, contracts, and tasks
```

## Search Modes

- **Live Search**: public/compliant sources plus official company career sources. Current connectors include Arbeitnow, Remotive, official company hints, Greenhouse-style boards, and seeded fallback examples.
- **Adzuna Search**: uses the Adzuna API endpoint format `https://api.adzuna.com/v1/api/jobs/{country}/search/1?app_id=...&app_key=...` with region-specific country codes.

Live Search deduplicates by apply URL, title, and company before ranking.

## Resume Upload

The app supports TXT, DOCX, and best-effort PDF parsing through `api/parse_resume.py`. Scanned PDFs without OCR may not extract clean text.

## Optional Environment Variables

Set these locally or in Vercel. Do not commit real secrets.

```bash
ADZUNA_APP_ID=
ADZUNA_APP_KEY=
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

## Local Development

```bash
npm install
npm test
npm run dev
```

Production build:

```bash
npm run build
```

## Application Boundary

The system prepares application materials and direct apply links. It does not submit applications, answer legal attestations, bypass login/CAPTCHA, or send outreach without explicit user action.
