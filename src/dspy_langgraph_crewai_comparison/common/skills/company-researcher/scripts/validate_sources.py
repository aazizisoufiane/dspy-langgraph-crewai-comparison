"""Validate source URLs from CompanyFacts.
In mock mode, checks URL format. In production, would check HTTP status."""

import json
import re
import sys


def validate_sources(urls: list[str]) -> dict:
    """Validate a list of source URLs."""
    results = {"valid": [], "invalid": [], "total": len(urls)}

    url_pattern = re.compile(
        r"^https?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    for url in urls:
        if url_pattern.match(url):
            results["valid"].append(url)
        else:
            results["invalid"].append(url)

    results["all_valid"] = len(results["invalid"]) == 0
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        urls = json.loads(sys.argv[1])
    else:
        urls = json.loads(sys.stdin.read())

    result = validate_sources(urls)
    print(json.dumps(result, indent=2))
