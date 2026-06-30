# Bluestock Power BI Build Notes

Power BI Desktop was not available through the local command line, so the native PBIX file must be created in Desktop from this model.

## Verified SQLite Tables

- `dim_date`: 1,306 rows
- `dim_fund`: 40 rows
- `fact_aum`: 90 rows
- `fact_benchmark`: 8,050 rows
- `fact_category_inflows`: 144 rows
- `fact_folio_count`: 21 rows
- `fact_nav`: 46,000 rows
- `fact_performance`: 40 rows
- `fact_portfolio`: 322 rows
- `fact_sip`: 48 rows
- `fact_sip_inflows`: 48 rows
- `fact_transactions`: 32,778 rows

## Required Relationships

- `dim_fund[amfi_code]` 1:* `fact_nav[amfi_code]`
- `dim_fund[amfi_code]` 1:* `fact_transactions[amfi_code]`
- `dim_fund[amfi_code]` 1:* `fact_performance[amfi_code]`
- `dim_fund[amfi_code]` 1:* `fact_portfolio[amfi_code]`
- `dim_date[date]` 1:* `fact_nav[date]`
- `dim_date[date]` 1:* `fact_transactions[transaction_date]`
- `dim_date[date]` 1:* `fact_aum[date]`
- `dim_date[date]` 1:* `fact_benchmark[date]`

## Relationship Audit

- `fact_nav amfi_code -> dim_fund`: 0 orphan rows
- `fact_transactions amfi_code -> dim_fund`: 0 orphan rows
- `fact_performance amfi_code -> dim_fund`: 0 orphan rows
- `fact_portfolio amfi_code -> dim_fund`: 0 orphan rows
- `fact_nav date -> dim_date`: 0 orphan rows
- `fact_transactions transaction_date -> dim_date`: 0 orphan rows
- `fact_aum date -> dim_date`: 0 orphan rows
- `fact_benchmark date -> dim_date`: 0 orphan rows

## Assets

- Theme: `dashboard/bluestock_powerbi_theme.json`
- Logo: `dashboard/bluestock_logo.png`
- SQLite source: `bluestock_mf.db`