# Data Model: Job Search and Curation Agent

## CandidateProfile

- `resumeText`: Raw resume or CV text provided by the user.
- `extractedSkills`: Normalized skills inferred from the resume.
- `experienceSignals`: Titles, domains, seniority clues, and achievements found in the resume.
- `targetTitles`: User-selected titles or inferred title preferences.
- `preferredCountries`: EU countries or region selections.
- `remotePreference`: Remote, hybrid, onsite, or any.
- `visaPreference`: Required, preferred, or any.

Validation:

- Resume text must contain enough content to extract at least one skill or experience signal before scoring is trusted.
- Preferences default to EU, remote preferred, and visa sponsorship preferred.

## SearchPreference

- `query`: Primary keyword or title search.
- `titles`: Optional list of desired titles.
- `countries`: EU countries to include.
- `region`: Active region, initially EU.
- `remoteOnly`: Whether to require remote signal.
- `visaSponsorship`: Whether to require or prefer sponsorship signal.
- `sources`: Enabled source identifiers.

Validation:

- Region defaults to EU and unsupported regions remain inactive until explicitly enabled.
- At least one source must be enabled for live search.

## JobSource

- `id`: Stable source key.
- `name`: Human-readable source name.
- `coverage`: Countries or region covered.
- `requiresCredential`: Whether the source needs a key or user authorization.
- `attribution`: Display requirement for source links.
- `limitations`: Known limits such as delayed listings or board-specific coverage.
- `status`: Available, degraded, disabled, or unsupported.

## JobPosting

- `id`: Stable normalized ID derived from source and source posting key.
- `sourceId`: Source that produced the job.
- `sourceName`: Display name.
- `title`: Job title.
- `company`: Hiring company.
- `location`: Location text.
- `country`: Normalized country where available.
- `remote`: Yes, no, or unknown.
- `visaSponsorship`: Yes, no, or unknown.
- `description`: Plain text job description.
- `tags`: Skills, categories, or labels from the source.
- `postedAt`: Publication date when available.
- `applyUrl`: Direct application or job-detail URL.
- `fetchedAt`: Fetch timestamp.

Validation:

- Title, company, source, and apply URL or detail URL are required for display.
- Unknown remote or visa signals must remain unknown rather than inferred as positive.

## FitEvaluation

- `jobId`: Evaluated job.
- `score`: 0 to 100 score.
- `confidence`: High, medium, or low.
- `recommendation`: Strong fit, possible fit, stretch, or low fit.
- `matchedSkills`: Evidence found in resume and job.
- `missingSkills`: Job requirements not found in resume.
- `strengths`: Human-readable reasons to apply.
- `risks`: Human-readable gaps or caveats.
- `signalNotes`: Remote and visa interpretation.

Validation:

- Every evaluation must include at least one reason or one caveat.
- Low-information resumes or job descriptions reduce confidence.

## ResumeDraft

- `id`: Stable draft ID.
- `jobId`: Selected job.
- `baseResumeText`: Source resume text.
- `draftText`: Tailored resume draft.
- `changeSummary`: User-readable list of changes.
- `warnings`: Gaps or unsupported claims that were not added.
- `createdAt`: Creation timestamp.

Validation:

- Draft must not introduce facts absent from the base resume or explicit user input.

## OutreachDraft

- `id`: Stable draft ID.
- `jobId`: Selected job.
- `channel`: LinkedIn, email, or short text.
- `targetPersona`: Recruiter, hiring manager, team lead, or employee referral.
- `contactHint`: Named contact or search guidance.
- `message`: Draft content.
- `reviewStatus`: Draft, copied, approved, or rejected.

Validation:

- Draft messages must reference the selected role and candidate value proposition.
- Named contacts require reliable source evidence; otherwise use persona/search-link guidance.

## Prospect

- `id`: Stable prospect ID.
- `job`: Saved job snapshot.
- `evaluation`: Last fit evaluation.
- `status`: New, reviewing, tailored, outreach drafted, applied, interviewing, rejected, archived.
- `notes`: User notes.
- `nextAction`: User-defined next step.
- `resumeDrafts`: Associated resume drafts.
- `outreachDrafts`: Associated outreach drafts.
- `history`: Timestamped status and note events.

Validation:

- Status changes append to history.
- Prospect saves should deduplicate by source and apply URL.
