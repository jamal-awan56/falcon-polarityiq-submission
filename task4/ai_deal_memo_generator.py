"""
ai_deal_memo_generator.py — AI-powered private credit deal memo generator.
Uses Claude API to generate professional investment memo outlines.

Run:
    streamlit run ai_deal_memo_generator.py

Set ANTHROPIC_API_KEY environment variable before running.
"""

import os
import streamlit as st
import anthropic
from datetime import date

st.set_page_config(
    page_title="Private Credit Deal Memo Generator",
    page_icon="📄",
    layout="wide",
)

st.markdown("""
<style>
.main-header { font-size: 28px; font-weight: 700; color: #0D1B2A; margin-bottom: 5px; }
.sub-header  { font-size: 14px; color: #666; margin-bottom: 20px; }
.section-box { background: #F8F9FA; border-left: 4px solid #1B4F72;
               padding: 15px; margin: 10px 0; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📄 Private Credit Deal Memo Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered investment memo generation | The Private Credit Intelligence Toolkit</div>', unsafe_allow_html=True)

SYSTEM_PROMPT = """You are a senior credit analyst at a $10 billion private credit fund with 15 years of experience
in direct lending, mezzanine financing, and distressed credit. You write institutional-quality investment memos
used by investment committees at major credit funds, family offices, and BDCs.

When generating deal memos:
- Write in professional, precise credit-fund language
- Be specific about risks — do not generalize
- Include quantitative metrics wherever the inputs allow
- Structure the memo with clear sections and logical flow
- Identify 3–5 specific risk factors with mitigants for each
- Use market context (comparable deals, benchmark rates, industry trends) appropriately
- Be direct: if the deal has problems, say so clearly"""

def generate_memo(params: dict) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "⚠️ ANTHROPIC_API_KEY not set. Please set the environment variable and restart."

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Generate a comprehensive private credit investment memo for the following deal:

DEAL PARAMETERS:
- Company Name: {params["company_name"]}
- Industry / Sector: {params["sector"]}
- Transaction Type: {params["transaction_type"]}
- Total Facility Size: ${params["facility_size_m"]}M
- Drawn Amount at Close: ${params["drawn_amount_m"]}M
- Seniority: {params["seniority"]}
- SOFR Spread: {params["sofr_spread_bps"]}bps
- SOFR Floor: {params["sofr_floor_pct"]}%
- OID: {params["oid_pct"]}%
- PIK Component: {params["pik_pct"]}%
- Maturity: {params["maturity_years"]} years
- Borrower LTM Revenue: ${params["ltm_revenue_m"]}M
- Borrower LTM EBITDA: ${params["ltm_ebitda_m"]}M
- EBITDA Margin: {round(params["ltm_ebitda_m"]/params["ltm_revenue_m"]*100,1)}%
- Total Leverage (Debt/EBITDA): {params["total_leverage"]}x
- Senior Leverage: {params["senior_leverage"]}x
- Interest Coverage (EBITDA/Interest): {params["interest_coverage"]}x
- Sponsor (if PE-backed): {params["sponsor"]}
- Collateral: {params["collateral"]}
- Covenant Package: {params["covenant_package"]}
- Use of Proceeds: {params["use_of_proceeds"]}
- Additional Context: {params["additional_context"]}

Generate a full investment memo with the following sections:
1. EXECUTIVE SUMMARY (2–3 paragraphs: deal overview, thesis, recommendation)
2. COMPANY OVERVIEW (business description, competitive position, customer base)
3. FINANCIAL ANALYSIS (key metrics, EBITDA quality, FCF analysis, leverage analysis)
4. TRANSACTION STRUCTURE (facility terms, security package, covenant summary)
5. RISK FACTORS & MITIGANTS (5 specific risks, each with a mitigant)
6. COMPARABLE TRANSACTIONS (3 recent comparable private credit deals)
7. RECOMMENDATION (Clear proceed/conditional/pass with rationale)

Format the memo professionally. Use headers in ALL CAPS. Be specific and analytical."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text

# ── Input form ────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Company & Deal")
    company_name     = st.text_input("Company Name", "Acme Software Holdings")
    sector           = st.text_input("Sector / Industry", "B2B SaaS / HR Technology")
    transaction_type = st.selectbox("Transaction Type",
        ["LBO Financing","Acquisition Financing","Refinancing","Recapitalization",
         "Growth Capital","Dividend Recapitalization","Distressed Buyout"])
    seniority        = st.selectbox("Seniority",
        ["First Lien Senior Secured","Unitranche","Second Lien","Mezzanine","Senior Unsecured","HoldCo PIK"])
    sponsor          = st.text_input("PE Sponsor (if applicable)", "Vista Equity Partners")
    use_of_proceeds  = st.text_input("Use of Proceeds", "LBO acquisition financing + working capital")

with col2:
    st.subheader("Economics")
    facility_size_m  = st.number_input("Total Facility Size ($M)", 1.0, 5000.0, 75.0, 5.0)
    drawn_amount_m   = st.number_input("Drawn Amount at Close ($M)", 1.0, 5000.0, 65.0, 5.0)
    sofr_spread_bps  = st.number_input("SOFR Spread (bps)", 100, 2000, 600, 25)
    sofr_floor_pct   = st.number_input("SOFR Floor (%)", 0.0, 5.0, 0.5, 0.25)
    oid_pct          = st.number_input("OID (%)", 0.0, 10.0, 2.0, 0.25)
    pik_pct          = st.number_input("PIK Component (%)", 0.0, 15.0, 0.0, 0.5)
    maturity_years   = st.number_input("Maturity (years)", 1, 10, 5, 1)

with col3:
    st.subheader("Credit Metrics")
    ltm_revenue_m    = st.number_input("LTM Revenue ($M)", 1.0, 10000.0, 80.0, 5.0)
    ltm_ebitda_m     = st.number_input("LTM EBITDA ($M)", 1.0, 5000.0, 22.0, 1.0)
    total_leverage   = st.number_input("Total Leverage (Debt/EBITDA)", 1.0, 15.0, 5.8, 0.1)
    senior_leverage  = st.number_input("Senior Leverage", 0.5, 10.0, 4.5, 0.1)
    interest_coverage= st.number_input("Interest Coverage (EBITDA/Interest)", 0.5, 10.0, 1.8, 0.1)
    collateral       = st.text_input("Collateral Package", "First priority lien on all assets + pledged equity")
    covenant_package = st.selectbox("Covenant Package",
        ["Full Maintenance (leverage + coverage quarterly)",
         "Springing Maintenance Covenant","Incurrence Only (Covenant-Lite)","No Financial Covenants"])

additional_context = st.text_area(
    "Additional Context / Special Considerations",
    "Company has 90%+ recurring revenue with 120% net revenue retention. "
    "Top 10 customers = 35% of revenue. Sponsor has 5x equity cushion.",
    height=80,
)

# ── Calculated metrics display ────────────────────────────────────────────────
st.divider()
col_a, col_b, col_c, col_d, col_e = st.columns(5)
all_in_yield = (sofr_spread_bps/100) + sofr_floor_pct + (oid_pct/maturity_years) + pik_pct
col_a.metric("All-In Yield (est.)", f"{all_in_yield:.2f}%")
col_b.metric("EBITDA Margin", f"{ltm_ebitda_m/ltm_revenue_m*100:.1f}%")
col_c.metric("Total Leverage", f"{total_leverage:.1f}x")
col_d.metric("Interest Coverage", f"{interest_coverage:.1f}x")
col_e.metric("Debt Service ($M/yr)", f"${drawn_amount_m * all_in_yield/100:.1f}M")

# ── Generate button ────────────────────────────────────────────────────────────
if st.button("📄 Generate Investment Memo", type="primary", use_container_width=True):
    params = dict(
        company_name=company_name, sector=sector, transaction_type=transaction_type,
        seniority=seniority, sponsor=sponsor, use_of_proceeds=use_of_proceeds,
        facility_size_m=facility_size_m, drawn_amount_m=drawn_amount_m,
        sofr_spread_bps=sofr_spread_bps, sofr_floor_pct=sofr_floor_pct,
        oid_pct=oid_pct, pik_pct=pik_pct, maturity_years=maturity_years,
        ltm_revenue_m=ltm_revenue_m, ltm_ebitda_m=ltm_ebitda_m,
        total_leverage=total_leverage, senior_leverage=senior_leverage,
        interest_coverage=interest_coverage, collateral=collateral,
        covenant_package=covenant_package, additional_context=additional_context,
    )
    with st.spinner("Generating investment memo (30–45 seconds)..."):
        memo = generate_memo(params)

    st.divider()
    st.subheader("📄 Generated Investment Memo")
    st.markdown(memo)

    # Download button
    st.download_button(
        label="⬇️ Download Memo as Text",
        data=memo,
        file_name=f"investment_memo_{company_name.replace(' ','_')}_{date.today()}.txt",
        mime="text/plain",
    )
else:
    st.info("👆 Fill in deal parameters above and click **Generate Investment Memo**.")
    st.markdown("""
**Pre-loaded example:** Acme Software Holdings — B2B SaaS LBO by Vista Equity Partners
- $75M first lien unitranche at SOFR + 600bps
- 5.8x total leverage, 90% recurring revenue
- Full maintenance covenant package

*The toolkit generates a full IC-ready memo in ~30 seconds.*
""")
