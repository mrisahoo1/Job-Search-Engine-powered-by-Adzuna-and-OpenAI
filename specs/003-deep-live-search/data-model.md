# Data Model: Deep Live Job Search

## DeepSearchQuery

- `query`: Target role entered by the user.
- `region`: Selected region identifier.
- `countries`: Concrete country filters derived from region or user selection.
- `remote_only`: Whether only remote jobs should be returned.
- `visa_sponsorship`: User's visa preference.
- `sources`: Enabled source identifiers, including `deep`.
- `official_companies`: Selected official company boards.

## DiscoveredJobLink

- `url`: Public URL discovered from a search provider or source feed.
- `title`: Search/provider title.
- `description`: Search/provider snippet.
- `source_name`: Human-readable source label.
- `source_id`: Source identifier.
- `link_only`: True when the page should not be crawled or cannot be crawled.

## CrawledJobPage

- `url`: Fetched public page URL.
- `title`: Extracted page or posting title.
- `company`: Extracted hiring organization where available.
- `location`: Extracted location where available.
- `description`: Extracted posting text or summary.
- `posted_at`: Posting date where available.
- `confidence`: High for structured job posting data, medium for page text extraction, low for snippet-only results.

## CanonicalJobResult

Uses the existing `JobPosting` shape:

- `id`, `source_id`, `source_name`
- `title`, `company`, `location`, `country`
- `remote`, `visa_sponsorship`
- `description`, `tags`, `posted_at`, `apply_url`, `fetched_at`

## SourceStatus

Uses the existing `SourceStatus` shape:

- `source_id`
- `status`: available, degraded, disabled, or unsupported
- `message`: User-visible source summary including partial extraction and credential status
