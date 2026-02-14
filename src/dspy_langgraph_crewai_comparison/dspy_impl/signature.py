import dspy

from dspy_langgraph_crewai_comparison.common.models import (
    CompanyFacts,
    AnalystSummary,
    ReviewResult,
)


class ResearchCompany(dspy.Signature):
    """Research a public company using web search results and extract
    structured facts with source attribution. Return recent news,
    financial highlights, key events, and source URLs."""

    company_name: str = dspy.InputField(desc="Name of the company to research")
    search_results: str = dspy.InputField(
        desc="Raw web search results to extract facts from"
    )
    company_facts: CompanyFacts = dspy.OutputField(
        desc="Structured company research facts"
    )


class WriteAnalystSummary(dspy.Signature):
    """Write a concise analyst-style summary from researched company facts.
    Maximum 200 words. Every claim must trace back to a source.
    Include key risks and a one-sentence outlook (bullish/bearish/neutral)."""

    company_facts: CompanyFacts = dspy.InputField(
        desc="Structured facts from the researcher"
    )
    analyst_summary: AnalystSummary = dspy.OutputField(desc="Concise analyst summary")


class WriteAnalystSummaryWithFeedback(dspy.Signature):
    """Rewrite an analyst summary incorporating reviewer feedback.
    Fix the specific issues raised. Maximum 200 words."""

    company_facts: CompanyFacts = dspy.InputField(
        desc="Structured facts from the researcher"
    )
    previous_summary: str = dspy.InputField(
        desc="The previous summary that needs improvement"
    )
    feedback: str = dspy.InputField(desc="Specific feedback from the reviewer")
    analyst_summary: AnalystSummary = dspy.OutputField(desc="Improved analyst summary")


class ReviewSummary(dspy.Signature):
    """Evaluate an analyst summary against the source facts.
    For each factual claim in the summary, verify it against the sources.
    Check which expected facets are covered (news, financials, risks, outlook, events).
    Rate conciseness from 1 (verbose) to 5 (tight).
    Approve only if accuracy_ratio >= 0.8 and completeness_ratio >= 0.8."""

    analyst_summary: AnalystSummary = dspy.InputField(desc="The summary to evaluate")
    company_facts: CompanyFacts = dspy.InputField(desc="Source facts to verify against")
    review: ReviewResult = dspy.OutputField(
        desc="Detailed evaluation with claim verifications"
    )
