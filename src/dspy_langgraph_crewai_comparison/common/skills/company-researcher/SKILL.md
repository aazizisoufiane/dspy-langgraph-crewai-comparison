---
name: company-researcher
description: >
  Researches a public company using web search and extracts structured
  financial facts with source attribution. Use when given a company name
  and asked to produce a CompanyFacts report with recent news, financial
  highlights, key events, and verified source URLs.
metadata:
  author: faunaris-ai
  version: "2.0"
allowed-tools: web_search execute_python
---

# Company Researcher

## Goal
Produce a CompanyFacts report for a given company: recent news, financial
highlights, key events, and verified source URLs.

## Workflow
1. Classify the company sector
2. Search for recent news (past 30 days), financial highlights, and key events
3. Validate your source URLs
4. Check your output structure before finalizing

## Resources
Consult these when needed — don't load them all upfront:

- **[sector-taxonomy.json](assets/sector-taxonomy.json)** — official sector
  classifications. Consult when assigning a sector.
- **[search-strategies.md](references/search-strategies.md)** — sector-specific
  search queries. Consult if your initial search returns poor results.
- **[output-schema.md](references/output-schema.md)** — full CompanyFacts
  spec with field rules. Consult if unsure about required fields or format.
- **[quality-checklist.md](references/quality-checklist.md)** — quality
  criteria. Consult before finalizing to catch common issues.
- **[validate_sources.py](scripts/validate_sources.py)** — URL validator.
  Run when you have collected your sources.
- **check_structure** tool — structural validator. Run when you think you're done.