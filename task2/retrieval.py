"""
retrieval.py — TF-IDF semantic search + metadata filtering.
No external model downloads required.
"""

from __future__ import annotations
import re
from collections import Counter
from typing import Optional

import numpy as np

from ingest import load_index, tokenize, STOPWORDS

_index = None


def _get_index():
    global _index
    if _index is None:
        _index = load_index()
    return _index


def _embed_query(query: str, vocab: dict, idf: np.ndarray) -> np.ndarray:
    """Convert query string to a TF-IDF vector using the corpus vocabulary."""
    tokens = tokenize(query)
    V = len(vocab)
    vec = np.zeros(V, dtype=np.float32)
    if not tokens:
        return vec
    counts = Counter(tokens)
    total = len(tokens)
    for term, count in counts.items():
        if term in vocab:
            j = vocab[term]
            vec[j] = (count / total) * idf[j]
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def search(
    query: str,
    n_results: int = 10,
    fo_type:        Optional[str] = None,
    hq_country:     Optional[str] = None,
    sector_keyword: Optional[str] = None,
    min_check_size: Optional[int] = None,
    max_check_size: Optional[int] = None,
    co_invest_freq: Optional[str] = None,
    geography_kw:   Optional[str] = None,
) -> list[dict]:
    """
    Semantic search with optional metadata filters.
    Returns list of result dicts sorted by relevance score.
    """
    idx = _get_index()
    tfidf_matrix = idx["tfidf_matrix"]
    vocab        = idx["vocab"]
    idf          = idx["idf"]
    metadatas    = idx["metadatas"]
    documents    = idx["documents"]

    # Embed query
    q_vec = _embed_query(query, vocab, idf)

    # Cosine similarity (matrix @ vector)
    scores = tfidf_matrix @ q_vec  # shape (N,)

    # Sort descending
    ranked_indices = np.argsort(scores)[::-1]

    # Collect results with filters
    results = []
    for i in ranked_indices:
        meta  = metadatas[i]
        score = float(scores[i])

        # Metadata filters
        if fo_type and meta.get("fo_type", "").upper() != fo_type.upper():
            continue
        if hq_country and meta.get("hq_country", "").lower() != hq_country.lower():
            continue
        if min_check_size and min_check_size > 0:
            if meta.get("check_size_max", 0) < min_check_size:
                continue
        if max_check_size and max_check_size > 0:
            if meta.get("check_size_min", 0) > max_check_size:
                continue
        if co_invest_freq and meta.get("co_invest_freq", "") != co_invest_freq:
            continue
        if sector_keyword:
            if sector_keyword.lower() not in meta.get("sector_focus", "").lower():
                continue
        if geography_kw:
            geo_text = (
                meta.get("geographic_focus", "").lower() +
                meta.get("hq_country", "").lower() +
                meta.get("hq_city", "").lower()
            )
            if geography_kw.lower() not in geo_text:
                continue

        results.append({
            "id":               f"fo_{i:05d}",
            "document":         documents[i],
            "fo_name":          meta.get("fo_name", ""),
            "fo_type":          meta.get("fo_type", ""),
            "hq_city":          meta.get("hq_city", ""),
            "hq_country":       meta.get("hq_country", ""),
            "aum_estimate":     meta.get("aum_estimate", ""),
            "check_size_min":   meta.get("check_size_min", 0),
            "check_size_max":   meta.get("check_size_max", 0),
            "investment_stage": meta.get("investment_stage", ""),
            "sector_focus":     meta.get("sector_focus", ""),
            "geographic_focus": meta.get("geographic_focus", ""),
            "co_invest_freq":   meta.get("co_invest_freq", ""),
            "dm1_name":         meta.get("dm1_name", ""),
            "dm1_role":         meta.get("dm1_role", ""),
            "dm1_email":        meta.get("dm1_email", ""),
            "dm1_linkedin":     meta.get("dm1_linkedin", ""),
            "portfolio_cos":    meta.get("portfolio_cos", ""),
            "website":          meta.get("website", ""),
            "recent_news":      meta.get("recent_news", ""),
            "validation_status":meta.get("validation_status", ""),
            "investment_themes":meta.get("investment_themes", ""),
            "relevance_score":  round(score, 4),
        })

        if len(results) >= n_results:
            break

    return results


def get_index_stats() -> dict:
    try:
        idx = _get_index()
        return {"total_records": idx["n_docs"], "vocab_size": len(idx["vocab"])}
    except Exception as e:
        return {"error": str(e), "total_records": 0}


if __name__ == "__main__":
    print("Quick test — retrieval.py")
    results = search("family offices in New York focused on healthcare large check sizes", n_results=5)
    print(f"Results: {len(results)}")
    for r in results:
        print(f"  {r['fo_name']:35s} | {r['hq_city']:15s} | {r['sector_focus'][:30]:30s} | {r['relevance_score']:.4f}")
