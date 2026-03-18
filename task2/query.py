"""
query.py — Natural language query interface for the Family Office RAG pipeline.

Wraps retrieval.py + pipeline.py into a simple CLI and importable query function.

Usage (CLI):
    python query.py "Which family offices in New York focus on healthcare?"
    python query.py "European family offices with AUM above $500M" --top 5
    python query.py "Show co-investors" --fo-type SFO --sector Technology

Usage (Python):
    from query import query_family_offices
    results = query_family_offices("AI-focused family offices with $10M+ checks")
    for r in results:
        print(r['fo_name'], r['aum_estimate'], r['sector_focus'])
"""

from __future__ import annotations
import argparse
import sys
import os
from typing import Optional


def query_family_offices(
    query_text: str,
    top_k: int = 10,
    fo_type: Optional[str] = None,
    sector: Optional[str] = None,
    geography: Optional[str] = None,
    min_check_size: Optional[int] = None,
    co_invest_freq: Optional[str] = None,
    use_llm: bool = True,
) -> dict:
    """
    Run a natural language query against the family office vector database.

    Parameters
    ----------
    query_text     : Natural language question or search phrase
    top_k          : Max number of results to return (default 10)
    fo_type        : Filter by 'SFO' or 'MFO' (optional)
    sector         : Sector keyword filter, e.g. 'Healthcare' (optional)
    geography      : Geography keyword, e.g. 'New York' or 'Europe' (optional)
    min_check_size : Minimum check size in USD (optional)
    co_invest_freq : Filter by 'High', 'Med', or 'Low' (optional)
    use_llm        : If True, generate an AI summary using Claude API (default True)

    Returns
    -------
    dict with keys:
        - query          : original query
        - retrieved_count: number of records found
        - results        : list of matching family office records
        - response       : AI-generated natural language answer (if use_llm=True)
    """
    try:
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from pipeline import run_rag
    except ImportError as e:
        return {
            "query": query_text,
            "retrieved_count": 0,
            "results": [],
            "response": f"ERROR: Could not import pipeline. Run 'python ingest.py' first.\nDetails: {e}",
        }

    result = run_rag(
        query=query_text,
        n_results=top_k,
        fo_type=fo_type,
        sector_keyword=sector,
        geography_kw=geography,
        min_check_size=min_check_size,
        co_invest_freq=co_invest_freq,
    )

    # If LLM disabled or no API key, return retrieval-only results
    if not use_llm or not os.environ.get("ANTHROPIC_API_KEY"):
        result["response"] = _format_retrieval_only(result.get("results", []))

    return result


def _format_retrieval_only(results: list[dict]) -> str:
    """Plain-text formatted results when LLM is not available."""
    if not results:
        return "No matching family offices found."

    lines = [f"Found {len(results)} matching family offices:\n"]
    for i, r in enumerate(results, 1):
        check = (
            f"${r['check_size_min']:,}–${r['check_size_max']:,}"
            if r.get("check_size_min", 0) > 0 else "N/A"
        )
        lines.append(
            f"{i:2d}. {r['fo_name']} ({r['fo_type']}) | "
            f"{r['hq_city']}, {r['hq_country']} | "
            f"AUM: {r['aum_estimate']} | "
            f"Check: {check} | "
            f"Score: {r['relevance_score']:.3f}"
        )
        if r.get("sector_focus") and r["sector_focus"] != "N/A":
            lines.append(f"    Sectors: {r['sector_focus']}")
        if r.get("co_invest_freq"):
            lines.append(f"    Co-invest: {r['co_invest_freq']}")
    return "\n".join(lines)


def _print_result(result: dict, verbose: bool = False):
    """Pretty-print a query result to the console."""
    print(f"\n{'='*70}")
    print(f"QUERY: {result['query']}")
    print(f"RECORDS RETRIEVED: {result['retrieved_count']}")
    print(f"{'='*70}")

    if result.get("response"):
        print("\nAI RESPONSE:")
        print("-" * 40)
        print(result["response"])

    if verbose and result.get("results"):
        print("\nRAW RECORDS:")
        print("-" * 40)
        for r in result["results"]:
            print(f"  {r['fo_name']} | {r['aum_estimate']} | {r['sector_focus']} | Score:{r['relevance_score']}")


# ── Demo queries (used by test runner) ────────────────────────────────────────
DEMO_QUERIES = [
    {
        "query": "Which family offices focus on AI/ML with check sizes above $10M?",
        "filters": {"sector": "AI", "min_check_size": 10_000_000},
    },
    {
        "query": "Which family offices in New York focus on healthcare and life sciences?",
        "filters": {"geography": "New York", "sector": "Healthcare"},
    },
    {
        "query": "Find family offices that frequently co-invest with other funds",
        "filters": {"co_invest_freq": "High"},
    },
    {
        "query": "Which European family offices have AUM above $500M?",
        "filters": {"geography": "Europe"},
    },
    {
        "query": "Show me all single-family offices that made direct investments in the last 12 months",
        "filters": {"fo_type": "SFO"},
    },
]


# ── CLI ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Query the Family Office intelligence database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python query.py "Family offices investing in healthcare New York"
  python query.py "European SFOs with large check sizes" --top 5
  python query.py "Co-investors technology" --fo-type SFO --sector Technology
  python query.py --run-demos
        """,
    )
    parser.add_argument("query", nargs="?", help="Natural language query")
    parser.add_argument("--top", "-n", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("--fo-type", choices=["SFO", "MFO"], help="Filter by family office type")
    parser.add_argument("--sector", help="Filter by sector keyword")
    parser.add_argument("--geography", help="Filter by geography keyword")
    parser.add_argument("--min-check", type=int, default=0, help="Minimum check size in USD")
    parser.add_argument("--co-invest", choices=["High", "Med", "Low"], help="Co-investment frequency filter")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM generation, show raw results only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show raw records after LLM response")
    parser.add_argument("--run-demos", action="store_true", help="Run all 5 demo queries")

    args = parser.parse_args()

    if args.run_demos:
        print("Running 5 demo queries against the family office database...")
        for i, demo in enumerate(DEMO_QUERIES, 1):
            print(f"\n[Demo {i}/5]")
            result = query_family_offices(
                query_text=demo["query"],
                top_k=5,
                use_llm=not args.no_llm,
                **demo["filters"],
            )
            _print_result(result, verbose=args.verbose)
        return

    if not args.query:
        parser.print_help()
        print("\nNo query provided. Use --run-demos to test with example queries.")
        sys.exit(1)

    result = query_family_offices(
        query_text=args.query,
        top_k=args.top,
        fo_type=args.fo_type,
        sector=args.sector,
        geography=args.geography,
        min_check_size=args.min_check if args.min_check > 0 else None,
        co_invest_freq=args.co_invest,
        use_llm=not args.no_llm,
    )
    _print_result(result, verbose=args.verbose)


if __name__ == "__main__":
    main()
