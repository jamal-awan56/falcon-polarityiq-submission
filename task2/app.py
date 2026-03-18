"""
app.py — Streamlit interface for the Family Office RAG pipeline.

Run:
    streamlit run app.py

Deploy:
    Push to GitHub, connect to Streamlit Community Cloud, set ANTHROPIC_API_KEY in secrets.
"""

import os
import sys
import streamlit as st
import pandas as pd
from io import BytesIO

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PolarityIQ Family Office Intelligence",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.fo-card {
    background: #1a1a2e;
    border: 1px solid #16213e;
    border-left: 4px solid #0f3460;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 10px 0;
}
.fo-card-sfo { border-left-color: #e94560; }
.fo-card-mfo { border-left-color: #0f3460; }
.fo-name { font-size: 18px; font-weight: 700; color: #ffffff; }
.fo-tag { background: #0f3460; color: #ffffff; padding: 2px 8px; border-radius: 12px;
          font-size: 11px; margin-right: 4px; }
.fo-tag-sfo { background: #e94560; }
.metric-row { display: flex; gap: 20px; margin: 8px 0; flex-wrap: wrap; }
.metric-item { font-size: 13px; color: #a0a0b0; }
.metric-value { font-size: 13px; color: #ffffff; font-weight: 600; }
.score-badge { float: right; background: #0d7c3d; color: white;
               padding: 2px 10px; border-radius: 12px; font-size: 12px; }
.demo-btn { cursor: pointer; }
</style>
""", unsafe_allow_html=True)

# ── Imports (lazy to handle missing deps gracefully) ──────────────────────────
@st.cache_resource(show_spinner="Loading intelligence engine...")
def load_pipeline():
    """Load ChromaDB + embedding model (cached across sessions)."""
    try:
        from pipeline import run_rag, DEMO_QUERIES
        from retrieval import get_collection_stats
        stats = get_collection_stats()
        return run_rag, DEMO_QUERIES, stats
    except Exception as e:
        return None, [], {"error": str(e), "total_records": 0}


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/falcon.png", width=60)
    st.title("PolarityIQ")
    st.caption("Family Office Intelligence Platform")
    st.divider()

    st.subheader("🔍 Filters")

    fo_type_filter = st.selectbox(
        "Family Office Type",
        options=["All", "SFO (Single)", "MFO (Multi)"],
        index=0,
    )
    fo_type_val = None
    if fo_type_filter == "SFO (Single)":
        fo_type_val = "SFO"
    elif fo_type_filter == "MFO (Multi)":
        fo_type_val = "MFO"

    sector_filter = st.text_input(
        "Sector Keyword",
        placeholder="e.g. Healthcare, AI, Real Estate",
        help="Filter by sector focus",
    )

    geography_filter = st.text_input(
        "Geography Keyword",
        placeholder="e.g. New York, Europe, Singapore",
        help="Filter by city, country, or region",
    )

    check_min_filter = st.number_input(
        "Min Check Size ($)",
        min_value=0,
        value=0,
        step=1_000_000,
        format="%d",
    )

    co_invest_filter = st.selectbox(
        "Co-Investment Frequency",
        options=["All", "High", "Med", "Low"],
        index=0,
    )
    co_invest_val = None if co_invest_filter == "All" else co_invest_filter

    n_results = st.slider("Max Results", min_value=5, max_value=30, value=10, step=5)

    st.divider()
    st.subheader("📊 Database Stats")
    run_rag_fn, DEMO_QUERIES, stats = load_pipeline()
    if "error" not in stats:
        st.metric("Total Records", stats.get("total_records", 0))
    else:
        st.error(f"DB Error: {stats['error']}")
        st.info("Run `python ingest.py` first to build the database.")

    st.divider()
    st.caption("Powered by ChromaDB + Claude API")
    st.caption("Embeddings: all-MiniLM-L6-v2")


# ── Main content ──────────────────────────────────────────────────────────────
st.title("🦅 Family Office Intelligence")
st.markdown("*Search 270+ verified family offices with natural language*")

# Demo query buttons
if DEMO_QUERIES:
    st.subheader("💡 Example Queries")
    cols = st.columns(len(DEMO_QUERIES[:5]))
    selected_demo = None
    for i, (col, q) in enumerate(zip(cols, DEMO_QUERIES[:5])):
        with col:
            # Truncate for button display
            short_q = q[:55] + "…" if len(q) > 55 else q
            if st.button(short_q, key=f"demo_{i}", use_container_width=True):
                selected_demo = q

# Query input
query_input = st.text_area(
    "Natural Language Query",
    value=selected_demo or "",
    placeholder="e.g. Which European family offices focus on healthcare with AUM above $500M?",
    height=100,
    key="query_box",
)

col_search, col_clear = st.columns([1, 5])
with col_search:
    search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
with col_clear:
    if st.button("Clear", use_container_width=False):
        st.rerun()

st.divider()

# ── Run search ────────────────────────────────────────────────────────────────
if search_clicked and query_input.strip():
    if run_rag_fn is None:
        st.error("Pipeline not loaded. Run `python ingest.py` first.")
    else:
        with st.spinner("Searching family office database..."):
            result = run_rag_fn(
                query=query_input.strip(),
                n_results=n_results,
                fo_type=fo_type_val,
                sector_keyword=sector_filter.strip() or None,
                geography_kw=geography_filter.strip() or None,
                min_check_size=int(check_min_filter) if check_min_filter > 0 else None,
                co_invest_freq=co_invest_val,
            )

        # ── AI Summary ────────────────────────────────────────────────────────
        st.subheader("🤖 AI Analysis")
        if "response" in result:
            st.markdown(result["response"])
        elif "response_stream" in result:
            with st.empty():
                full_response = ""
                for chunk in result["response_stream"]:
                    full_response += chunk
                    st.markdown(full_response + "▌")
                st.markdown(full_response)

        st.divider()

        # ── Results ───────────────────────────────────────────────────────────
        retrieved = result.get("results", [])
        st.subheader(f"📋 Results ({len(retrieved)} matches)")

        if not retrieved:
            st.info("No matching family offices found. Try broader search terms or adjust filters.")
        else:
            # Export button
            export_df = pd.DataFrame(retrieved).drop(columns=["document", "id"], errors="ignore")
            csv_bytes = export_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Export Results as CSV",
                data=csv_bytes,
                file_name=f"fo_results_{query_input[:30].replace(' ','_')}.csv",
                mime="text/csv",
            )

            # Result cards
            for r in retrieved:
                fo_type_class = "fo-card-sfo" if r["fo_type"] == "SFO" else "fo-card-mfo"
                check_range = (
                    f"${r['check_size_min']:,} – ${r['check_size_max']:,}"
                    if r["check_size_min"] > 0 else "N/A"
                )
                dm_line = ""
                if r["dm1_name"] and r["dm1_name"] not in ("N/A", ""):
                    dm_line = f"👤 **{r['dm1_name']}** ({r['dm1_role']})"
                    if r["dm1_linkedin"] and r["dm1_linkedin"] != "N/A":
                        dm_line += f" · [LinkedIn]({r['dm1_linkedin']})"

                portfolio_line = ""
                if r["portfolio_cos"] and r["portfolio_cos"] not in ("N/A", ""):
                    portfolio_line = f"**Portfolio:** {r['portfolio_cos']}"

                news_line = ""
                if r["recent_news"] and r["recent_news"] not in ("N/A", ""):
                    news_line = f"📰 {r['recent_news']}"

                with st.container():
                    st.markdown(f"""
<div class="fo-card {fo_type_class}">
  <span class="score-badge">Score: {r['relevance_score']}</span>
  <div class="fo-name">{r['fo_name']}
    <span class="fo-tag {'fo-tag-sfo' if r['fo_type']=='SFO' else ''}">{r['fo_type']}</span>
  </div>
  <div style="color:#a0a0b0; font-size:13px; margin-top:4px;">
    📍 {r['hq_city']}, {r['hq_country']} &nbsp;|&nbsp;
    💰 AUM: {r['aum_estimate']} &nbsp;|&nbsp;
    📝 Check: {check_range}
  </div>
  <div style="margin-top:8px; font-size:13px; color:#c0c0d0;">
    🏭 <b>Sectors:</b> {r['sector_focus']}<br>
    🌍 <b>Geography:</b> {r['geographic_focus']}<br>
    📈 <b>Stage:</b> {r['investment_stage']} &nbsp;|&nbsp;
    🤝 <b>Co-Invest:</b> {r['co_invest_freq']}
  </div>
</div>
""", unsafe_allow_html=True)

                    if dm_line or portfolio_line or news_line:
                        with st.expander("More details"):
                            if dm_line:
                                st.markdown(dm_line)
                            if portfolio_line:
                                st.markdown(portfolio_line)
                            if news_line:
                                st.markdown(news_line)
                            if r.get("website") and r["website"] not in ("N/A", ""):
                                st.markdown(f"🌐 {r['website']}")

elif search_clicked:
    st.warning("Please enter a search query.")
else:
    # Landing state
    st.info(
        "👆 Enter a natural language query above or click a demo query to search "
        "the family office intelligence database."
    )
    st.markdown("""
**What you can search for:**
- Family offices by sector focus (AI, Healthcare, Real Estate, etc.)
- By geography (New York, Europe, Asia, etc.)
- By check size or AUM range
- By co-investment behavior
- By investment stage (Seed, Growth, PE, Buyout)
- By decision maker name
- Recent portfolio activity and news
""")
