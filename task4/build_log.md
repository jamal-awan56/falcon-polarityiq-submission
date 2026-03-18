# Private Credit Intelligence Toolkit — Build Log

**Build Date:** 2026-03-18 21:39:32
**Toolkit Version:** 1.0
**Price Point:** $197
**ICP:** Independent RIAs, family office analysts, private wealth managers, alternative investment allocators

---

## Build Summary

All 5 product components were successfully generated programmatically using Python.

| File | Description | Size |
|------|-------------|------|
| `Private_Credit_Deal_Scorecard.xlsx` | .XLSX file | 11.7 KB |
| `Manager_Due_Diligence_Framework.docx` | .DOCX file | 43.4 KB |
| `Portfolio_Allocation_Optimizer.xlsx` | .XLSX file | 10.3 KB |
| `Private_Credit_Glossary_Education_Guide.docx` | .DOCX file | 42.9 KB |
| `ai_deal_memo_generator.py` | .PY file | 9.3 KB |

---

## Tools & Libraries Used

| Tool | Purpose | Version |
|------|---------|---------|
| Python | Build scripting | 3.11+ |
| openpyxl | Excel file generation (XLSX) | 3.1+ |
| python-docx | Word document generation (DOCX) | 1.1+ |
| Streamlit | Web app interface for AI memo generator | 1.38+ |
| Anthropic Claude API | AI-powered deal memo generation | claude-sonnet-4-20250514 |

---

## Component Details

### 1. Private_Credit_Deal_Scorecard.xlsx
- **Sheet 1 (Deal Scorecard):** 24 weighted criteria across 6 categories; auto-calculates weighted score and Red/Yellow/Green rating
- **Sheet 2 (Benchmark Comparison):** 12 market benchmarks across direct lending, mezz, BDC, and distressed strategies
- **Sheet 3 (Return Calculator):** Risk-adjusted expected return with base/downside/stress scenarios and hurdle rate comparison
- All formulas are live; user inputs are highlighted in yellow

### 2. Manager_Due_Diligence_Framework.docx
- 75 questions across 5 sections (Strategy, Team, Track Record, Operations, Terms)
- Each question includes guidance notes for the evaluator
- 8 automatic red flag indicators
- Scoring rubric with 1–5 scale and section weights
- Composite manager score summary table
- Sectional weighting: Track Record 25%, Strategy 20%, Team 20%, Operations 20%, Terms 15%

### 3. Portfolio_Allocation_Optimizer.xlsx
- **Sheet 1 (Allocation Dashboard):** Current vs. target allocation by seniority and sector with live status indicators
- **Sheet 2 (Manager Tracker):** Manager-level performance tracking (IRR, DPI, TVPI, MOIC)
- **Sheet 3 (Liquidity Ladder):** 12-quarter forward distribution and capital call projections with cumulative cash flow
- **Sheet 4 (Concentration Alerts):** 6 diversification dimensions with automated alert triggers

### 4. Private_Credit_Glossary_Education_Guide.docx
- 150+ terms defined across the full A–Z spectrum of private credit
- 3-part structure: Market Overview → Glossary → Market Data
- Strategy comparison matrix (direct lending, unitranche, mezz, distressed, specialty)
- 2024 market sizing data and trend analysis

### 5. ai_deal_memo_generator.py (Streamlit App)
- 3-column input form: Company/Deal | Economics | Credit Metrics
- Real-time calculated metrics (all-in yield, EBITDA margin, debt service)
- Claude API integration (claude-sonnet-4-20250514) for memo generation
- Full IC-ready memo: Executive Summary, Company Overview, Financial Analysis, Structure, Risk Factors, Comparables, Recommendation
- Download memo as text file

---

## Ascension Path Design

```
$197 Toolkit Purchase
    │
    ├─► Email sequence: "Using your scorecard? These are the family offices
    │   in your market actively allocating to private credit."
    │
    └─► $497/mo PolarityIQ Pro (family office + private credit manager database)
            │
            └─► $2,500 custom research reports (bespoke market analysis)
```

The toolkit is deliberately priced as a **trip-wire product**: low enough to remove purchase friction,
high enough to signal serious intent. Buyers who use the scorecard and glossary are self-identifying
as active private credit allocators — the highest-value PolarityIQ subscriber segment.

---

## Data Sources Referenced

- Preqin Global Private Debt Report 2024
- Cliffwater Direct Lending Index (CDLI) methodology
- Bloomberg Private Credit Market Data
- SEC EDGAR (ADV filings for private credit fund data)
- Standard & Poor's Leveraged Commentary & Data (LCD)

---

*Built for Falcon Scaling / PolarityIQ evaluation — March 2025*
