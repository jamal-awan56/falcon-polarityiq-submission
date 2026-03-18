"""
pipeline.py — End-to-end RAG chain: TF-IDF retrieval + Claude API generation.
"""

from __future__ import annotations
import os
from typing import Optional
import anthropic
from retrieval import search, get_index_stats

CLAUDE_MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """You are a senior family office intelligence analyst with deep expertise in private wealth,
alternative investments, and family office operations.

You have access to a curated database of 271 family offices globally. When answering:
- Be specific and cite the relevant family offices by name
- Include key details: AUM, check size, sector focus, geography, decision makers when available
- If multiple matches exist, summarize patterns across them
- Be direct — these users are sophisticated institutional investors
- Format responses with names in **bold** when listing results
- If the database has insufficient info, say so clearly"""

DEMO_QUERIES = [
    "Which family offices focus on AI/ML with check sizes above $10M?",
    "Show me all single-family offices that made direct investments in the last 12 months",
    "Which family offices in New York focus on healthcare and life sciences?",
    "Find family offices that frequently co-invest with other funds",
    "Which European family offices have AUM above $500M?",
]


def format_context(results: list[dict], max_records: int = 8) -> str:
    if not results:
        return "No matching family offices found in the database."
    lines = [f"RETRIEVED FAMILY OFFICE RECORDS ({len(results)} matches):\n"]
    for i, r in enumerate(results[:max_records], 1):
        check_range = (
            f"${r['check_size_min']:,}–${r['check_size_max']:,}"
            if r["check_size_min"] > 0 else "N/A"
        )
        block = [
            f"[{i}] {r['fo_name']} ({r['fo_type']})",
            f"    Location: {r['hq_city']}, {r['hq_country']}",
            f"    AUM: {r['aum_estimate']} | Check Size: {check_range}",
            f"    Stage: {r['investment_stage']}",
            f"    Sectors: {r['sector_focus']}",
            f"    Geography: {r['geographic_focus']}",
            f"    Co-Invest Frequency: {r['co_invest_freq']}",
        ]
        if r["dm1_name"] not in ("N/A", "", "nan"):
            block.append(f"    Decision Maker: {r['dm1_name']} ({r['dm1_role']})")
        if r["portfolio_cos"] not in ("N/A", "", "nan"):
            block.append(f"    Portfolio: {r['portfolio_cos'][:80]}")
        if r["recent_news"] not in ("N/A", "", "nan"):
            block.append(f"    Recent News: {r['recent_news']}")
        block.append(f"    Relevance: {r['relevance_score']:.4f}")
        lines.append("\n".join(block))
    return "\n\n".join(lines)


def run_rag(
    query: str,
    n_results: int = 10,
    fo_type:        Optional[str] = None,
    hq_country:     Optional[str] = None,
    sector_keyword: Optional[str] = None,
    min_check_size: Optional[int] = None,
    max_check_size: Optional[int] = None,
    co_invest_freq: Optional[str] = None,
    geography_kw:   Optional[str] = None,
    stream: bool = False,
) -> dict:
    """Full RAG: retrieve → format context → generate with Claude."""
    # Retrieve
    results = search(
        query=query,
        n_results=n_results,
        fo_type=fo_type,
        hq_country=hq_country,
        sector_keyword=sector_keyword,
        min_check_size=min_check_size,
        max_check_size=max_check_size,
        co_invest_freq=co_invest_freq,
        geography_kw=geography_kw,
    )

    context = format_context(results)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        # Return retrieval results only
        plain = _plain_results(results)
        return {
            "query": query,
            "retrieved_count": len(results),
            "results": results,
            "context": context,
            "response": f"[No ANTHROPIC_API_KEY — showing raw retrieval]\n\n{plain}",
        }

    client = anthropic.Anthropic(api_key=api_key)
    user_msg = f"""User Query: {query}

Database Context:
{context}

Answer the user's query based on the family office records above. Be specific and cite names."""

    if stream:
        def _stream_gen():
            with client.messages.stream(
                model=CLAUDE_MODEL,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            ) as s:
                for text in s.text_stream:
                    yield text
        return {
            "query": query,
            "retrieved_count": len(results),
            "results": results,
            "context": context,
            "response_stream": _stream_gen(),
        }

    msg = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return {
        "query": query,
        "retrieved_count": len(results),
        "results": results,
        "context": context,
        "response": msg.content[0].text,
    }


def _plain_results(results: list[dict]) -> str:
    if not results:
        return "No results found."
    lines = []
    for i, r in enumerate(results, 1):
        check = f"${r['check_size_min']:,}–${r['check_size_max']:,}" if r["check_size_min"] > 0 else "N/A"
        lines.append(
            f"{i:2d}. {r['fo_name']} ({r['fo_type']}) | "
            f"{r['hq_city']}, {r['hq_country']} | "
            f"AUM: {r['aum_estimate']} | Check: {check}"
        )
        if r["sector_focus"] not in ("N/A","","nan"):
            lines.append(f"    Sectors: {r['sector_focus']}")
    return "\n".join(lines)


if __name__ == "__main__":
    print("Pipeline test")
    print("Stats:", get_index_stats())
    for q in DEMO_QUERIES[:2]:
        print(f"\nQUERY: {q}")
        r = run_rag(q, n_results=5)
        print(f"Retrieved: {r['retrieved_count']}")
        print(r["response"][:600])
