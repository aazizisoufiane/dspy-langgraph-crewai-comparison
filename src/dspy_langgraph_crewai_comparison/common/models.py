from pydantic import BaseModel, Field


class CompanyFacts(BaseModel):
    """Structured output from the Researcher step."""

    company_name: str
    sector: str
    recent_news: list[str] = Field(description="3-5 recent news headlines with dates")
    financial_highlights: list[str] = Field(
        description="Key financial metrics or events"
    )
    key_events: list[str] = Field(description="Notable recent events")
    sources: list[str] = Field(description="URLs of sources used")


class AnalystSummary(BaseModel):
    """Structured output from the Writer step."""

    summary_text: str = Field(description="200-word max analyst summary")
    key_risks: list[str]
    outlook: str = Field(description="One sentence: bullish, bearish, or neutral")
    confidence_score: float = Field(ge=0, le=1)


class ClaimVerification(BaseModel):
    """One verified claim from the summary."""

    claim: str = Field(description="A factual claim made in the summary")
    source_url: str = Field(description="Source URL that should support this claim")
    supported: bool = Field(description="Does the source actually support the claim?")
    reasoning: str = Field(description="Why supported or not")


class ReviewResult(BaseModel):
    """What the LLM judge evaluates — no vague 0-10 scores."""

    claim_verifications: list[ClaimVerification]
    accuracy_ratio: float = Field(
        ge=0, le=1, description="verified_claims / total_claims"
    )
    expected_facets: list[str] = Field(
        description="Facets we expected (news, financials, risks, outlook, events)"
    )
    covered_facets: list[str] = Field(
        description="Facets actually present in the summary"
    )
    completeness_ratio: float = Field(
        ge=0, le=1, description="covered_facets / expected_facets"
    )
    conciseness_rating: int = Field(
        ge=1, le=5, description="1=verbose with filler, 5=every sentence adds value"
    )
    feedback: str
    issues: list[str]
    approved: bool


def structural_check(
    company_name: str,
    sector: str,
    recent_news: str,
    financial_highlights: str,
    key_events: str,
    sources: str,
) -> str:
    """Check the structure of CompanyFacts before finalizing.
    Pass each field as a string. Lists should be comma-separated items.
    Returns 'PASS' if all checks pass, or a description of issues found."""
    issues = []

    # Parse comma-separated strings into lists
    news_items = (
        [x.strip() for x in recent_news.split(",") if x.strip()] if recent_news else []
    )
    fin_items = (
        [x.strip() for x in financial_highlights.split(",") if x.strip()]
        if financial_highlights
        else []
    )
    event_items = (
        [x.strip() for x in key_events.split(",") if x.strip()] if key_events else []
    )
    source_items = (
        [x.strip() for x in sources.split(",") if x.strip()] if sources else []
    )

    if not company_name.strip():
        issues.append("company_name is empty")
    if not sector.strip():
        issues.append("sector is empty")
    if len(news_items) < 3:
        issues.append(f"Need at least 3 recent_news items, got {len(news_items)}")
    if len(fin_items) < 2:
        issues.append(f"Need at least 2 financial_highlights, got {len(fin_items)}")
    if len(event_items) < 1:
        issues.append(f"Need at least 1 key_event, got {len(event_items)}")
    if len(source_items) < 1:
        issues.append(f"Need at least 1 source URL, got {len(source_items)}")

    if issues:
        return "ISSUES FOUND: " + "; ".join(issues)
    return "PASS — all structural checks passed"
