# DSPy vs LangGraph vs CrewAI: Same Pipeline, Three Philosophies

A practitioner's comparison of three AI agent frameworks — not from docs, but from building the **same production pipeline** in all three.

**The pipeline:** A Company Research Agent that searches the web, extracts structured facts, writes an analyst summary, reviews it with an LLM judge, and loops back if quality isn't good enough.

## Pipeline Architecture
```
Input: "Apple"
  │
  ▼
web_search(mock) ──▶ Researcher ──▶ Writer ──▶ structural_check()
                     CompanyFacts    Summary         │
                                                fail │ pass
                                              ┌──────┤
                                              │      ▼
                                              │   Reviewer (LLM judge)
                                              │      │
                                              │  approved? ──yes──▶ Output
                                              │      │ no
                                              │      ▼
                                              └── Rewriter (with feedback)
                                                  (max 3 iterations)
```

**Two-stage evaluation:** `structural_check()` catches obvious failures (word count, missing fields) for free — the LLM judge only runs when structural checks pass. The judge verifies claims against sources, checks facet coverage, and rates conciseness. No vague 0-10 scores.

**What makes this different:**
- **MCP Integration** — each framework connected to real MCP servers, including [mcp-python-repl](https://pypi.org/project/mcp-python-repl/)
- **Agent Skills** — structured agent capabilities using the [Agent Skills](https://agentskills.io) spec, with scripts, references, and multi-file navigation
- **LLM-as-a-Judge** — decomposed evaluation: claim verification, facet coverage, source-grounded accuracy
- **DSPy GEPA optimization** — can prompt optimization fix the skill trigger reliability problem [Vercel identified](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)?

## Blog Series

| Part | Title | Status |
|------|-------|--------|
| 1 | [Same Pipeline, Three Philosophies](https://faunaris.ai/blog/dspy-langgraph-crewai-part1) | ✅ Published |
| 2 | Building the Same Pipeline, Three Ways | 🚧 In progress |
| 3 | MCP, Agent Skills & Dependency Audit | ⬜ Planned |
| 4 | Evaluation, Optimization & Verdict | ⬜ Planned |

## Project Structure
```
├── common/                  # Shared across all frameworks
│   ├── models.py            # Pydantic models (CompanyFacts, AnalystSummary, ReviewResult)
│   ├── tools.py             # Web search (mock → MCP in Part 3)
│   └── skills/              # Agent Skills (SKILL.md + scripts + references)
│       └── company-researcher/
│
├── dspy_impl/               # DSPy: "Define what, not how"
│   ├── signatures.py        # Typed input/output contracts
│   ├── pipeline.py          # Modules + review loop
│   └── run.py               # Entry point
│
├── langgraph_impl/          # LangGraph: "Draw your workflow"
│   ├── state.py
│   ├── nodes.py
│   ├── graph.py
│   └── run.py
│
└── crewai_impl/             # CrewAI: "Describe your team"
    ├── agents.yaml
    ├── tasks.yaml
    ├── crew.py
    └── run.py
```

## Quick Start
```bash
git clone https://github.com/aazizisoufiane/dspy-langgraph-crewai-comparison.git
cd dspy-langgraph-crewai-comparison

cp .env.example .env         # add your API key
uv sync                      # install dependencies

# Run any implementation
just dspy "Apple"
just langgraph "Apple"
just crewai "Apple"
just all "Apple"             # run all three
```

## Key Findings (Preview)

| Aspect | DSPy | LangGraph | CrewAI |
|--------|------|-----------|--------|
| Philosophy | Compile & optimize | Engineer & control | Configure & orchestrate |
| MCP integration | Manual wrapper | Ecosystem adapters | Native |
| Skill trigger reliability | Optimizable (GEPA) | Manual prompt tweaking | Manual backstory tweaking |
| LLM-as-a-Judge | First-class module | Manual node + prompt | Agent with reviewer role |
| Prompt optimization | Built-in | None | None |

Full analysis in the [blog series](https://faunaris.ai/blog/dspy-langgraph-crewai-part1).

## Author

**Soufiane Aazizi** — Lead AI Engineer | [Faunaris AI](https://faunaris.ai)

12+ years in quantitative finance and AI engineering. Building production LLM systems across pharma, banking, and audit.

## License

MIT