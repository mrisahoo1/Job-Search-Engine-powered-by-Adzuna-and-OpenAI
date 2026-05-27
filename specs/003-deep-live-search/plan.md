# Implementation Plan: Deep Live Job Search

**Branch**: `003-deep-live-search` | **Date**: 2026-05-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-deep-live-search/spec.md`

## Summary

Improve Live Search so it no longer returns near-identical results across role queries. Add a deep live source that combines role-filtered public job feeds, optional public web search discovery through free-key providers, bounded multi-page public crawling and extraction, closed-platform link-only handling, deduplication, and the existing resume-fit ranking pipeline.

## Technical Context

**Language/Version**: Python 3.x for backend/Vercel functions; TypeScript 5.x on Node.js 24.x for frontend  
**Primary Dependencies**: Python standard library + existing pypdf; React, Vite, Vitest, lucide-react  
**Storage**: In-memory request workflow and local browser state already used by the app; no new persistent database  
**Testing**: Python unittest for backend; Vitest for frontend  
**Target Platform**: Vercel-hosted web app with Python serverless functions and Vite frontend  
**Project Type**: Web application with separate backend, frontend, and API folders  
**Performance Goals**: Typical deep live search should return partial useful results inside the existing hosted function execution limit  
**Constraints**: Maximize public-page crawl coverage; no login/captcha bypass; secrets remain backend-only; bounded discovery and crawl volume  
**Scale/Scope**: Single-user interactive job search workflow; EU + UK default with India, US, Australia, and Remote/Global selectable

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **User-Controlled Career Automation**: PASS. The feature only searches, ranks, tailors, and drafts; it does not send outreach or apply automatically.
- **Source Compliance**: PASS. The design uses public APIs, public search results, public pages, and link-only statuses for protected platforms.
- **Test-First Delivery**: PASS. Add backend tests before implementation for extraction, filtering, and source enablement.
- **Explainable Matching**: PASS. Results continue through existing fit evaluation with matched skills, risks, visa/remote notes, and confidence.
- **Privacy and Secrets Hygiene**: PASS. Optional search credentials are environment variables read only by backend code.

## Project Structure

### Documentation (this feature)

```text
specs/003-deep-live-search/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── search-response.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── services/
│   ├── sources.py
│   ├── search.py
│   └── models.py
└── tests/
    ├── test_sources.py
    └── test_deep_search.py

frontend/
└── src/
    ├── App.tsx
    ├── components/
    │   └── PreferencesPanel.tsx
    └── lib/
        └── types.ts

api/
└── search.py
```

**Structure Decision**: Preserve the existing frontend/backend/API split. Deep search is implemented as a backend source fetcher so the existing `/api/search` contract and frontend result components continue to work.

## Complexity Tracking

No constitution violations. No extra project or database introduced.
