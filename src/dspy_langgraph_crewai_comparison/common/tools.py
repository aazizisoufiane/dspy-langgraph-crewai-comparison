"""Mock web search tool for prototyping.
Returns different quality results based on query specificity.
Will be replaced by MCP servers in Part 3.

Query tiers:
- Vague query ("Apple") → news only, no financials
- Targeted query ("Apple quarterly earnings") → full results
- Sector-specific query from search-strategies.md → full results + bonus
- Bad source included to test validate_sources.py
"""

MOCK_DATA = {
    "apple": {
        "news": [
            "Apple reports Q1 2026 revenue of $124.3B, beating estimates by 4% (Jan 30, 2026)",
            "Apple Intelligence rollout expands to 15 new languages across EU markets (Feb 3, 2026)",
            "Apple Vision Pro 2 rumored for WWDC 2026 with M4 chip and lighter design (Feb 10, 2026)",
            "Apple acquires UK-based AI startup for $200M to bolster on-device ML (Jan 22, 2026)",
        ],
        "financials": [
            "Q1 2026 revenue: $124.3B (+8% YoY)",
            "Services revenue: $26.3B (+14% YoY), new all-time high",
            "Gross margin: 46.9%, up from 45.9% year-ago quarter",
            "iPhone revenue: $71.4B (+6% YoY), driven by iPhone 16 Pro demand",
        ],
        "events": [
            "Expanded Apple Intelligence to EU with on-device processing focus",
            "Opened new R&D center in Munich focused on wireless chip design",
            "Announced $110B share buyback program, largest in corporate history",
        ],
        "sources_good": [
            "https://investor.apple.com/quarterly-results/2026-q1",
            "https://www.reuters.com/technology/apple-q1-2026-earnings",
            "https://www.bloomberg.com/news/apple-intelligence-eu-expansion",
        ],
        "sources_bad": [
            "not-a-valid-url",
        ],
        "bonus": [
            "R&D spending: $7.8B in Q1 2026, up 11% YoY",
            "App Store developer payouts exceeded $100B cumulative in 2025",
        ],
        "sector": "Technology",
        "keywords_targeted": ["earnings", "quarterly", "revenue", "financial"],
        "keywords_sector": ["AI strategy", "product launch", "R&D spending"],
    },
    "tesla": {
        "news": [
            "Tesla delivers 495,000 vehicles in Q4 2025, missing estimates by 3% (Jan 5, 2026)",
            "Tesla Semi begins volume production at Giga Nevada (Jan 18, 2026)",
            "Elon Musk confirms FSD v13 achieving 99.99% intervention-free miles (Feb 7, 2026)",
            "Tesla Energy division posts $3.2B quarterly revenue, up 67% YoY (Jan 29, 2026)",
        ],
        "financials": [
            "Q4 2025 revenue: $27.1B (+12% YoY)",
            "Automotive gross margin: 18.2%, recovering from 2024 lows",
            "Energy generation and storage revenue: $3.2B (+67% YoY)",
            "Free cash flow: $2.8B, driven by energy storage deployments",
        ],
        "events": [
            "Robotaxi pilot program launched in Austin, TX with 200 vehicles",
            "Optimus humanoid robot demo at shareholder meeting — walking and sorting tasks",
            "Giga Mexico construction resumed after regulatory approval",
        ],
        "sources_good": [
            "https://ir.tesla.com/quarterly-results/2025-q4",
            "https://www.reuters.com/business/autos/tesla-q4-deliveries",
            "https://www.bloomberg.com/news/tesla-semi-volume-production",
        ],
        "sources_bad": [
            "htp://electrek.co/broken-link",
        ],
        "bonus": [
            "Supercharger network: 65,000+ stalls globally, up 30% YoY",
            "Tesla Insurance now available in 14 states",
        ],
        "sector": "Automotive / Energy",
        "keywords_targeted": [
            "earnings",
            "quarterly",
            "revenue",
            "delivery",
            "deliveries",
        ],
        "keywords_sector": ["production capacity", "delivery numbers", "regulatory"],
    },
    "nvidia": {
        "news": [
            "Nvidia reports Q4 FY2026 revenue of $44.2B, data center up 85% YoY (Feb 12, 2026)",
            "Nvidia announces Blackwell Ultra B300 GPU at GTC 2026 (Feb 5, 2026)",
            "Nvidia partners with Saudi Arabia's NEOM for $5B AI infrastructure deal (Jan 25, 2026)",
            "US tightens AI chip export controls; Nvidia expects $1.5B revenue impact (Feb 1, 2026)",
        ],
        "financials": [
            "Q4 FY2026 revenue: $44.2B (+65% YoY)",
            "Data center revenue: $39.1B (+85% YoY)",
            "Gross margin: 73.8%, slight compression from Blackwell ramp costs",
            "Full FY2026 revenue: $158B, surpassing all analyst estimates",
        ],
        "events": [
            "Blackwell Ultra B300 announced — 2x inference throughput vs B200",
            "Expanded sovereign AI partnerships: Saudi Arabia, UAE, India, France",
            "Jensen Huang keynote at GTC 2026 — 'physical AI' and robotics roadmap",
        ],
        "sources_good": [
            "https://investor.nvidia.com/quarterly-results/fy2026-q4",
            "https://www.reuters.com/technology/nvidia-q4-fy2026-earnings",
            "https://www.bloomberg.com/news/nvidia-blackwell-ultra-announcement",
        ],
        "sources_bad": [
            "www.cnbc.com/nvidia-export-controls",
        ],
        "bonus": [
            "CUDA developer ecosystem: 5M+ developers worldwide",
            "Nvidia DGX Cloud partnerships with AWS, Azure, and GCP",
        ],
        "sector": "Technology / Semiconductors",
        "keywords_targeted": ["earnings", "quarterly", "revenue", "data center"],
        "keywords_sector": ["GPU announcement", "chip export", "data center revenue"],
    },
}


def _query_tier(query_lower: str, data: dict) -> str:
    """Determine query quality: 'vague', 'targeted', or 'sector'."""
    for kw in data["keywords_sector"]:
        if kw.lower() in query_lower:
            return "sector"
    for kw in data["keywords_targeted"]:
        if kw.lower() in query_lower:
            return "targeted"
    return "vague"


def web_search(query: str) -> str:
    """Mock web search with query-quality sensitivity.

    - Vague queries → news only, no financials, includes bad source
    - Targeted queries → news + financials + events, includes bad source
    - Sector-specific queries → full results + bonus data, clean sources

    In Part 3, this will be replaced by a real MCP web_search tool."""
    query_lower = query.lower()

    for company, data in MOCK_DATA.items():
        if company in query_lower:
            tier = _query_tier(query_lower, data)
            results = []

            # --- News: always returned ---
            results.append(f"=== Recent News for {company.title()} ===")
            for item in data["news"]:
                results.append(f"- {item}")

            # --- Financials: only for targeted/sector ---
            if tier in ("targeted", "sector"):
                results.append("\n=== Financial Highlights ===")
                for item in data["financials"]:
                    results.append(f"- {item}")

            # --- Events: only for targeted/sector ---
            if tier in ("targeted", "sector"):
                results.append("\n=== Key Events ===")
                for item in data["events"]:
                    results.append(f"- {item}")

            # --- Bonus: only for sector-specific queries ---
            if tier == "sector":
                results.append("\n=== Additional Insights ===")
                for item in data["bonus"]:
                    results.append(f"- {item}")

            # --- Sources: bad source included for vague/targeted ---
            results.append("\n=== Sources ===")
            for url in data["sources_good"]:
                results.append(f"- {url}")
            if tier != "sector":
                for url in data["sources_bad"]:
                    results.append(f"- {url}")

            # --- Hint for vague queries ---
            if tier == "vague":
                results.append(
                    "\n⚠️ Limited results. Try a more specific query "
                    "(e.g., include 'quarterly earnings', 'revenue', or sector-specific terms)."
                )

            return "\n".join(results)

    return f"No results found for: {query}"
