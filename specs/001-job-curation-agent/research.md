# Research: Job Search and Curation Agent

## Decision: Use a Vite React app with Vercel Node.js Functions

**Rationale**: The product needs an accessible web UI, client-side resume workflow, and a server-side search endpoint for public job sources. Vercel currently supports Node.js 24.x, 22.x, and 20.x for functions, so Node.js 24.x matches the local runtime and deployment target.

**Alternatives considered**:

- Next.js full-stack app: Strong Vercel fit, but heavier than needed for a single-screen MVP with one API endpoint.
- Static-only app: Simpler, but browser-only source fetching can hit CORS limits and exposes source integration details.
- Python backend plus frontend: Flexible for scraping, but larger deployment surface and unnecessary for the compliant public-source MVP.

## Decision: Start with public/compliant job sources and connector boundaries

**Rationale**: The product must avoid closed-platform scraping and platform bypassing. Arbeitnow documents a free Europe-focused job API with remote and visa sponsorship parameters. Remotive offers a public remote jobs API with attribution requirements. Greenhouse, Lever, Ashby, and SmartRecruiters expose public or customer-authorized job-board APIs that work well when a company board identifier is known.

**Alternatives considered**:

- Scrape LinkedIn, Indeed, or every job board: Rejected because it can violate platform controls and is brittle.
- Require paid aggregators from day one: Rejected because the MVP should run without credentials.
- Only use sample jobs: Useful for tests, but insufficient for real use.

## Decision: Deterministic explainable matching for MVP

**Rationale**: A deterministic matcher can score skills, title overlap, seniority, remote preference, visa sponsorship signal, and gaps without requiring paid AI keys. It is auditable, testable, and safe for first release.

**Alternatives considered**:

- LLM-only matching: More flexible, but harder to test deterministically and may require sensitive resume data to leave the app.
- Manual scoring only: Too slow for the target workflow.

## Decision: Browser localStorage for saved prospects in first release

**Rationale**: The requester needs an immediately usable personal tool. Local storage avoids account setup and reduces server-side handling of sensitive resume and prospect data.

**Alternatives considered**:

- Hosted database: Better for multi-device sync but introduces authentication, privacy, and operations scope.
- File export only: Good backup path but too weak for an interactive prospect board.

## Decision: Application automation remains user-reviewed assistance

**Rationale**: Job applications can include legal attestations, custom questions, login-only steps, CAPTCHAs, and consent requirements. The first release prepares packets and direct links, but does not submit external actions without explicit approval.

**Alternatives considered**:

- Fully autonomous apply bot: Rejected for compliance, quality, and consent reasons.
- No application support: Rejected because direct links, tailored packets, and checklists are core to the workflow.
