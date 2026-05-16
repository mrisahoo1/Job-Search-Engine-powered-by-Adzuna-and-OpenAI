# Implementation Plan: Job Search and Curation Agent

**Branch**: `001-job-curation-agent` | **Date**: 2026-05-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-job-curation-agent/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a deployable single-user web application for EU-focused job discovery, resume-to-job fit scoring, resume tailoring, outreach drafting, and prospect tracking. The first implementation is backend-first: Python agent/service modules own job sourcing, matching, curation, outreach drafting, and application-boundary logic. React/Vite owns the user workbench. Vercel receives a thin root `api/search.py` adapter because Vercel routes standalone Python Functions from the root `api` directory.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript 5.x frontend on Node.js 24.x  
**Primary Dependencies**: Python standard library backend for MVP; React, Vite, Vitest, lucide-react frontend; Vercel Python Functions  
**Storage**: Browser localStorage for MVP saved prospects and drafts; no server persistence in first release  
**Testing**: Python unittest for backend agents/services; Vitest for frontend persistence/UI-adjacent logic  
**Target Platform**: Vercel-hosted web app with Python serverless search endpoint  
**Project Type**: Web application with separate Python backend and TypeScript frontend folders  
**Performance Goals**: Initial search should return usable results in under 10 seconds when at least one public source responds; local scoring should complete under 1 second for 100 normalized jobs  
**Constraints**: User approval required for all external submissions/messages; no closed-platform scraping; no resume text in server logs; source failures must degrade gracefully; Vercel Python runtime is Beta, so backend remains dependency-light  
**Scale/Scope**: Single-user MVP with connector-based expansion path; EU region active by default with inactive future region options

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- User-Controlled Career Automation: PASS. Plan requires explicit review before applications or outreach are sent.
- Source Compliance: PASS. Initial connectors use public APIs or user-provided authorized endpoints; closed platforms are not scraped.
- Test-First Delivery: PASS. Tasks include failing Python backend tests before behavioral implementation.
- Explainable Matching: PASS. Fit evaluations include match reasons, gaps, confidence, and signal interpretation.
- Privacy and Secrets Hygiene: PASS. MVP keeps saved data in browser storage, avoids server persistence, and uses server-only source fetching for public APIs.

## Project Structure

### Documentation (this feature)

```text
specs/001-job-curation-agent/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── search-api.md
│   ├── tailoring-contract.md
│   └── outreach-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
api/
└── search.py                 # Thin Vercel adapter; imports backend.services.search

backend/
├── __init__.py
├── agents/
│   ├── __init__.py
│   ├── application_agent.py
│   ├── curation_agent.py
│   └── sourcing_agent.py
├── services/
│   ├── __init__.py
│   ├── matching.py
│   ├── models.py
│   ├── outreach.py
│   ├── resume.py
│   ├── resume_tailor.py
│   ├── search.py
│   ├── signals.py
│   └── sources.py
└── tests/
    ├── test_matching.py
    ├── test_outreach.py
    ├── test_resume.py
    ├── test_resume_tailor.py
    ├── test_search.py
    └── test_signals.py

frontend/
├── index.html
├── public/
│   └── favicon.svg
├── vite.config.ts
└── src/
    ├── App.tsx
    ├── main.tsx
    ├── styles.css
    ├── components/
    │   ├── JobResults.tsx
    │   ├── PreferencesPanel.tsx
    │   ├── ProspectBoard.tsx
    │   ├── ResumePanel.tsx
    │   └── SelectedJobWorkspace.tsx
    └── lib/
        ├── prospects.ts
        └── types.ts
```

**Structure Decision**: Use Python backend agents/services first, React frontend second. Python is the better long-term fit for sourcing agents, parsing, future authorized crawling, and AI workflows. Vercel Python Functions are supported but Beta, so the MVP backend stays dependency-light and uses a thin `api/search.py` adapter.

## Complexity Tracking

No constitution violations.
