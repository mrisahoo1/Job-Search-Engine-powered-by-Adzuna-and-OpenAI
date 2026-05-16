# Implementation Plan: Dynamic Search, Resume Upload, and Personalization

**Branch**: `002-dynamic-search-upload-personalization` | **Date**: 2026-05-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-dynamic-search-upload-personalization/spec.md`

## Summary

Upgrade the Python-backend/React-frontend app into a more complete job search agent: selectable regions, live public/compliant source connectors, official company/ATS source support, resume file parsing, and smarter JD-specific personalization. The backend remains the source of truth for parsing/search/tailoring/outreach. The frontend becomes reactive and file-first while keeping text editing available.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript 5.x frontend on Node.js 24.x  
**Primary Dependencies**: Python standard library, optional `pypdf` and `python-docx` for resume parsing, React, Vite, Vitest, lucide-react  
**Storage**: Browser localStorage for prospects and generated materials; no server persistence  
**Testing**: Python unittest for backend services/endpoints; Vitest for frontend persistence and API shapes  
**Target Platform**: Vercel-hosted web app with Python Functions  
**Project Type**: Web app with Python backend and React frontend  
**Performance Goals**: Search returns partial usable results within 12 seconds; upload parsing returns within 8 seconds for normal resumes  
**Constraints**: No scraping closed platforms; official sources use public APIs, known ATS endpoints, or user-provided official URLs; OpenAI is optional via environment variables and never committed  
**Scale/Scope**: Single-user MVP with multiple regions and expandable official-source registry

## Constitution Check

- User-Controlled Career Automation: PASS. External actions remain review-only.
- Source Compliance: PASS. Official sources are represented as public APIs, ATS endpoints, or search/deep-link hints when no compliant API is available.
- Test-First Delivery: PASS. Backend behavior changes are covered by tests before implementation.
- Explainable Matching: PASS. Search still returns fit reasoning and signal notes.
- Privacy and Secrets Hygiene: PASS. OpenAI key is environment-only; uploaded files are parsed in request scope and not persisted server-side.

## Project Structure

```text
api/
├── outreach.py
├── parse_resume.py
├── search.py
└── tailor.py

backend/
├── agents/
│   ├── application_agent.py
│   ├── curation_agent.py
│   └── sourcing_agent.py
├── services/
│   ├── llm.py
│   ├── models.py
│   ├── regions.py
│   ├── resume_file_parser.py
│   ├── search.py
│   ├── sources.py
│   └── ...existing services
└── tests/
    ├── test_regions.py
    ├── test_resume_file_parser.py
    ├── test_sources.py
    ├── test_personalization.py
    └── ...existing tests

frontend/
└── src/
    ├── components/
    │   ├── PreferencesPanel.tsx
    │   ├── ResumePanel.tsx
    │   └── SelectedJobWorkspace.tsx
    └── lib/types.ts
```

**Structure Decision**: Add backend capabilities first, then adapt frontend components to call them. Official company sites are source connectors/hints, not brittle browser scraping.

## Complexity Tracking

No constitution violations.
