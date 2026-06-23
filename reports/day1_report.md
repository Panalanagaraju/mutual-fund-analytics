# Day 1 Report – Data Ingestion and Initial Data Validation

## Mutual Fund Analytics Platform

### Introduction

The primary objective of Day 1 was to establish the project environment, load and validate all available mutual fund datasets, explore the structure of the data, and integrate live NAV data from an external API source. This phase was focused on ensuring that the datasets were accessible, consistent, and suitable for further analysis in the Mutual Fund Analytics Platform.

---

## Project Setup

The project folder structure was successfully created with dedicated directories for raw data, processed data, notebooks, SQL scripts, dashboards, and reports. Version control was initialized using Git, and the repository was connected to GitHub for collaborative development and tracking of project progress.

The following folders were created:

* data/raw
* data/processed
* notebooks
* sql
* dashboard
* reports

Additionally, all required Python libraries were installed and documented in the requirements.txt file.

---

## Data Ingestion Summary

A total of **17 CSV datasets** were successfully loaded and examined using Pandas.

The datasets consist of mutual fund master data, historical NAV records, AUM statistics, SIP inflows, category-wise inflows, investor transaction data, portfolio holdings, benchmark index data, and live NAV information collected from MFAPI.

### Key Dataset Statistics

| Dataset                   |   Rows | Columns |
| ------------------------- | -----: | ------: |
| Fund Master               |     40 |      15 |
| NAV History               | 46,000 |       3 |
| AUM by Fund House         |     90 |       5 |
| Monthly SIP Inflows       |     48 |       6 |
| Category Inflows          |    144 |       3 |
| Industry Folio Count      |     21 |       6 |
| Scheme Performance        |     40 |      19 |
| Investor Transactions     | 32,778 |      13 |
| Portfolio Holdings        |    322 |       8 |
| Benchmark Indices         |  8,050 |       3 |
| Axis Bluechip NAV         |  3,580 |       8 |
| HDFC Top 100 Direct NAV   |  3,106 |       8 |
| ICICI Bluechip NAV        |  3,322 |       8 |
| Kotak Bluechip NAV        |  3,316 |       8 |
| Live NAV Combined Dataset | 19,888 |       8 |
| Nippon Large Cap NAV      |  3,313 |       8 |
| SBI Bluechip NAV          |  3,251 |       8 |

All datasets were loaded successfully without any file-reading errors.

---

## Fund Master Dataset Exploration

The Fund Master dataset serves as the primary reference table for all mutual fund schemes in the project.

### Dataset Overview

* Total Records: **40**
* Total Columns: **15**
* Missing Values: **0**
* Duplicate Records: **0**

### Fund Houses Identified

The dataset contains schemes from **10 major fund houses**:

* SBI Mutual Fund
* HDFC Mutual Fund
* ICICI Prudential MF
* Nippon India MF
* Kotak Mahindra MF
* Axis Mutual Fund
* Aditya Birla Sun Life MF
* UTI Mutual Fund
* Mirae Asset MF
* DSP Mutual Fund

### Categories Available

The schemes are classified into two primary categories:

* Equity
* Debt

### Sub-Categories Available

A total of **12 sub-categories** were identified:

* Large Cap
* Small Cap
* Mid Cap
* Flexi Cap
* Value
* ELSS
* Index
* Index/ETF
* Large & Mid Cap
* Gilt
* Liquid
* Short Duration

These classifications will be useful for future performance analysis, category comparison, and recommendation features.

---

## Live NAV Data Collection

Live NAV data was successfully fetched using the MFAPI service.

The following schemes were selected for data collection:

1. HDFC Top 100 Direct
2. SBI Bluechip
3. ICICI Bluechip
4. Nippon Large Cap
5. Axis Bluechip
6. Kotak Bluechip

The API responses were parsed and stored as structured CSV files.

### Live NAV Dataset Summary

* Combined NAV Records Collected: **19,888**
* Missing Values: **0**
* Duplicate Records: **0**

The live NAV integration process completed successfully and generated separate CSV files for each scheme as well as a combined NAV dataset.

---

## AMFI Code Validation

An AMFI code validation process was attempted between the Fund Master dataset and the NAV History dataset.

During validation it was observed that:

* The Fund Master dataset uses the column **amfi_code**
* The NAV History dataset also uses the column **amfi_code**

However, the validation script was searching for a column named **scheme_code**, resulting in a mismatch and preventing the validation from being completed automatically.

This issue was identified during Day 1 and can be corrected by updating the validation logic to use the **amfi_code** field instead of **scheme_code**.

---

## Data Quality Assessment

A detailed quality assessment was performed across all datasets.

### Positive Observations

* All 17 datasets loaded successfully.
* No duplicate records were identified in any dataset.
* Most datasets contain complete information with no missing values.
* Data types are consistent and suitable for analytical processing.
* Historical NAV data contains a substantial volume of records (46,000 rows) for trend analysis.
* Investor transaction data contains over 32,000 records, providing a strong foundation for behavioral analytics.

### Data Quality Issues Identified

#### Monthly SIP Inflows Dataset

The Monthly SIP Inflows dataset contains:

* 48 rows
* 6 columns
* 12 missing values

The missing values are present in the **yoy_growth_pct** column and likely correspond to periods where year-over-year comparisons were not available.

No other significant missing-value issues were detected.

---

## Overall Data Quality Summary

| Metric                       | Result |
| ---------------------------- | ------ |
| Total Datasets Loaded        | 17     |
| Datasets Loaded Successfully | 17     |
| Duplicate Records Found      | 0      |
| Major Missing Value Issues   | No     |
| API Integration Successful   | Yes    |
| Data Ready for Analysis      | Yes    |

The overall dataset quality is excellent and suitable for further processing, exploratory analysis, and dashboard development.

---

## Deliverables Completed

The following Day 1 deliverables were successfully completed:

* Project folder structure creation
* Git repository initialization
* GitHub repository setup
* requirements.txt creation
* data_ingestion.py development
* live_nav_fetch.py development
* Loading and validation of all datasets
* Fund master exploration
* Live NAV API integration
* Initial data quality assessment
* Jupyter notebook setup for exploratory analysis

---

## Conclusion

Day 1 successfully established the data foundation for the Mutual Fund Analytics Platform. All available datasets were ingested and analyzed, live NAV information was collected through API integration, and preliminary data quality checks were performed. The datasets contain comprehensive information related to mutual fund schemes, historical NAV movements, investor transactions, portfolio holdings, industry trends, and benchmark performance.

The project environment is now fully prepared for Day 2 activities, which will focus on data cleaning, preprocessing, feature engineering, and exploratory data analysis.
