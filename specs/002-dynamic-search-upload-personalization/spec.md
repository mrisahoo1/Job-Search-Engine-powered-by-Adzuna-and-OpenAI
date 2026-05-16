# Feature Specification: Dynamic Search, Resume Upload, and Personalization

**Feature Branch**: `002-dynamic-search-upload-personalization`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: User request to add selectable regions beyond EU, real-time web job results that react to role changes, PDF/DOCX resume upload, smarter personalized outreach/email drafts, and selected-JD-based resume tailoring.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search Real Jobs by Region and Role (Priority: P1)

As a candidate, I want to switch between EU+UK, India, US, Australia, and remote/global regions and see live job results that change with role and region so that the search is not static.

**Why this priority**: The current job search feels static and does not respond enough to role changes.

**Independent Test**: Select different regions and queries, run search, and verify backend request preferences and returned jobs reflect query/region filtering with live or source-attributed fallback statuses.

**Acceptance Scenarios**:

1. **Given** EU+UK is the default region, **When** the user changes region to India and searches for "backend engineer", **Then** the backend receives India preferences and results are filtered or labeled for India/remote relevance.
2. **Given** the user changes the role query from "software engineer" to "product manager", **When** search runs, **Then** the source requests and displayed result set reflect the new query.
3. **Given** a public source fails, **When** another source succeeds, **Then** partial live results remain visible with a degraded status for the failed source.

---

### User Story 2 - Upload Resume Files (Priority: P1)

As a candidate, I want to upload a PDF, DOCX, or TXT resume so that I do not have to paste resume text manually.

**Why this priority**: Uploading a CV is the normal workflow for users and feeds search, scoring, tailoring, and outreach.

**Independent Test**: Upload DOCX/TXT/PDF-like fixtures and verify parsed resume text populates the app and is used for search scoring.

**Acceptance Scenarios**:

1. **Given** a DOCX resume file, **When** the user uploads it, **Then** the backend extracts text and the frontend shows parse status.
2. **Given** an unsupported or unreadable file, **When** upload is attempted, **Then** the app shows a clear error and keeps existing resume text.

---

### User Story 3 - Personalize Drafts from Job Description (Priority: P2)

As a candidate, I want resume tailoring and outreach drafts to use the selected job description and my uploaded resume so that generated materials are specific and credible.

**Why this priority**: Generic messages reduce the product value.

**Independent Test**: Select two different jobs and verify tailored resume summaries and outreach drafts differ by company, role, match evidence, gaps, and visa/remote context.

**Acceptance Scenarios**:

1. **Given** a selected job with a job description, **When** the user requests resume tailoring, **Then** the generated CV draft emphasizes matched evidence and flags missing requirements without inventing facts.
2. **Given** optional LLM credentials are not configured, **When** outreach is drafted, **Then** deterministic personalized drafts are still generated.
3. **Given** optional LLM credentials are configured, **When** personalization succeeds, **Then** the app may use model output while preserving approval boundaries and fallback behavior.

---

### Edge Cases

- Source results may be unavailable, rate limited, duplicated, or region-ambiguous.
- PDF extraction may fail for scanned image PDFs without OCR.
- DOCX files may contain tables or headers; text extraction should preserve readable content where possible.
- LLM calls may fail or be unavailable; deterministic fallback must still produce usable drafts.
- API keys and user resume content must not be logged or committed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Region selection MUST default to EU+UK and allow switching to India, US, Australia, and Remote/Global.
- **FR-002**: The backend search request MUST include selected region, countries, query, remote, visa, and enabled source preferences.
- **FR-003**: Search results MUST be fetched from public/compliant web sources when available, with source attribution and source status messages.
- **FR-004**: Search results MUST be filtered or ranked using query and region relevance so different queries and regions can produce different ranked results.
- **FR-005**: Users MUST be able to upload PDF, DOCX, or TXT resume files and receive parsed resume text.
- **FR-006**: Parsed resume text MUST feed search scoring, resume tailoring, and outreach generation.
- **FR-007**: Tailored CV generation MUST use the selected job title, company, job description, matched evidence, and gaps.
- **FR-008**: Outreach generation MUST produce differentiated LinkedIn and email drafts using role, company, match evidence, gaps, remote/visa context, and contact hints.
- **FR-009**: Optional OpenAI personalization MUST use server-side environment variables only and must fall back to deterministic drafting when unavailable.
- **FR-010**: The frontend MUST provide reactive upload/search/generation states instead of rigid static controls.
- **FR-011**: Secrets MUST NOT be committed, displayed, or bundled into frontend code.

### Key Entities

- **Region Option**: Selectable region with label, default countries, source hints, and search terms.
- **Parsed Resume**: Extracted resume text, file name, file type, parser warnings, and confidence.
- **Live Source Result**: Source-attributed job postings and status returned by public source connectors.
- **Personalization Request**: Resume, selected job, fit evaluation, and optional instructions for tailoring/outreach.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can switch region and query and see changed search preferences reflected in the result request and UI within one search cycle.
- **SC-002**: TXT and DOCX resume upload parsing succeeds for representative text-based fixtures; PDF text extraction succeeds when text is extractable.
- **SC-003**: Two different selected jobs generate visibly different outreach drafts and tailored resume summaries.
- **SC-004**: The app remains usable without OpenAI credentials.
- **SC-005**: No secret values appear in committed files or frontend bundles.

## Assumptions

- OCR for scanned PDFs is out of scope for this version.
- Public source availability may vary; source statuses explain live failures.
- Adzuna is supported only when the user later configures API credentials.
- The user will configure OpenAI keys in Vercel or local `.env`, not in committed files.
