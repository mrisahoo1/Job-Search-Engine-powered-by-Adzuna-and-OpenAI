# Tasks: Deep Live Job Search

**Input**: Design documents from `/specs/003-deep-live-search/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/search-response.md, quickstart.md

## Phase 1: Setup

- [x] T001 Verify current backend live-search baseline in notes in `specs/003-deep-live-search/quickstart.md`
- [x] T002 Add optional deep-search environment placeholders in `.env.example`

## Phase 2: Foundational Tests

- [x] T003 [P] Add backend tests for deep HTML/JSON-LD job extraction in `backend/tests/test_deep_search.py`
- [x] T004 [P] Add backend tests for query-specific deep source filtering and closed-platform link-only handling in `backend/tests/test_deep_search.py`
- [x] T005 [P] Add backend test for enabling the `deep` source in the live source selector in `backend/tests/test_live_search.py`

## Phase 3: User Story 1 - Query-Specific Deep Live Results (P1)

**Goal**: Deep live search produces materially different results for different role queries and avoids seeded fallback unless explicitly selected.

**Independent Test**: Run backend tests and a live smoke search for `generative ai engineer` and `data engineer`; verify different top results and source statuses.

- [x] T006 [US1] Implement role-term extraction and relevance filtering helpers in `backend/services/sources.py`
- [x] T007 [US1] Implement public RemoteOK normalization and source fetching in `backend/services/sources.py`
- [x] T008 [US1] Implement `fetch_deep_live` using no-key public job feeds and bounded result volume in `backend/services/sources.py`
- [x] T009 [US1] Register `fetch_deep_live` in live source ordering and source filtering in `backend/services/sources.py` and `backend/services/search.py`
- [x] T010 [US1] Update default backend/API live sources to prefer `deep` and avoid seeded fallback by default in `backend/services/models.py` and `api/search.py`

## Phase 4: User Story 2 - High-Coverage Public Crawl Expansion (P2)

**Goal**: Deep live search can optionally discover public job URLs across job boards, remote sites, ATS pages, and official sites; crawl accessible public pages deeply; and mark protected platforms as unavailable/link-only when they cannot be crawled.

**Independent Test**: With mocked discovery payloads, verify crawled public jobs become JobPosting records and LinkedIn/Naukri/Instahyre/Wellfound-style links are not crawled.

- [x] T011 [US2] Add public page extraction helpers for title, JSON-LD JobPosting data, company, location, and description in `backend/services/sources.py`
- [x] T012 [US2] Add optional Brave and Google Programmable Search discovery using backend-only `BRAVE_SEARCH_API_KEY` in `backend/services/sources.py`
- [x] T013 [US2] Add closed-platform link-only handling for protected domains in `backend/services/sources.py`
- [x] T014 [US2] Add deep-search source status messages for no-key, partial, blocked, and crawled outcomes in `backend/services/sources.py`

## Phase 5: User Story 3 - Resume Workflow Continuity (P3)

**Goal**: Deep search appears in the UI and feeds the existing selected-job, tailoring, outreach, and download workflow.

**Independent Test**: Use the UI to enable Deep Search, run a search, select a deep result, tailor a resume, switch jobs, and confirm drafts reset.

- [x] T015 [US3] Add `deep` to frontend source controls and defaults in `frontend/src/components/PreferencesPanel.tsx`, `frontend/src/App.tsx`, and `frontend/src/lib/types.ts`
- [x] T016 [US3] Improve source labels so Deep Search explains optional Brave API and public feed behavior in `frontend/src/components/PreferencesPanel.tsx`

## Phase 6: Polish & Verification

- [x] T017 Run `npm run test:backend` and fix failures
- [x] T018 Run `npm run test:frontend` and fix failures
- [x] T019 Run `npm run build` and fix failures
- [x] T020 Run live smoke comparison for current deep search behavior and record results in final response
- [x] T021 Deploy a new Vercel preview for the deep live search version

## Dependencies

- Setup tasks T001-T002 before implementation.
- Tests T003-T005 before implementation tasks T006-T014.
- US1 tasks T006-T010 are the MVP and should complete before US2/US3.
- US2 tasks T011-T014 depend on T006-T010.
- US3 tasks T015-T016 depend on T009-T010.
- Verification T017-T021 runs after implementation.

## Parallel Example

- T003, T004, and T005 can be written together because they touch independent test concerns.
- T015 can run alongside T014 after backend source registration is complete.

## Implementation Strategy

Deliver MVP first: role-filtered deep search using no-key public job feeds. Then add optional Brave public discovery and closed-platform link-only treatment. Finish by exposing the deep source in the frontend and verifying tests, build, live smoke behavior, and deployment.

