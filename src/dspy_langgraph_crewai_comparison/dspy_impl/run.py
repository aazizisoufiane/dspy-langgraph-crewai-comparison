"""Run the DSPy Company Research Pipeline.

Usage:
    python -m dspy_impl.run                    # defaults to Apple
    python -m dspy_impl.run "Tesla"
    python -m dspy_impl.run "Nvidia"
"""

import sys
import dspy
from loguru import logger

from dspy_langgraph_crewai_comparison.common.workspace import Workspace
from dspy_langgraph_crewai_comparison.dspy_impl.pipeline import CompanyResearchPipeline


def configure_lm(cache: bool = True):
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
            "Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or VERTEX_PROJECT_ID."
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
    pipeline = CompanyResearchPipeline(workspace=ws)

    logger.info(f"Researching {company}...")
    result = pipeline(company_name=company)

    facts = result.company_facts
    summary = result.analyst_summary
    review = result.review
    tracker = result.skill_tracker
    scores = tracker["scores"]

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

    logger.info(f"\n{'─' * 60}")
    logger.info("REVIEW")
    logger.info(f"{'─' * 60}")
    logger.info(f"Accuracy:     {review.accuracy_ratio:.0%}")
    logger.info(f"Completeness: {review.completeness_ratio:.0%}")
    logger.info(f"Conciseness:  {review.conciseness_rating}/5")
    logger.info(f"Approved:     {'✓' if review.approved else '✗'}")
    if review.issues:
        logger.info(f"Issues:       {'; '.join(review.issues)}")

    logger.info(f"\n{'─' * 60}")
    logger.info("SKILL TRACKING")
    logger.info(f"{'─' * 60}")
    logger.info(f"Skill read:          {'✓' if tracker['skill_read'] else '✗'}")
    logger.info(
        f"References read:     {', '.join(tracker['references_read']) or 'none'}"
    )
    logger.info(
        f"References missed:   {', '.join(tracker['references_missed']) or 'none'}"
    )
    logger.info(
        f"Scripts executed:     {', '.join(tracker['scripts_executed']) or 'none'}"
    )
    logger.info(
        f"Scripts missed:       {', '.join(tracker['scripts_missed']) or 'none'}"
    )
    logger.info(f"Tools called:        {', '.join(tracker['tools_called']) or 'none'}")
    logger.info(f"Tools missed:        {', '.join(tracker['tools_missed']) or 'none'}")

    logger.info(f"\n{'─' * 60}")
    logger.info("SCORES")
    logger.info(f"{'─' * 60}")
    logger.info(f"Skill trigger:       {scores['skill_trigger']:.0%}")
    logger.info(f"Reference coverage:  {scores['reference_coverage']:.0%}")
    logger.info(f"Script coverage:     {scores['script_coverage']:.0%}")
    logger.info(f"Tool coverage:       {scores['tool_coverage']:.0%}")
    logger.info(f"Overall:             {scores['overall']:.0%}")

    logger.info(f"\n{'=' * 60}")
    logger.info("Done.")


if __name__ == "__main__":
    main()
