"""Run the DSPy Company Research Pipeline.

Usage:
    python -m dspy_impl.run                    # defaults to Apple
    python -m dspy_impl.run "Tesla"
    python -m dspy_impl.run "Nvidia"

Requires ANTHROPIC_API_KEY or OPENAI_API_KEY in environment.
"""

import sys
import dspy

from dspy_langgraph_crewai_comparison.common.workspace import Workspace
from src.dspy_langgraph_crewai_comparison.dspy_impl.pipeline import (
    CompanyResearchPipeline,
)
from loguru import logger


def configure_lm(cache: bool = True):
    """Configure DSPy language model. Tries Anthropic first, then OpenAI."""
    import os

    if os.getenv("ANTHROPIC_API_KEY"):
        lm = dspy.LM("anthropic/claude-sonnet-4-20250514", cache=cache, max_tokens=4096)
        logger.info("Using: Claude Sonnet 4")
    elif os.getenv("OPENAI_API_KEY"):
        lm = dspy.LM("openai/gpt-4o", cache=cache, max_tokens=4096)
        logger.info("Using: GPT-4o")
    elif os.getenv("VERTEX_PROJECT_ID"):
        lm = dspy.LM(
            model="vertex_ai/gemini-2.5-pro",
            cache=cache,
            max_tokens=None,
            vertex_ai_location=os.getenv("VERTEX_LOCATION", ""),
            project=os.getenv("VERTEX_PROJECT_ID", ""),
        )
        logger.info("Using: Vertex AI Gemini")

    else:
        raise EnvironmentError(
            "Set ANTHROPIC_API_KEY or OPENAI_API_KEY in your environment."
        )
    dspy.configure(lm=lm)


def main():
    company = sys.argv[1] if len(sys.argv) > 1 else "Apple"

    logger.info(f"\n{'=' * 60}")
    logger.info("  Company Research Pipeline (DSPy)")
    logger.info(f"  Target: {company}")
    logger.info(f"{'=' * 60}\n")

    configure_lm()
    ws = Workspace()
    pipeline = CompanyResearchPipeline(max_iterations=3, workspace=ws)

    logger.info(f"[1/3] Researching {company}...")
    result = pipeline(company_name=company)

    # Display results
    facts = result.company_facts
    summary = result.analyst_summary
    review = result.review

    logger.info(f"\n{'─' * 60}")
    logger.info("COMPANY FACTS")
    logger.info(f"{'─' * 60}")
    logger.info(f"Company: {facts.company_name}")
    logger.info(f"Sector:  {facts.sector}")
    logger.info(f"News:    {len(facts.recent_news)} items")
    logger.info(f"Sources: {len(facts.sources)} URLs")

    logger.info(f"\n{'─' * 60}")
    logger.info("ANALYST SUMMARY")
    logger.info(f"{'─' * 60}")
    logger.info(summary.summary_text)
    logger.info(f"\nRisks:      {', '.join(summary.key_risks)}")
    logger.info(f"Outlook:    {summary.outlook}")
    logger.info(f"Confidence: {summary.confidence_score:.0%}")

    if review:
        logger.info(f"\n{'─' * 60}")
        logger.info("REVIEW")
        logger.info(f"{'─' * 60}")
        logger.info(f"Accuracy:     {review.accuracy_ratio:.0%}")
        logger.info(f"Completeness: {review.completeness_ratio:.0%}")
        logger.info(f"Conciseness:  {review.conciseness_rating}/5")
        logger.info(f"Approved:     {'✓' if review.approved else '✗'}")
        if review.issues:
            logger.info(f"Issues:       {'; '.join(review.issues)}")

    logger.info(f"\n{'=' * 60}")
    logger.info("Done.")


if __name__ == "__main__":
    main()
