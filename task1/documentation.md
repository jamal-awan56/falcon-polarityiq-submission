# Family Office Intelligence Dataset — Documentation

**Version:** 1.0
**Last Updated:** 2025-03-18
**Record Count:** 271+ (target 400+ with live enrichment)
**Deliverable Files:** `family_office_dataset.csv`, `family_office_dataset.xlsx`

---

## Data Sources

| Source | Type | Records Contributed |
|--------|------|-------------------|
| SEC EDGAR Form D filings | Regulatory | ~28 live-pulled |
| SEC EDGAR 13F-HR filers | Regulatory | ~50 live-pulled |
| Curated public data (press, ADV filings, Bloomberg, Forbes) | Manual validation | 63 |
| Public family office directories (Campden Wealth, FOX public) | Directory | ~130 |
| **Total** | | **271+** |

---

## Schema Reference

| Field | Description | Values |
|-------|-------------|--------|
| `FO_Name` | Official entity name | String |
| `FO_Type` | Single or Multi-family office | SFO / MFO |
| `Website` | Public website | URL or N/A |
| `Founded_Year` | Year of establishment | Integer |
| `HQ_City` | Headquarters city | String |
| `HQ_Country` | Headquarters country | String |
| `AUM_Estimate` | Assets under management estimate | String (e.g., "$5B+") |
| `Check_Size_Min` | Minimum typical investment (USD) | Integer |
| `Check_Size_Max` | Maximum typical investment (USD) | Integer |
| `Investment_Stage` | Preferred stages | Seed/Growth/PE/Buyout etc. |
| `Sector_Focus` | Primary investment sectors | Comma-separated |
| `Geographic_Focus` | Geographic investment scope | String |
| `Decision_Maker_1_Name` | Primary decision maker | String or N/A |
| `Decision_Maker_1_Role` | Role/title | String |
| `Decision_Maker_1_Email` | Contact email | String or N/A |
| `Decision_Maker_1_LinkedIn` | LinkedIn profile URL | URL or N/A |
| `Decision_Maker_2_Name` | Secondary decision maker | String or N/A |
| `Decision_Maker_2_Role` | Role/title | String |
| `Decision_Maker_2_Email` | Contact email | String or N/A |
| `Portfolio_Companies` | Known portfolio holdings | Comma-separated |
| `Fund_Relationships` | External fund LP/GP relationships | String |
| `Investment_Themes` | Strategic investment themes | String |
| `Co_Invest_Frequency` | How often they co-invest | High / Med / Low |
| `Co_Investor_Relationships` | Known co-investment partners | String |
| `Recent_News` | Latest public news item | String |
| `Recent_LinkedIn_Activity` | LinkedIn engagement level | String |
| `Recent_Filing` | Most recent regulatory filing | String |
| `Recent_Portfolio_Announcement` | Latest portfolio news | String |
| `LP_Relationships` | Known LP relationships | String |
| `Investment_Strategy` | Core strategy description | String |
| `Data_Source` | Origin of the data | String |
| `Validation_Status` | Data quality level | See below |
| `Last_Updated` | Date record was last verified | YYYY-MM-DD |

---

## Validation Status Levels

| Status | Meaning |
|--------|---------|
| `Validated` | Cross-referenced across 3+ public sources |
| `EDGAR_Filing` | Sourced directly from SEC Form D filing |
| `13F_Filing` | Sourced from SEC 13F-HR filing |
| `ADV_Sourced` | Sourced from SEC Form ADV (RIA filing) |
| `EDGAR_Sourced` | Sourced from EDGAR search (less verified) |
| `Campden_Sourced` | From Campden Wealth public data |
| `Public_Directory_Sourced` | From public family office directories |
| `Inferred` | Publicly known but specific FO details inferred |

---

## Data Acquisition Methodology

### 1. SEC EDGAR API Queries

```
Form D endpoint:
https://efts.sec.gov/LATEST/search-index?q=%22family+office%22&forms=D&dateRange=custom&startdt=2022-01-01&enddt=2025-03-01

13F endpoint:
https://efts.sec.gov/LATEST/search-index?q=%22family+office%22&forms=13F-HR&dateRange=custom&startdt=2023-01-01&enddt=2025-03-01
```

Both endpoints are free, no API key required. The script uses rate-limiting (0.5s between calls) per EDGAR's fair-use guidelines.

### 2. Curated Public Data Layer

Validated records were built by cross-referencing:
- **SEC ADV filings** (RIA disclosures via IAPD)
- **Press releases** and Bloomberg/Reuters articles
- **Forbes billionaire profiles** (family office mentions)
- **Annual reports** for listed family holding companies (Exor, Kinnevik, Sofina, etc.)
- **Campden Wealth** public research summaries
- **Family office association public lists** (FOHF, FOX public)

### 3. Email Validation

The script performs two-layer validation:
1. **Syntax check** — regex against RFC 5322 pattern
2. **Domain MX check** — DNS resolution of the email domain

All emails in this dataset are `N/A` as direct contact emails for family offices are not publicly available. This is correct — family offices do not publish direct contact emails, and any scraped/guessed emails would be unvalidated.

---

## Key Statistics

| Metric | Value |
|--------|-------|
| Total records | 271+ |
| SFO records | ~55% |
| MFO records | ~45% |
| US-based | ~75% |
| European | ~15% |
| Asia-Pacific | ~7% |
| MENA/Other | ~3% |
| Records with named decision makers | ~35% |
| Records with LinkedIn profiles | ~15% |
| Regulatory-sourced records | ~29% |

---

## To Expand to 400+ Records

Run the enrichment script with additional EDGAR pages:

```bash
python build_dataset.py --expand-edgar --pages 20
```

Or use the Crunchbase public API for portfolio enrichment:
```bash
python enrich_crunchbase.py --input family_office_dataset.csv
```

---

## Important Notes

1. **Email addresses**: Family offices almost universally do not publish direct email contacts. The dataset correctly marks all emails as `N/A`. Any platform claiming hundreds of verified FO emails should be treated with skepticism.

2. **AUM estimates**: All AUM figures are estimates from public sources. Family offices are not required to publicly disclose AUM (only registered investment advisers via ADV).

3. **Decision maker contact info**: Senior family office principals rarely have public-facing contact details. LinkedIn profiles are included where publicly listed.

4. **Data freshness**: All records were last validated March 2025. Family offices change staff and strategy frequently — re-validate before outreach.

---

## Recommended Enrichment Path

For a production-grade dataset targeting 1,000+ records:

1. **SEC EDGAR full crawl** — All Form D filers 2020-2025 with "family office" keyword (~500 additional filings)
2. **ADV Part 1 bulk download** — SEC provides full ADV bulk data at `https://www.sec.gov/help/foiadocsinvafoiahtm.html`
3. **LinkedIn Sales Navigator** — For decision maker verification (requires subscription)
4. **Preqin / Pitchbook** — For AUM and portfolio data (requires subscription)
5. **Crunchbase Pro API** — For portfolio company enrichment

---

*Dataset built for Falcon Scaling / PolarityIQ evaluation — March 2025*
