# Research: Deep Live Job Search

## Decision: Do not rely on DuckDuckGo HTML scraping as the primary search provider

**Rationale**: The current job-search-bot diagnostic showed DuckDuckGo HTML returning a bot challenge instead of usable search results. DuckDuckGo's official help focuses on Instant Answers and direct site bangs, not a full server-side search results API suitable for this use case.

**Alternatives considered**: Direct DuckDuckGo HTML scraping, DuckDuckGo Instant Answer API, and site bangs. These are not reliable enough for deep job discovery.

## Decision: Use high-coverage public web discovery as the deep crawler entry point

**Rationale**: The crawler needs a real search-results source to discover public job URLs beyond curated feeds. Brave Search is the recommended first provider because it returns web URLs and snippets from an independent index with monthly free credits. Google Programmable Search can be used as a secondary optional provider when configured. Without a search API key, the crawler still uses public job feeds and ATS APIs, but broad web discovery will be narrower.

**Alternatives considered**: Google Programmable Search JSON API is documented but paid per 1,000 queries for server-side JSON and has quota constraints. SerpAPI/Serper are useful but add another paid or trial-based dependency.

## Decision: Keep no-key public job sources as the default working path

**Rationale**: The app must work without a new API key. Existing no-key sources such as Remotive and Arbeitnow provide public job data, and RemoteOK exposes public job JSON. The deep source should role-filter these feeds more strictly than the current live search and optionally crawl returned apply pages for richer descriptions.

**Alternatives considered**: Requiring a search API key before deep search runs. Rejected because the user asked for the best free path and the existing deployed app should remain usable out of the box.

## Decision: Treat protected job portals as link-only unless public pages are accessible

**Rationale**: LinkedIn, Naukri, Instahyre, and some Wellfound pages can require login, present bot checks, or restrict automated access. The feature should include discovered public links where available but should not bypass protections or pretend it extracted a full posting.

**Alternatives considered**: Authenticated scraping or browser automation. Rejected by the project constitution and reliability requirements.

## Decision: Add aggressive bounded crawling, extraction, dedupe, and source statuses inside the backend source layer

**Rationale**: The existing search pipeline already handles resume parsing, fit evaluation, and result sorting. Adding deep crawl discovery as a source keeps frontend changes small and preserves the existing tailoring/outreach flow.

**Alternatives considered**: A separate endpoint or background crawler. Rejected for this iteration because the user wants an interactive Vercel-hosted app and no new storage layer.
