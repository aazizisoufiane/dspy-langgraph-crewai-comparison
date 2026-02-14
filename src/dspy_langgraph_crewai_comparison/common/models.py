from pydantic import BaseModel, Field


# ── Pipeline data models ─────────────────────────────────

class CompanyFacts(BaseModel):
    """Structured output from the Researcher step."""
    company_name: str
    sector: str
    recent_news: list[str] = Field(
        description="3-5 recent news headlines with dates"
    )
    financial_highlights: list[str] = Field(
        description="Key financial metrics or events"
    )
    key_events: list[str] = Field(
        description="Notable recent events"
    )
    sources: list[str] = Field(
        description="URLs of sources used"
    )


class AnalystSummary(BaseModel):
    """Structured output from the Writer step."""
    summary_text: str = Field(description="200-word max analyst summary")
    key_risks: list[str]
    outlook: str = Field(
        description="One sentence: bullish, bearish, or neutral"
    )
    confidence_score: float = Field(ge=0, le=1)


# ── Pre-validation gate (no LLM needed) ──────────────────

def structural_check(summary: AnalystSummary, facts: CompanyFacts) -> list[str]:
    """Cheap checks before calling the LLM judge.
    Returns a list of issues. Empty list = pass."""
    issues = []
    word_count = len(summary.summary_text.split())
    if word_count > 200:
        issues.append(f"Summary too long: {word_count} words (max 200)")
    if not summary.key_risks:
        issues.append("Missing key_risks")
    if not summary.outlook:
        issues.append("Missing outlook")
    if not facts.sources:
        issues.append("No sources provided by researcher")
    return issues


# ── LLM judge models ─────────────────────────────────────

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
        ge=0, le=1,
        description="verified_claims / total_claims"
    )
    expected_facets: list[str] = Field(
        description="Facets we expected (news, financials, risks, outlook, events)"
    )
    covered_facets: list[str] = Field(
        description="Facets actually present in the summary"
    )
    completeness_ratio: float = Field(
        ge=0, le=1,
        description="covered_facets / expected_facets"
    )
    conciseness_rating: int = Field(
        ge=1, le=5,
        description="1=verbose with filler, 5=every sentence adds value"
    )
    feedback: str
    issues: list[str]
    approved: bool