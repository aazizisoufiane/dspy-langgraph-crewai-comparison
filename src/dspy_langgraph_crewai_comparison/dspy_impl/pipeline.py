import dspy
from loguru import logger

from dspy_langgraph_crewai_comparison.common.models import structural_check
from dspy_langgraph_crewai_comparison.common.tools import web_search
from dspy_langgraph_crewai_comparison.common.workspace import Workspace
from dspy_langgraph_crewai_comparison.dspy_impl.signature import (
    ResearchCompany,
    WriteAnalystSummary,
    WriteAnalystSummaryWithFeedback,
    ReviewSummary,
)


class CompanyResearchPipeline(dspy.Module):
    """Full pipeline: Research → Write → (structural check → Review → Rewrite loop)."""

    def __init__(self, max_iterations: int = 3, workspace: Workspace | None = None):
        self.researcher = dspy.ChainOfThought(ResearchCompany)
        self.writer = dspy.ChainOfThought(WriteAnalystSummary)
        self.rewriter = dspy.ChainOfThought(WriteAnalystSummaryWithFeedback)
        self.reviewer = dspy.ChainOfThought(ReviewSummary)
        self.max_iterations = max_iterations
        self.ws = workspace

    def _dump(self, name: str, data):
        """Dump to workspace if available."""
        if self.ws:
            payload = data.model_dump() if hasattr(data, "model_dump") else data
            self.ws.dump(name, payload)

    def forward(self, company_name: str):
        # Step 1: Search + Research
        search_results = web_search(company_name)
        self._dump(
            "01_search_results", {"query": company_name, "results": search_results}
        )

        research_result = self.researcher(
            company_name=company_name,
            search_results=search_results,
        )
        facts = research_result.company_facts
        self._dump("02_company_facts", facts)

        # Step 2: Write initial summary
        write_result = self.writer(company_facts=facts)
        summary = write_result.analyst_summary
        self._dump("03_summary_v0", summary)

        # Step 3: Review loop
        review = None
        for iteration in range(self.max_iterations):
            # Stage 1: Structural pre-check (free, no LLM)
            structural_issues = structural_check(summary, facts)
            if structural_issues:
                feedback = "Structural issues: " + "; ".join(structural_issues)
                logger.info(f"  [iter {iteration + 1}] Structural fail: {feedback}")
                self._dump(
                    f"04_structural_fail_iter{iteration + 1}",
                    {
                        "issues": structural_issues,
                        "feedback": feedback,
                    },
                )
                rewrite_result = self.rewriter(
                    company_facts=facts,
                    previous_summary=summary.summary_text,
                    feedback=feedback,
                )
                summary = rewrite_result.analyst_summary
                self._dump(f"05_summary_v{iteration + 1}", summary)
                continue

            # Stage 2: LLM judge (costs tokens, only if structural checks pass)
            review_result = self.reviewer(
                analyst_summary=summary,
                company_facts=facts,
            )
            review = review_result.review
            self._dump(f"06_review_iter{iteration + 1}", review)

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
            self._dump(f"05_summary_v{iteration + 1}", summary)

        # Final dump
        self._dump(
            "07_final_output",
            {
                "company_facts": facts.model_dump()
                if hasattr(facts, "model_dump")
                else facts,
                "analyst_summary": summary.model_dump()
                if hasattr(summary, "model_dump")
                else summary,
                "review": review.model_dump()
                if hasattr(review, "model_dump") and review
                else None,
            },
        )

        return dspy.Prediction(
            company_facts=facts,
            analyst_summary=summary,
            review=review,
        )
