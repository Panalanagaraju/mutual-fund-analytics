# Bluestock Mutual Fund Dashboard Report

Created on: 30-06-2026

## Output Files

- Dashboard PDF: `Dashboard.pdf`
- Page 1 PNG: `dashboard/page_exports/01_industry_overview.png`
- Page 2 PNG: `dashboard/page_exports/02_fund_performance.png`
- Page 3 PNG: `dashboard/page_exports/03_investor_analytics.png`
- Page 4 PNG: `dashboard/page_exports/04_sip_market_trends.png`
- Power BI theme: `dashboard/bluestock_powerbi_theme.json`
- Build notes and model audit: `dashboard/powerbi_build_notes.md`

## Dashboard Pages

### 1. Industry Overview

The page presents headline industry KPIs, the 2022-2025 AUM trend, and AUM by AMC. The KPI cards use the requested dashboard presentation values:

- Total AUM: Rs 81L Cr
- SIP Inflows: Rs 31K Cr
- Folios: 26.12 Cr
- Schemes: 1,908

Latest SQLite model snapshot:

- Latest AUM date: 2025-12-31
- Latest aggregated AUM in model: 62.74L Cr
- Top AMC by AUM: SBI Mutual Fund, 12.5L Cr
- Latest scheme count in model: 1,522

### 2. Fund Performance

The page includes a return vs risk scatter plot, fund scorecard table, and NAV comparison against NIFTY 50.

Key model observation:

- Highest 3Y return fund: SBI Small Cap Fund - Regular Plan - Growth, 23.39%

### 3. Investor Analytics

The page covers transaction amount by state, transaction type mix, age group vs average SIP amount, and monthly transaction volume.

Key model observation:

- Top transaction state by amount: Punjab, Rs 31.58 Cr

### 4. SIP & Market Trends

The page combines SIP inflow bars with the NIFTY 50 trend, plus a category inflow heatmap and top FY25 categories by net inflow.

Key model observations:

- Latest SIP month: 2025-12
- Latest SIP inflow: Rs 31,002 Cr
- Top FY25 category by net inflow: Liquid, Rs 104,947 Cr

## Data Model Status

The SQLite database was regenerated from cleaned processed CSVs. The relationship audit in `dashboard/powerbi_build_notes.md` reports zero orphan rows for the main `amfi_code` and `date` relationships used by the dashboard.

## Notes

Power BI Desktop is not available in this environment, so the native `.pbix` file still needs to be created in Power BI Desktop from `bluestock_mf.db` or the cleaned CSVs. The current PDF and PNG dashboard exports were regenerated successfully from the Python dashboard export script.
