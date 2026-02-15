"""Skill loader following the Agent Skills spec (agentskills.io).

Uses skills-ref to parse frontmatter, then exposes tools for progressive
disclosure: the agent sees metadata at startup, reads SKILL.md body on
demand, and accesses references/scripts as needed."""

import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass, field
from loguru import logger

from skills_ref import read_properties, to_prompt, validate


@dataclass
class SkillTracker:
    """Tracks which parts of the skill the agent actually accessed."""

    skill_read: bool = False
    references_read: list[str] = field(default_factory=list)
    scripts_executed: list[str] = field(default_factory=list)
    tools_called: list[str] = field(default_factory=list)

    expected_references: list[str] = field(
        default_factory=lambda: [
            "output-schema.md",
            "search-strategies.md",
            "quality-checklist.md",
            "assets/sector-taxonomy.json",
        ]
    )
    expected_scripts: list[str] = field(
        default_factory=lambda: [
            "validate_sources.py",
        ]
    )
    expected_tools: list[str] = field(
        default_factory=lambda: [
            "check_structure",
        ]
    )

    def summary(self) -> dict:
        total_expected = (
            1  # skill_read
            + len(self.expected_references)
            + len(self.expected_scripts)
            + len(self.expected_tools)
        )
        total_accessed = (
            (1 if self.skill_read else 0)
            + len(self.references_read)
            + len(self.scripts_executed)
            + len(self.tools_called)
        )
        ref_missed = [
            r for r in self.expected_references if r not in self.references_read
        ]
        script_missed = [
            s for s in self.expected_scripts if s not in self.scripts_executed
        ]
        tool_missed = [t for t in self.expected_tools if t not in self.tools_called]

        return {
            "skill_read": self.skill_read,
            "references_read": self.references_read,
            "references_missed": ref_missed,
            "scripts_executed": self.scripts_executed,
            "scripts_missed": script_missed,
            "tools_called": self.tools_called,
            "tools_missed": tool_missed,
            "scores": {
                "skill_trigger": 1.0 if self.skill_read else 0.0,
                "reference_coverage": len(self.references_read)
                / len(self.expected_references)
                if self.expected_references
                else 1.0,
                "script_coverage": len(self.scripts_executed)
                / len(self.expected_scripts)
                if self.expected_scripts
                else 1.0,
                "tool_coverage": len(self.tools_called) / len(self.expected_tools)
                if self.expected_tools
                else 1.0,
                "overall": total_accessed / total_expected if total_expected else 1.0,
            },
        }


class SkillLoader:
    """Loads and serves an Agent Skill with progressive disclosure."""

    def __init__(self, skill_dir: str | Path):
        self.skill_dir = Path(skill_dir)
        self.skill_md_path = self.skill_dir / "SKILL.md"
        self.tracker = SkillTracker()

        if not self.skill_md_path.exists():
            raise FileNotFoundError(f"No SKILL.md found in {self.skill_dir}")

        errors = validate(self.skill_dir)
        if errors:
            logger.warning(f"Skill validation warnings: {errors}")

        self.properties = read_properties(self.skill_dir)
        logger.info(
            f"Loaded skill metadata: {self.properties.name} — "
            f"{self.properties.description[:80]}..."
        )

    def get_system_prompt_xml(self) -> str:
        """Generate <available_skills> XML for injection into system prompt."""
        return to_prompt([self.skill_dir])

    def get_metadata_prompt(self) -> str:
        """Lightweight text version for injection into DSPy signatures."""
        return (
            f"Available skill: {self.properties.name}\n"
            f"Description: {self.properties.description}\n"
            f"To use this skill, call read_skill_instructions() to load full instructions."
        )

    # — Tools exposed to the agent —

    def read_skill(self) -> str:
        """Tool: Read the full SKILL.md body (instructions)."""
        self.tracker.skill_read = True
        content = self.skill_md_path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) >= 3:
            body = parts[2].strip()
        else:
            body = content
        logger.info(f"Agent read skill: {self.properties.name}")
        return body

    def read_reference(self, name: str) -> str:
        """Tool: Read a reference file from references/ directory."""
        ref_path = self.skill_dir / "references" / name
        if not ref_path.exists():
            available = [f.name for f in (self.skill_dir / "references").glob("*")]
            return f"Reference '{name}' not found. Available: {available}"

        self.tracker.references_read.append(name)
        content = ref_path.read_text(encoding="utf-8")
        logger.info(f"Agent read reference: {name}")
        return content

    def run_script(self, name: str, input_data: str = "") -> str:
        """Tool: Execute a script from scripts/ directory.
        Only the output enters context — not the script code."""
        script_path = self.skill_dir / "scripts" / name
        if not script_path.exists():
            available = [f.name for f in (self.skill_dir / "scripts").glob("*.py")]
            return f"Script '{name}' not found. Available: {available}"

        self.tracker.scripts_executed.append(name)
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout.strip()
            if result.returncode != 0:
                output += f"\nSTDERR: {result.stderr.strip()}"
            logger.info(f"Agent executed script: {name}")
            return output
        except subprocess.TimeoutExpired:
            return f"Script '{name}' timed out after 30 seconds"

    def read_asset(self, name: str) -> str:
        """Tool: Read an asset file from assets/ directory."""
        asset_path = self.skill_dir / "assets" / name
        if not asset_path.exists():
            available = [f.name for f in (self.skill_dir / "assets").glob("*")]
            return f"Asset '{name}' not found. Available: {available}"

        self.tracker.references_read.append(f"assets/{name}")
        content = asset_path.read_text(encoding="utf-8")
        logger.info(f"Agent read asset: {name}")
        return content
