"""
ingest.py — Load family office CSV, build TF-IDF index, save to disk.

No external model downloads required. Uses numpy + pandas only.

Run:
    python ingest.py --csv ../task1/family_office_dataset.csv
    python ingest.py --csv ../task1/family_office_dataset.csv --reset
"""

import argparse
import json
import os
import sys
import pickle
import re
import math
from collections import Counter
from pathlib import Path

import pandas as pd
import numpy as np

INDEX_PATH = Path("./fo_index.pkl")


# ── Text processing ────────────────────────────────────────────────────────────

STOPWORDS = set("""
a an the and or but in on at to for of with by from is are was were be been
has have had do does did will would could should may might shall can cannot
its it this that these those we our us i me my you your he his she her they
their them all any some no not also as if so than into out up over well
""".split())


def tokenize(text: str) -> list:
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def build_document_text(row: dict) -> str:
    parts = [
        str(row.get("FO_Name", "")),
        str(row.get("FO_Type", "")),
        str(row.get("HQ_City", "")),
        str(row.get("HQ_Country", "")),
        str(row.get("AUM_Estimate", "")),
        str(row.get("Investment_Stage", "")),
        str(row.get("Sector_Focus", "")),
        str(row.get("Geographic_Focus", "")),
        str(row.get("Investment_Strategy", "")),
        str(row.get("Investment_Themes", "")),
        str(row.get("Co_Invest_Frequency", "")),
        str(row.get("Co_Investor_Relationships", "")),
        str(row.get("Portfolio_Companies", "")),
        str(row.get("Decision_Maker_1_Name", "")),
        str(row.get("Decision_Maker_1_Role", "")),
        str(row.get("Recent_News", "")),
        str(row.get("LP_Relationships", "")),
        str(row.get("Fund_Relationships", "")),
    ]
    return " ".join(p for p in parts if p not in ("", "N/A", "nan"))


# ── TF-IDF index builder ───────────────────────────────────────────────────────

def build_tfidf_index(documents: list[str]):
    """Build TF-IDF matrix. Returns (tfidf_matrix, vocab)."""
    print(f"  Tokenizing {len(documents)} documents...")
    tokenized = [tokenize(doc) for doc in documents]

    # Build vocabulary
    vocab = {}
    for tokens in tokenized:
        for t in set(tokens):
            if t not in vocab:
                vocab[t] = len(vocab)
    V = len(vocab)
    N = len(documents)
    print(f"  Vocabulary size: {V}")

    # Compute TF and DF
    tf_matrix = np.zeros((N, V), dtype=np.float32)
    df = np.zeros(V, dtype=np.float32)

    for i, tokens in enumerate(tokenized):
        counts = Counter(tokens)
        total = max(len(tokens), 1)
        for term, count in counts.items():
            if term in vocab:
                j = vocab[term]
                tf_matrix[i, j] = count / total
                df[j] += 1

    # IDF
    idf = np.log((N + 1) / (df + 1)) + 1.0

    # TF-IDF
    tfidf = tf_matrix * idf

    # L2 normalize
    norms = np.linalg.norm(tfidf, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    tfidf = tfidf / norms

    return tfidf, vocab, idf


def build_metadata(row: dict) -> dict:
    def safe_int(val):
        try:
            return int(float(str(val).replace(",", "").replace("$", "").replace("+", "")))
        except (ValueError, TypeError):
            return 0

    return {
        "fo_name":           str(row.get("FO_Name", "")),
        "fo_type":           str(row.get("FO_Type", "")).upper(),
        "hq_city":           str(row.get("HQ_City", "")),
        "hq_country":        str(row.get("HQ_Country", "")),
        "aum_estimate":      str(row.get("AUM_Estimate", "")),
        "check_size_min":    safe_int(row.get("Check_Size_Min", 0)),
        "check_size_max":    safe_int(row.get("Check_Size_Max", 0)),
        "investment_stage":  str(row.get("Investment_Stage", "")),
        "sector_focus":      str(row.get("Sector_Focus", "")),
        "geographic_focus":  str(row.get("Geographic_Focus", "")),
        "co_invest_freq":    str(row.get("Co_Invest_Frequency", "")),
        "dm1_name":          str(row.get("Decision_Maker_1_Name", "")),
        "dm1_role":          str(row.get("Decision_Maker_1_Role", "")),
        "dm1_email":         str(row.get("Decision_Maker_1_Email", "")),
        "dm1_linkedin":      str(row.get("Decision_Maker_1_LinkedIn", "")),
        "portfolio_cos":     str(row.get("Portfolio_Companies", "")),
        "website":           str(row.get("Website", "")),
        "recent_news":       str(row.get("Recent_News", "")),
        "validation_status": str(row.get("Validation_Status", "")),
        "data_source":       str(row.get("Data_Source", "")),
        "last_updated":      str(row.get("Last_Updated", "")),
        "investment_themes": str(row.get("Investment_Themes", "")),
        "investment_strategy": str(row.get("Investment_Strategy", "")),
    }


def ingest(csv_path: str, reset: bool = False):
    if INDEX_PATH.exists() and not reset:
        print(f"Index already exists at {INDEX_PATH}. Use --reset to rebuild.")
        idx = load_index()
        print(f"  Loaded existing index: {idx['n_docs']} documents.")
        return idx["n_docs"]

    print(f"Loading dataset: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"  Rows loaded: {len(df)}")

    documents = []
    metadatas = []
    for _, row in df.iterrows():
        documents.append(build_document_text(row.to_dict()))
        metadatas.append(build_metadata(row.to_dict()))

    print("Building TF-IDF index...")
    tfidf_matrix, vocab, idf = build_tfidf_index(documents)

    index = {
        "tfidf_matrix": tfidf_matrix,
        "vocab": vocab,
        "idf": idf,
        "documents": documents,
        "metadatas": metadatas,
        "n_docs": len(documents),
    }

    with open(INDEX_PATH, "wb") as f:
        pickle.dump(index, f)

    print(f"\nIngestion complete. Index saved to {INDEX_PATH}")
    print(f"  Documents indexed: {len(documents)}")
    print(f"  Vocabulary size:   {len(vocab)}")
    return len(documents)


def load_index():
    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"Index not found at {INDEX_PATH}. Run 'python ingest.py' first."
        )
    with open(INDEX_PATH, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest family office CSV into TF-IDF index")
    parser.add_argument("--csv", default="../task1/family_office_dataset.csv")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"ERROR: CSV not found at {args.csv}")
        sys.exit(1)

    count = ingest(args.csv, reset=args.reset)
    print(f"\nReady. {count} family offices indexed.")
