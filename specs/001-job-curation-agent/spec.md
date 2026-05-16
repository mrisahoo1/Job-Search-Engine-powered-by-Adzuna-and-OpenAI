# Feature Specification: Job Search and Curation Agent

**Feature Branch**: `001-job-curation-agent`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: User description: "Create a full-fledged job search and curation agent that searches EU job opportunities based on my resume, prioritizes remote and visa sponsorship roles, evaluates fit, curates resumes, drafts outreach, provides direct apply links, and can assist with the hiring prospect workflow."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Discover Matched EU Jobs (Priority: P1)

As a candidate targeting Europe, I want to upload or paste my resume and search EU-focused opportunities so that I can quickly see remote and visa-sponsorship-friendly roles that match my background.

**Why this priority**: This is the core value of the product. Without job discovery and fit ranking, resume curation and outreach have no target.

**Independent Test**: Can be tested by providing a resume and search preferences, running a search, and verifying that the result list contains EU-scoped jobs with fit scores, remote/visa indicators, source labels, and direct links.

**Acceptance Scenarios**:

1. **Given** a candidate resume and default EU region scope, **When** the user starts a search, **Then** the system returns a ranked list of jobs with title, company, location, remote status, sponsorship signal, source, fit score, confidence, and direct apply link where available.
2. **Given** a job description with skills that partially match the resume, **When** the result is scored, **Then** the system explains matched strengths, gaps, missing evidence, and why the role is or is not a strong fit.
3. **Given** a user wants to expand beyond the default region later, **When** they view region settings, **Then** the product shows EU as active and presents inactive expansion options without including them in the current search.

---

### User Story 2 - Curate Resume for a Selected Job (Priority: P2)

As a candidate reviewing a promising job, I want the system to propose a tailored resume version based on the job description so that my application highlights the most relevant experience without inventing facts.

**Why this priority**: Once the user identifies a target role, tailored application material is the next highest leverage step.

**Independent Test**: Can be tested by selecting a job and a resume, generating a tailored resume draft, and verifying that it preserves truthful source facts while emphasizing job-relevant skills and experience.

**Acceptance Scenarios**:

1. **Given** a selected job and an existing resume, **When** the user requests tailoring, **Then** the system produces a revised resume draft with a change summary and role-specific emphasis.
2. **Given** the job asks for skills not present in the resume, **When** the tailored draft is generated, **Then** the system flags those gaps instead of fabricating experience.
3. **Given** the user rejects a suggested resume change, **When** they return to the job, **Then** the original resume content remains recoverable.

---

### User Story 3 - Draft Outreach and Application Packets (Priority: P3)

As a candidate, I want the system to identify plausible outreach targets and draft messages so that I can contact recruiters, hiring managers, or relevant employees for a selected role.

**Why this priority**: Outreach increases the value of curated opportunities but depends on having selected roles first.

**Independent Test**: Can be tested by selecting a job and verifying that the product generates outreach target suggestions, message drafts, and a review step before sending or copying.

**Acceptance Scenarios**:

1. **Given** a selected job with company information, **When** the user requests outreach support, **Then** the system suggests target personas or public profile search links and generates concise message drafts for LinkedIn, email, or text.
2. **Given** the system cannot confidently identify a named contact, **When** outreach support is requested, **Then** it provides search guidance and role/persona suggestions rather than guessing a person.
3. **Given** a drafted message or application packet, **When** the user has not approved it, **Then** the system does not send, submit, or represent the content as sent.

---

### User Story 4 - Track Prospects Through the Hiring Process (Priority: P4)

As a candidate managing multiple prospects, I want to save jobs and track progress so that I can manage outreach, applications, follow-ups, and decisions in one place.

**Why this priority**: Tracking improves long-running workflow value, but the MVP can function with search and selected job actions first.

**Independent Test**: Can be tested by saving jobs, changing their status, adding notes, and confirming the prospect board reflects the updated hiring pipeline.

**Acceptance Scenarios**:

1. **Given** a job result, **When** the user saves it, **Then** it appears in the prospect tracker with source, status, next action, and timestamp.
2. **Given** a saved prospect, **When** the user updates its status, **Then** the system preserves the timeline and latest next step.

### Edge Cases

- If a job source is unavailable, rate limited, or returns malformed data, the system shows partial results from other sources and records which source failed.
- If no EU jobs match the current preferences, the system explains the empty state and suggests preference changes such as broader titles, adjacent skills, or remote-only relaxation.
- If a job appears multiple times across sources, the system groups or deduplicates it while preserving source links.
- If remote or visa sponsorship is ambiguous, the system marks the signal as unknown with low confidence rather than treating it as positive.
- If a resume is missing key sections or is too sparse to score confidently, the system asks the user to add more resume detail before relying on fit scores.
- If a job board blocks automated access or forbids scraping, the system must skip that source unless the user provides a compliant link or authorized integration.
- If an application requires custom questions, login, CAPTCHA, payment, protected pages, or legally significant attestations, the system must require manual user intervention.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to provide a resume or CV as text or file content for analysis.
- **FR-002**: Users MUST be able to define search preferences including target titles, keywords, seniority, remote preference, visa sponsorship preference, countries or region, and source scope.
- **FR-003**: The default active region MUST be Europe, and all non-Europe expansion options MUST remain inactive until the user explicitly enables them.
- **FR-004**: The system MUST collect job opportunities from compliant public or user-authorized sources and normalize them into a consistent result format.
- **FR-005**: The system MUST inspect job titles, company names, locations, descriptions, remote signals, sponsorship signals, and apply links when those fields are available.
- **FR-006**: The system MUST score each job against the resume and search preferences using explainable factors, including matched skills, relevant experience, seniority, location fit, remote fit, visa sponsorship signal, and missing evidence.
- **FR-007**: The system MUST display fit score, confidence, recommendation category, reasons to apply, risks or gaps, source attribution, and direct application link for each job result.
- **FR-008**: Users MUST be able to save, reject, or mark a job for later review.
- **FR-009**: Users MUST be able to generate a tailored resume draft for a selected job based only on resume facts and user-provided information.
- **FR-010**: The tailored resume flow MUST show a summary of changes, gaps that cannot be filled truthfully, and the source resume content used.
- **FR-011**: Users MUST be able to generate outreach drafts for selected jobs in at least LinkedIn-style short message and email-style formats.
- **FR-012**: The system MUST suggest outreach targets as roles, personas, or public search links when named contacts are not reliably available.
- **FR-013**: The system MUST provide application assistance, but MUST require explicit user approval before submitting an application, sending a message, or marking an external action complete.
- **FR-014**: The system MUST track prospect status, notes, generated materials, next action, and timestamps for saved jobs.
- **FR-015**: The system MUST support source expansion through a documented connector model so additional regions or job sources can be added without redesigning the user workflow.
- **FR-016**: The system MUST protect sensitive resume and contact data from unnecessary exposure in logs, public pages, or client-visible secrets.
- **FR-017**: The system MUST identify unavailable, unsupported, or non-compliant sources and communicate that limitation to the user.
- **FR-018**: The system MUST provide a deployable web experience that can be accessed from different devices.

### Key Entities *(include if feature involves data)*

- **Candidate Profile**: Resume content, extracted skills, experience, target titles, preferred countries, remote preference, visa sponsorship preference, and contact preferences.
- **Search Preference**: User-selected job criteria such as region, countries, titles, keywords, seniority, source selection, remote mode, sponsorship requirement, and freshness window.
- **Job Source**: A compliant source configuration with name, region coverage, supported fields, limitations, and availability status.
- **Job Posting**: A normalized opportunity with title, company, location, description, tags, remote signal, sponsorship signal, source, date, apply URL, and raw source reference.
- **Fit Evaluation**: Match score, confidence, matched evidence, gaps, recommendation category, and explanation for a candidate-job pair.
- **Resume Draft**: A generated resume variant tied to a selected job, source resume, edits, warnings, and user decision.
- **Outreach Draft**: A generated message tied to a job and target persona or contact hint, including channel, tone, content, and review status.
- **Prospect**: A saved job with status, notes, next action, history, generated materials, and timestamps.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can enter resume content, run an EU-focused search, and review ranked results in under 5 minutes.
- **SC-002**: At least 90% of displayed job results include title, company, location or remote marker, source, fit explanation, and a link to view or apply.
- **SC-003**: At least 80% of jobs with explicit remote or visa sponsorship text are correctly labeled with the corresponding signal during manual review of a representative sample.
- **SC-004**: For any scored job, a user can identify the top three match reasons and top three gaps without reading the full job description.
- **SC-005**: A selected job can produce a tailored resume draft and outreach draft in under 2 minutes after the user requests them.
- **SC-006**: The system never submits an application or sends outreach unless the user approves that specific external action.
- **SC-007**: A new compliant job source or non-EU region can be added through the connector model without changing the saved prospect workflow.
- **SC-008**: Users can save a prospect and update its status with no data loss across normal page navigation.

## Assumptions

- The first release is a single-user web application intended for the requesting candidate.
- Europe means EU and Europe-adjacent job market coverage for remote relocation opportunities, but the active default filter is EU-focused roles unless the user broadens it.
- The first release emphasizes software and technology roles because the resume was not yet provided and this is the most likely target domain for the requester.
- Fully automated application submission is out of scope unless a source explicitly supports authorized submission and the user reviews the final packet first.
- LinkedIn, Indeed, and similar closed platforms are not scraped directly; the product can generate search links, outreach copy, and manual workflow guidance for those platforms.
- Real-time job availability can change after ingestion, so apply links may become stale and must be shown with source and fetched time.
- The product can operate with public/sample sources in development and accept credentials for richer providers later.
