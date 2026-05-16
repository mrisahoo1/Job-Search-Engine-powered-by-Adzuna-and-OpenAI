# Contract: Search API

## POST /api/search

Searches enabled compliant job sources, normalizes results, evaluates fit, and returns source status.

### Request

```json
{
  "resumeText": "string",
  "preferences": {
    "query": "software engineer",
    "region": "EU",
    "countries": ["Germany", "Netherlands"],
    "remoteOnly": false,
    "visaSponsorship": "preferred",
    "sources": ["arbeitnow", "remotive"]
  }
}
```

### Response

```json
{
  "results": [
    {
      "job": {
        "id": "source:id",
        "sourceId": "arbeitnow",
        "sourceName": "Arbeitnow",
        "title": "Backend Engineer",
        "company": "Example GmbH",
        "location": "Berlin, Germany",
        "country": "Germany",
        "remote": "yes",
        "visaSponsorship": "unknown",
        "description": "Plain text description",
        "tags": ["TypeScript", "Node.js"],
        "postedAt": "2026-05-12T00:00:00.000Z",
        "applyUrl": "https://example.com/job",
        "fetchedAt": "2026-05-12T00:00:00.000Z"
      },
      "evaluation": {
        "score": 84,
        "confidence": "high",
        "recommendation": "strong-fit",
        "matchedSkills": ["TypeScript", "Node.js"],
        "missingSkills": ["AWS"],
        "strengths": ["Strong backend keyword overlap"],
        "risks": ["Cloud platform evidence missing"],
        "signalNotes": ["Remote signal found", "Visa sponsorship not stated"]
      }
    }
  ],
  "sourceStatuses": [
    {
      "sourceId": "arbeitnow",
      "status": "available",
      "message": "12 jobs returned"
    }
  ],
  "fetchedAt": "2026-05-12T00:00:00.000Z"
}
```

### Error Behavior

- Invalid or sparse resume: return 400 with a user-readable message.
- All sources unavailable: return 503 with source status details.
- Some sources unavailable: return 200 with partial results and degraded source statuses.
