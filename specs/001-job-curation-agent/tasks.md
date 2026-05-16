# Tasks: Job Search and Curation Agent

**Input**: Design documents from `/specs/001-job-curation-agent/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Testing**: Required. Follow TDD for behavioral logic.

## Phase 1: Setup

- [X] T001 Create root package/build config and separate frontend/backend directories in package.json, frontend/vite.config.ts, tsconfig.json, and vitest.config.ts
- [X] T002 Create Vercel deployment configuration and Python runtime markers in vercel.json, .python-version, and requirements.txt
- [X] T003 Create ignore and environment example files in .gitignore and .env.example
- [X] T004 Create frontend entry files in frontend/index.html, frontend/src/main.tsx, frontend/src/App.tsx, frontend/src/styles.css, and frontend/public/favicon.svg

## Phase 2: Backend-First Tests and Contracts

- [X] T005 [P] Define Python domain models in backend/services/models.py and frontend API mirror types in frontend/src/lib/types.ts
- [X] T006 [P] Create reusable Python test fixtures in backend/tests/fixtures.py
- [X] T007 [P] Write failing resume parsing tests in backend/tests/test_resume.py
- [X] T008 [P] Write failing signal detection tests in backend/tests/test_signals.py
- [X] T009 [P] Write failing matching tests in backend/tests/test_matching.py
- [X] T010 [P] Write failing search aggregation tests in backend/tests/test_search.py
- [X] T011 [P] Write failing resume tailoring tests in backend/tests/test_resume_tailor.py
- [X] T012 [P] Write failing outreach drafting tests in backend/tests/test_outreach.py
- [X] T013 [P] Write failing frontend prospect persistence tests in frontend/src/test/prospects.test.ts

## Phase 3: Python Backend Agents and Services (Priority: P1)

**Goal**: Backend can parse resume, source/normalize EU jobs, score fit, tailor resumes, draft outreach, and enforce approval boundaries.
**Independent Test**: Run backend unit tests against fixture resume and fixture jobs; verify explainable ranked results and generated drafts.

- [X] T014 [US1] Implement resume parsing in backend/services/resume.py
- [X] T015 [US1] Implement remote, visa, location, and seniority signal detection in backend/services/signals.py
- [X] T016 [US1] Implement fit scoring and explanation logic in backend/services/matching.py
- [X] T017 [US1] Implement source metadata and normalizers in backend/services/sources.py
- [X] T018 [US1] Implement job aggregation, filtering, deduplication, scoring, and graceful fallback behavior in backend/services/search.py
- [X] T019 [US1] Implement Python sourcing/curation/application agents in backend/agents/*.py and Vercel adapter in api/search.py
- [X] T020 [US2] Implement truthful resume tailoring in backend/services/resume_tailor.py
- [X] T021 [US3] Implement outreach message and contact-hint generation in backend/services/outreach.py

## Phase 4: React Frontend Integration (Priorities: P1-P4)

**Goal**: User can operate the full workflow through separated frontend files that call the Python backend API.
**Independent Test**: Start frontend, run search, inspect ranked results, generate drafts, save prospects, and update statuses.

- [X] T022 [US1] Build resume and search preferences UI in frontend/src/components/ResumePanel.tsx and frontend/src/components/PreferencesPanel.tsx
- [X] T023 [US1] Build ranked job results UI in frontend/src/components/JobResults.tsx
- [X] T024 [US2] Add selected job workspace resume draft controls in frontend/src/components/SelectedJobWorkspace.tsx
- [X] T025 [US3] Add outreach drafting and direct apply packet controls in frontend/src/components/SelectedJobWorkspace.tsx
- [X] T026 [US4] Implement prospect persistence helpers in frontend/src/lib/prospects.ts
- [X] T027 [US4] Build prospect board UI in frontend/src/components/ProspectBoard.tsx
- [X] T028 [US1-US4] Wire all flows into frontend/src/App.tsx

## Phase 5: Polish and Cross-Cutting Concerns

- [X] T029 [P] Add accessible empty, loading, degraded source, and error states across frontend/src/components/*.tsx
- [X] T030 [P] Add README.md with setup, source-compliance notes, and deployment instructions
- [X] T031 Run npm test and fix any failing tests
- [X] T032 Run npm run build and fix any production build issues
- [X] T033 Deploy the app to Vercel and record the deployment URL

## Dependencies

- Phase 1 before all other work.
- Phase 2 tests before backend implementation tasks T014-T021.
- Backend services and agents complete before frontend integration.
- Frontend prospect persistence can proceed after frontend API mirror types exist.
- Polish and deployment after backend and frontend flows are integrated.

## Parallel Opportunities

- T005-T013 can run in parallel after setup because they write separate files.
- T014-T017 are independent service modules after models exist.
- T020 and T021 can run in parallel because tailoring and outreach are separate backend services.
- T022-T027 can run in parallel after frontend types and backend API shape are stable.

## Implementation Strategy

1. Build backend tests and Python services first.
2. Add agent orchestration wrappers and Vercel Python adapter.
3. Integrate React frontend against the API contract.
4. Finish with persistence, accessibility states, docs, tests, production build, and Vercel deployment.




