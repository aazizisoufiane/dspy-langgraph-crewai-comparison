import dspy

from dspy_langgraph_crewai_comparison.common.models import (
    CompanyFacts,
    AnalystSummary,
    ReviewResult,
)


class ResearchCompany(dspy.Signature):
    """Research a public company and extract structured facts.

    You have access to tools: search, read_skill_instructions,
    read_reference, run_script, read_asset, check_structure.

    Start by reading the skill instructions to understand the research
    methodology, then use search and other tools as needed.
    Always check_structure before finalizing your output."""

    company_name: str = dspy.InputField(desc="Name of the company to research")
    skill_metadata: str = dspy.InputField(
        desc="Available skill metadata — read the skill instructions for full details"
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


class ReviewSummary(dspy.Signature):
    """Evaluate an analyst summary against the source facts.
    For each factual claim, verify it against sources.
    Check facet coverage (news, financials, risks, outlook, events).
    Rate conciseness 1-5. Approve if accuracy >= 0.8 and completeness >= 0.8."""

    analyst_summary: AnalystSummary = dspy.InputField(desc="The summary to evaluate")
    company_facts: CompanyFacts = dspy.InputField(desc="Source facts to verify against")
    review: ReviewResult = dspy.OutputField(
        desc="Detailed evaluation with claim verifications"
    )
