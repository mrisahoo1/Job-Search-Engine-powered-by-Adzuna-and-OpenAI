# Tasks: Dynamic Search, Resume Upload, and Personalization

## Phase 1: Backend Tests and Models

- [X] T001 Add region model/tests in backend/services/regions.py and backend/tests/test_regions.py
- [X] T002 Add resume file parser tests in backend/tests/test_resume_file_parser.py
- [X] T003 Add source connector tests for query/region variation and official ATS sources in backend/tests/test_sources.py
- [X] T004 Add personalization tests for distinct tailoring/outreach drafts in backend/tests/test_personalization.py

## Phase 2: Backend Implementation

- [X] T005 Implement region registry and preference normalization in backend/services/regions.py and backend/services/models.py
- [X] T006 Implement TXT, DOCX, and best-effort PDF resume parsing in backend/services/resume_file_parser.py and api/parse_resume.py
- [X] T007 Expand source connectors for region-aware Arbeitnow/Remotive/Adzuna and official Greenhouse/company source registry in backend/services/sources.py
- [X] T008 Update search orchestration to use region registry, enabled sources, official companies, and query-sensitive ranking in backend/services/search.py
- [X] T009 Add optional OpenAI personalization service with deterministic fallback in backend/services/llm.py, backend/services/resume_tailor.py, and backend/services/outreach.py

## Phase 3: Frontend Integration

- [X] T010 Update frontend API types for regions, parser result, source filters, and generated drafts in frontend/src/lib/types.ts
- [X] T011 Replace static region controls with selectable region/source controls in frontend/src/components/PreferencesPanel.tsx
- [X] T012 Add PDF/DOCX/TXT upload flow and parse status in frontend/src/components/ResumePanel.tsx
- [X] T013 Make selected-job workspace reactive for JD-specific resume tailoring and differentiated outreach in frontend/src/components/SelectedJobWorkspace.tsx
- [X] T014 Update App state flow so searches use uploaded resume text and selected regions/sources in frontend/src/App.tsx
- [X] T015 Refine UI states for live search, upload parsing, official-source statuses, and source failures in frontend/src/styles.css

## Phase 4: Verification and Deployment

- [X] T016 Update README and .env.example with optional OpenAI/Adzuna configuration and secret-handling notes
- [X] T017 Run full tests and production build
- [X] T018 Deploy new Vercel version


