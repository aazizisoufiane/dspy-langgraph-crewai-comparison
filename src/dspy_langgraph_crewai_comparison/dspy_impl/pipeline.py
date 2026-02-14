import dspy

from dspy_langgraph_crewai_comparison.common.tools import web_search
from dspy_langgraph_crewai_comparison.dspy_impl.signature import (
    ResearchCompany,
    WriteAnalystSummary,
    WriteAnalystSummaryWithFeedback,
    ReviewSummary,
)
from src.dspy_langgraph_crewai_comparison.common.models import structural_check

from loguru import logger


class CompanyResearchPipeline(dspy.Module):
    """Full pipeline: Research → Write → (structural check → Review → Rewrite loop)."""

    def __init__(self, max_iterations: int = 3):
        self.researcher = dspy.ChainOfThought(ResearchCompany)
        self.writer = dspy.ChainOfThought(WriteAnalystSummary)
        self.rewriter = dspy.ChainOfThought(WriteAnalystSummaryWithFeedback)
        self.reviewer = dspy.ChainOfThought(ReviewSummary)
        self.max_iterations = max_iterations

    def forward(self, company_name: str):
        # Step 1: Search + Research
        search_results = web_search(company_name)
        research_result = self.researcher(
            company_name=company_name,
            search_results=search_results,
        )
        facts = research_result.company_facts

        # Step 2: Write initial summary
        write_result = self.writer(company_facts=facts)
        summary = write_result.analyst_summary

        # Step 3: Review loop
        review = None
        for iteration in range(self.max_iterations):
            # Stage 1: Structural pre-check (free, no LLM)
            structural_issues = structural_check(summary, facts)
            if structural_issues:
                feedback = "Structural issues: " + "; ".join(structural_issues)
                logger.info(f"  [iter {iteration + 1}] Structural fail: {feedback}")
                rewrite_result = self.rewriter(
                    company_facts=facts,
                    previous_summary=summary.summary_text,
                    feedback=feedback,
                )
                summary = rewrite_result.analyst_summary
                continue

            # Stage 2: LLM judge (costs tokens, only if structural checks pass)
            review_result = self.reviewer(
                analyst_summary=summary,
                company_facts=facts,
            )
            review = review_result.review

            logger.info(
                f"  [iter {iteration + 1}] "
                f"accuracy={review.accuracy_ratio:.2f} "
                f"completeness={review.completeness_ratio:.2f} "
                f"conciseness={review.conciseness_rating}/5 "
                f"approved={review.approved}"
            )

            if review.approved:
                break

            # Not approved — rewrite with feedback
            feedback = review.feedback
            if review.issues:
                feedback += " Issues: " + "; ".join(review.issues)

            rewrite_result = self.rewriter(
                company_facts=facts,
                previous_summary=summary.summary_text,
                feedback=feedback,
            )
            summary = rewrite_result.analyst_summary

        return dspy.Prediction(
            company_facts=facts,
            analyst_summary=summary,
            review=review,
        )
