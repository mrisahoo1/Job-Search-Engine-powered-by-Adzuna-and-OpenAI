# Contract: Search Response With Deep Source

The existing `POST /api/search` endpoint remains the only search endpoint.

## Request

```json
{
  "resumeText": "Senior software engineer resume...",
  "preferences": {
    "query": "generative ai engineer",
    "region": "eu_uk",
    "countries": ["Germany", "Netherlands", "United Kingdom"],
    "remoteOnly": false,
    "visaSponsorship": "preferred",
    "sources": ["deep", "official"],
    "officialCompanies": ["bmw", "stripe"],
    "searchMode": "live"
  }
}
```

## Response

```json
{
  "results": [
    {
      "job": {
        "id": "deep:example:123",
        "sourceId": "deep",
        "sourceName": "Deep Live Search",
        "title": "Generative AI Engineer",
        "company": "Example Company",
        "location": "Berlin, Germany",
        "country": "Germany",
        "remote": "yes",
        "visaSponsorship": "unknown",
        "description": "Extracted job description...",
        "tags": ["deep-search", "public-page"],
        "applyUrl": "https://example.com/jobs/123",
        "postedAt": "2026-05-27T00:00:00Z",
        "fetchedAt": "2026-05-27T00:00:00Z"
      },
      "evaluation": {
        "score": 82,
        "confidence": "high",
        "recommendation": "strong-fit",
        "matchedSkills": ["React", "Node.js"],
        "missingSkills": ["Kubernetes"],
        "strengths": ["Strong product engineering overlap"],
        "risks": ["Cloud evidence is lighter"],
        "signalNotes": ["Remote signal found"]
      }
    }
  ],
  "sourceStatuses": [
    {
      "sourceId": "deep",
      "status": "available",
      "message": "Deep search returned 24 jobs from public feeds; Brave discovery disabled because BRAVE_SEARCH_API_KEY is not configured."
    }
  ],
  "fetchedAt": "2026-05-27T00:00:00Z"
}
```

## Compatibility

- Existing clients can ignore the new `deep` source option.
- Existing tailoring and outreach endpoints continue to receive the selected `job` object without contract changes.
