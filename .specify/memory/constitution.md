# Job Search Curation Agent Constitution

## Core Principles

### I. User-Controlled Career Automation
The system may collect, rank, tailor, and draft application materials, but it must not submit applications, send outreach, or impersonate the user without explicit user review and approval for each action.

### II. Source Compliance
Job sourcing must prefer official APIs, public feeds, public ATS endpoints, and user-provided source lists. The system must not bypass paywalls, authentication, robots restrictions, CAPTCHAs, or platform controls.

### III. Test-First Delivery
Behavioral code changes require tests first. Search, matching, ranking, resume tailoring, and outreach drafting must be covered by automated tests for normal and edge cases.

### IV. Explainable Matching
Every job fit score must include the visible reasons, missing evidence, visa/remote signal interpretation, and confidence level so the user can audit why a job was recommended.

### V. Privacy and Secrets Hygiene
Resume text, contact details, generated messages, and API keys are sensitive. The app must keep secrets out of client bundles, avoid logging sensitive user documents, and store only the minimum data needed for the workflow.

## Product Constraints
Initial region scope is Europe only, with architecture that supports adding more regions later. LinkedIn and other closed platforms are supported through user-provided links and message drafts, not automated scraping or unauthorized sending.

## Development Workflow
Use spec-kit artifacts as the source of truth: spec.md defines outcomes, plan.md defines architecture, tasks.md defines execution. Verification must include unit tests, build checks, and a deployability check before release.

## Governance
This constitution supersedes ad hoc implementation choices. Any exception must be documented in the feature plan with rationale, risk, and a mitigation.

**Version**: 1.0.0 | **Ratified**: 2026-05-12 | **Last Amended**: 2026-05-12
