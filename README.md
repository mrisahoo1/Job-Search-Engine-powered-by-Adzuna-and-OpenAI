# Job Search Engine, powered by Adzuna and OpenAI

A full-stack job search and curation workbench for finding relevant roles, ranking them against a resume, preparing tailored application material, and tracking hiring prospects. The app is built around an EU-first job search workflow, with Adzuna support for live job listings and optional OpenAI-powered personalization for resume and outreach drafts.

## Live Deployment

- Production: [job-search-curation-agent.vercel.app](https://job-search-curation-agent.vercel.app)
- Latest deployment: [job-search-curation-agent-nrhqtud66-chatgptbdsm-2985s-projects.vercel.app](https://job-search-curation-agent-nrhqtud66-chatgptbdsm-2985s-projects.vercel.app)

## What the Application Does

This application helps a job seeker move from raw job discovery to an organized application pipeline:

1. Upload or paste a resume/CV.
2. Choose a target role, region, search mode, remote preference, visa preference, and sources.
3. Search live job providers or Adzuna.
4. Normalize and deduplicate job postings across sources.
5. Score each job against the resume and explain the fit.
6. Select a job and generate tailored resume content.
7. Generate outreach drafts for the selected role.
8. Save the job as a prospect and track status, notes, and next actions.

The goal is not just to list jobs. It gives the candidate a structured workspace for deciding which jobs are worth applying to and what to do next.

## Core Features

- **Resume input and parsing**: paste resume text directly or upload TXT, DOCX, or best-effort PDF files through the resume parser.
- **Live search controls**: search by role, region, countries, source selection, remote-only preference, and visa sponsorship preference.
- **Adzuna search mode**: query Adzuna with configured credentials and fetch paginated results with total-count status messages.
- **Multiple source types**: supports Arbeitnow, Remotive, official company career links, Greenhouse-style boards, seeded examples, and Adzuna.
- **Fit evaluation**: ranks jobs using resume signals, matched skills, gaps, seniority hints, location fit, remote fit, and visa sponsorship signals.
- **Explainable recommendations**: each selected job shows fit score, confidence, strengths, and risks before the user takes action.
- **Tailored resume drafts**: creates a role-specific resume draft and change summary for the selected job while preserving truthful source facts.
- **Outreach drafts**: produces recruiter or hiring-team outreach messages for a selected job.
- **Prospect tracking**: saves jobs into a local prospect board with status, notes, and next-action fields.
- **Application boundary**: the app prepares materials and apply links, but it does not submit applications or send messages automatically.

## Search Modes

### Live Search

Live Search combines public or compliant sources and source-specific adapters:

- Arbeitnow for Europe-focused job board data.
- Remotive for remote roles.
- Official company career links for selected companies.
- Greenhouse-style board integrations where a public board API exists.
- Seeded examples so the app still demonstrates the workflow when public providers are unavailable.

Live Search deduplicates jobs by semantic job identity and apply URL, then filters by the active region, remote preference, and visa preference.

### Adzuna Search

Adzuna Search uses the Adzuna jobs API and the selected region to choose the country endpoint. Credentials are read from environment variables.

The connector supports pagination with:

- `ADZUNA_RESULTS_PER_PAGE`, capped at Adzuna's supported page size.
- `ADZUNA_MAX_RESULTS`, used to control how many results the app fetches before returning a response.

If a later page fails after at least one page succeeds, the app can return partial results with a degraded source status instead of dropping the whole search.

## OpenAI Personalization

OpenAI is optional. If `OPENAI_API_KEY` is configured, the backend calls the OpenAI Responses API to personalize structured JSON outputs for resume tailoring and outreach drafting. If no key is present, the app falls back to deterministic local draft generation so the workflow remains usable in development.

The default model is controlled by `OPENAI_MODEL` and currently defaults to `gpt-4o-mini`.

## User Workflow

1. **Resume panel**: paste resume text, load the sample resume, or upload a resume file.
2. **Preferences panel**: select Live Search or Adzuna Search, define the target role, choose the region, select sources, and set remote/visa preferences.
3. **Results list**: review ranked roles with source labels, fit scores, confidence, and direct apply links.
4. **Selected job workspace**: inspect why the job is a good or risky fit, then tailor a resume or draft outreach.
5. **Prospect board**: save promising jobs and manage them through statuses such as reviewing, tailored, outreach drafted, applied, interviewing, rejected, or archived.

## Architecture

```text
backend/   Python agents and services for sourcing, matching, parsing, tailoring, outreach, regions, and signals
api/       Vercel Python Function adapters for browser-facing API routes
frontend/  React and Vite workbench UI
specs/     Spec-kit specification, plan, contracts, and task artifacts
tests/     Project-level test area reserved by the generated structure
```

The frontend calls the Vercel API adapters. The adapters convert HTTP payloads into backend service calls and return JSON responses to the browser.

## API Routes

- `POST /api/search`: accepts resume text and search preferences, then returns ranked job results and source statuses.
- `POST /api/parse_resume`: accepts an uploaded resume payload and extracts text from TXT, DOCX, or best-effort PDF files.
- `POST /api/tailor`: accepts resume text, a selected job, and fit evaluation, then returns a tailored resume draft.
- `POST /api/outreach`: accepts resume text, a selected job, and fit evaluation, then returns outreach draft messages.

## Environment Variables

Set these locally or in Vercel. Do not commit real secrets.

```bash
ADZUNA_APP_ID=
ADZUNA_APP_KEY=
ADZUNA_RESULTS_PER_PAGE=50
ADZUNA_MAX_RESULTS=500
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

`ADZUNA_APP_ID` and `ADZUNA_APP_KEY` are required for Adzuna Search. `OPENAI_API_KEY` is optional and enables OpenAI-backed personalization.

## Local Development

Install dependencies:

```bash
npm install
```

Run the full test suite:

```bash
npm test
```

Start the local development server:

```bash
npm run dev
```

Build for production:

```bash
npm run build
```

## Validation Status

Current validation used before publishing this project:

- Backend unit tests: 36 tests passing.
- Frontend Vitest tests: 2 test files passing.
- Production build was previously validated during the implementation run.

There is currently no `npm run lint` script in `package.json`.

## Deployment

The project is configured for Vercel:

- The React/Vite frontend is built by the production build command.
- Python API adapters in `api/` are deployed as Vercel Functions.
- `vercel.json` configures the Python API function duration for broader paginated searches.

The stable production alias is:

```text
https://job-search-curation-agent.vercel.app
```

## Safety and Boundaries

This app is designed as a candidate-side assistant. It does not:

- Submit job applications.
- Send outreach messages.
- Bypass login, CAPTCHA, payment, protected pages, or legal attestations.
- Scrape closed platforms that do not expose a compliant public or authorized integration path.
- Invent resume experience that is not supported by the provided resume or user input.

It prepares drafts, explanations, and apply links so the user can review and take the final action manually.
