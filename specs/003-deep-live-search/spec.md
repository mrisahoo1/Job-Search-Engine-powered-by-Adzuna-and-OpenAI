# Feature Specification: Deep Live Job Search

**Feature Branch**: `003-deep-live-search`  
**Created**: 2026-05-27  
**Status**: Draft  
**Input**: User description: "Use spec-kit to add a deep live job search feature that improves the current weak live search by discovering real-time public job pages across remote boards, official company sites, and major job portals where accessible; crawl job descriptions; deduplicate results; rank them against the uploaded resume; and preserve the existing resume tailoring and outreach workflow. EU + UK remains the default region, with selectable India, US, Australia, and Remote/Global expansion."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Query-Specific Deep Live Results (Priority: P1)

A candidate uploads a resume, enters a target role, keeps EU + UK as the default region or selects another supported region, and runs a deep live search. The returned jobs should materially change when the target role changes and should include public job descriptions or enough extracted detail to support fit scoring.

**Why this priority**: The current live search returns nearly identical results for different roles, which undermines the core value of the product.

**Independent Test**: Run deep live search for at least two distinct target roles using the same resume and verify that source statuses, job titles, descriptions, and top-ranked results differ meaningfully between roles.

**Acceptance Scenarios**:

1. **Given** an uploaded resume and the default EU + UK region, **When** the user searches for "Generative AI Engineer", **Then** the system returns query-specific public jobs with application links, extracted descriptions, and fit evaluations.
2. **Given** the same uploaded resume, **When** the user changes the role to "Data Engineer", **Then** the top results differ from the AI-engineer search and reflect data-engineering language in titles, descriptions, or tags.
3. **Given** live sources are slow or partially unavailable, **When** the search completes, **Then** the user sees partial real results with clear source status messages instead of silent seeded-only output.

---

### User Story 2 - Compliant Source Expansion (Priority: P2)

A candidate wants coverage beyond the existing sources, including remote job boards, official company career pages, and major platforms such as LinkedIn, Wellfound, Naukri, and Instahyre where public access is available. The system should discover public listings, avoid duplicate jobs, and identify when a platform can only be linked rather than crawled.

**Why this priority**: Better source breadth is required for the agent to be useful as an end-to-end job prospect assembler, but it must avoid brittle or non-compliant scraping.

**Independent Test**: Enable expanded live sources and verify that the result set includes multiple source families, no obvious duplicate jobs, and transparent statuses for inaccessible or link-only sources.

**Acceptance Scenarios**:

1. **Given** a supported public job source is available, **When** the user runs deep live search, **Then** the system extracts job title, company, location, description, source, and apply link from that source.
2. **Given** a source blocks automated access or requires authentication, **When** the user runs deep live search, **Then** the system marks that source as link-only or unavailable and does not replace real results with misleading fake listings.
3. **Given** the same role appears on multiple sources, **When** results are shown, **Then** the system displays one canonical result with a stable apply link rather than duplicate rows.

---

### User Story 3 - Resume-Based Filtering Continuity (Priority: P3)

A candidate selects a deep-search job and continues the same workflow: review fit, tailor the resume from the uploaded CV and selected job description, download the tailored resume, and draft personalized outreach.

**Why this priority**: Deep search is only valuable if it feeds the existing job-fit, tailoring, and messaging workflow with richer real job descriptions.

**Independent Test**: Select a deep-search result with an extracted description, tailor the resume, download the tailored output, and generate outreach drafts that reference the selected job and candidate background.

**Acceptance Scenarios**:

1. **Given** a deep-search job with an extracted description, **When** the user selects it and clicks Tailor Resume, **Then** the tailored resume uses that job description and the uploaded resume rather than a generic template.
2. **Given** the user selects a different deep-search job, **When** the selection changes, **Then** any previous tailored resume and outreach drafts reset for the new job.
3. **Given** a deep-search job lacks a full description, **When** the user requests tailoring, **Then** the system warns the user about limited job detail and still produces the best available draft from extracted metadata.

### Edge Cases

- Public search discovery returns links that are not job pages, expired postings, login pages, or duplicate aggregator pages.
- A source returns many irrelevant jobs because the target role contains broad terms such as "engineer".
- A site blocks automated access, returns a challenge page, or changes its page structure.
- Crawled descriptions contain cookie banners, navigation text, or unrelated job lists instead of a single job description.
- The search takes longer than expected, especially on hosted serverless infrastructure.
- The user selects a region where some sources have no relevant public coverage.
- The uploaded resume has low extraction confidence, limiting match quality.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a deep live search option in addition to the existing live and Adzuna search paths.
- **FR-002**: System MUST keep EU + UK as the default region while allowing the user to select India, United States, Australia, and Remote/Global.
- **FR-003**: System MUST discover role-specific public job pages using the selected role, region, remote preference, and visa preference.
- **FR-004**: System MUST extract title, company, location, source, apply link, posting date when available, job description, remote signal, and visa signal from each usable public job result.
- **FR-005**: System MUST crawl only publicly accessible pages and MUST represent inaccessible, authenticated, or blocked sources as unavailable or link-only rather than fabricated listings.
- **FR-006**: System MUST deduplicate jobs across sources using job identity, canonical link, company, title, and location signals.
- **FR-007**: System MUST rank and filter deep-search jobs against the uploaded resume using the existing fit evaluation workflow.
- **FR-008**: System MUST show source status messages that distinguish successful extraction, partial extraction, blocked access, unavailable provider credentials, and fallback behavior.
- **FR-009**: System MUST avoid seeded fallback jobs in deep live search unless the user explicitly enables examples or every live source fails and the result is clearly labelled as a fallback example.
- **FR-010**: System MUST preserve the selected-job workflow for tailoring resumes, drafting outreach, and downloading the tailored resume.
- **FR-011**: System MUST reset tailored resume and outreach drafts when the selected job changes.
- **FR-012**: System MUST complete typical deep live searches within the hosted app's practical execution limit by capping discovery and crawl volume while still returning partial useful results.

### Key Entities *(include if feature involves data)*

- **Deep Search Query**: The user's role, region, country set, remote preference, visa preference, and enabled source families.
- **Discovered Job Link**: A candidate public URL found from a search or source provider before the job details are extracted.
- **Crawled Job Page**: A fetched public page or provider detail response containing extracted job content and extraction confidence.
- **Canonical Job Result**: A deduplicated job posting with normalized job fields and a stable apply link.
- **Source Status**: A user-visible summary of what each source attempted and whether it produced, skipped, partially extracted, or failed results.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For three distinct role queries, at least 70% of the top 10 deep live results differ between any two queries when the same resume and region are used.
- **SC-002**: At least 80% of displayed deep live results include a non-empty job description or clear extracted summary long enough to support fit scoring.
- **SC-003**: Deep live search returns at least 15 non-seeded results for a common EU + UK software role when at least one public source is available.
- **SC-004**: Duplicate visible listings remain below 5% of displayed results during a representative multi-source search.
- **SC-005**: Users can select a deep-search job, generate a tailored resume, and download it without re-uploading the resume.
- **SC-006**: When a source is blocked or unavailable, the user sees a clear status message and the system still returns usable results from other available sources when possible.

## Assumptions

- The system will not bypass paywalls, login walls, captchas, robots restrictions, or platform protections.
- Major platforms that do not provide public crawlable job pages may be represented as search/apply links or omitted with a transparent status.
- Search volume will be bounded to keep the app responsive and suitable for hosted execution.
- Existing resume parsing, fit scoring, tailoring, and outreach behavior remains in scope and should receive richer job data from this feature.
- Optional search provider credentials may improve discovery breadth, but the feature should still provide value through public no-key job sources when those credentials are absent.
