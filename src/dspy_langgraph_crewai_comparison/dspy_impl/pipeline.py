from pathlib import Path

import dspy
from loguru import logger

from dspy_langgraph_crewai_comparison.common.models import structural_check
from dspy_langgraph_crewai_comparison.common.skill_loader import SkillLoader
from dspy_langgraph_crewai_comparison.common.tools import web_search
from dspy_langgraph_crewai_comparison.common.workspace import Workspace
from dspy_langgraph_crewai_comparison.dspy_impl.signature import (
    ResearchCompany,
    WriteAnalystSummary,
    ReviewSummary,
)

SKILL_DIR = Path(__file__).parent.parent / "common" / "skills" / "company-researcher"


def make_skill_tools(skill: SkillLoader):
    """Create tool functions for the ReAct researcher agent."""

    def search(query: str) -> str:
        """Search the web for company information."""
        return web_search(query)

    def read_skill_instructions() -> str:
        """Read the full SKILL.md instructions for the company-researcher skill.
        Call this first to understand how to research a company properly."""
        return skill.read_skill()

    def read_reference(name: str) -> str:
        """Read a reference document from the skill.
        Available: output-schema.md, search-strategies.md, quality-checklist.md"""
        return skill.read_reference(name)

    def run_script(name: str, input_data: str) -> str:
        """Execute a skill script and get its output.
        Available: validate_sources.py
        Pass input as a JSON array of URLs."""
        return skill.run_script(name, input_data)

    def read_asset(name: str) -> str:
        """Read an asset file from the skill.
        Available: sector-taxonomy.json"""
        return skill.read_asset(name)

    def check_structure(
        company_name: str,
        sector: str,
        recent_news: str,
        financial_highlights: str,
        key_events: str,
        sources: str,
    ) -> str:
        """Check the structure of your CompanyFacts before finalizing.
        Pass each field as a string. Lists should be comma-separated items.
        Returns 'PASS' if OK, or describes issues to fix."""
        skill.tracker.tools_called.append("check_structure")
        return structural_check(
            company_name, sector, recent_news, financial_highlights, key_events, sources
        )

    return [
        search,
        read_skill_instructions,
        read_reference,
        run_script,
        read_asset,
        check_structure,
    ]


class CompanyResearchPipeline(dspy.Module):
    """Prompt chain pattern (Anthropic style):
      Researcher (ReAct, agentic) → Writer (CoT) → Reviewer (CoT)

    No review loop — the Researcher self-checks via tools.
    Reviewer provides evaluation data for GEPA optimization in Part 4.
    """

    def __init__(self, max_iterations: int = 3, workspace: Workspace | None = None):
        self.skill = SkillLoader(SKILL_DIR)

        # Researcher: ReAct agent with all tools (agentic)
        self.researcher = dspy.ReAct(
            ResearchCompany,
            tools=make_skill_tools(self.skill),
            max_iters=10,
        )

        # Writer & Reviewer: ChainOfThought (not agentic)
        self.writer = dspy.ChainOfThought(WriteAnalystSummary)
        self.reviewer = dspy.ChainOfThought(ReviewSummary)

        self.ws = workspace

    def _dump(self, name: str, data):
        if self.ws:
            payload = data.model_dump() if hasattr(data, "model_dump") else data
            self.ws.dump(name, payload)

    def forward(self, company_name: str):
        # — Step 1: Researcher (agentic) —
        skill_metadata = self.skill.get_metadata_prompt()

        research_result = self.researcher(
            company_name=company_name,
            skill_metadata=skill_metadata,
        )
        facts = research_result.company_facts
        self._dump("01_company_facts", facts)
        self._dump("01b_skill_tracker", self.skill.tracker.summary())

        # — Step 2: Writer —
        write_result = self.writer(company_facts=facts)
        summary = write_result.analyst_summary
        self._dump("02_summary", summary)

        # — Step 3: Reviewer (evaluation data for Part 4) —
        review_result = self.reviewer(
            analyst_summary=summary,
            company_facts=facts,
        )
        review = review_result.review
        self._dump("03_review", review)

        logger.info(
            f"Review: accuracy={review.accuracy_ratio:.2f} "
            f"completeness={review.completeness_ratio:.2f} "
            f"conciseness={review.conciseness_rating}/5 "
            f"approved={review.approved}"
        )

        # — Final output —
        self._dump(
            "04_final_output",
            {
                "company_facts": facts.model_dump(),
                "analyst_summary": summary.model_dump(),
                "review": review.model_dump(),
                "skill_tracker": self.skill.tracker.summary(),
            },
        )

        return dspy.Prediction(
            company_facts=facts,
            analyst_summary=summary,
            review=review,
            skill_tracker=self.skill.tracker.summary(),
        )
