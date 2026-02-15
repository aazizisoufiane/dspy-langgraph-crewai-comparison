# CompanyFacts Output Schema

The researcher must return a `CompanyFacts` object with all fields populated.

## Required fields

| Field | Type | Rules |
|-------|------|-------|
| company_name | str | Official name (e.g., "Apple Inc.", not "apple") |
| sector | str | Must match a value from `assets/sector-taxonomy.json` |
| recent_news | list[str] | 3-5 items, each with a date in parentheses |
| financial_highlights | list[str] | 2+ items with specific numbers (revenue, margins, etc.) |
| key_events | list[str] | 1+ notable events (launches, acquisitions, leadership changes) |
| sources | list[str] | Valid URLs, one per fact minimum |

## Format rules
- News items: "{headline} ({date})" — e.g., "Apple reports Q1 revenue of $124.3B (Jan 30, 2026)"
- Financial highlights: include YoY comparison when available
- Sources: full URLs, no shortened links