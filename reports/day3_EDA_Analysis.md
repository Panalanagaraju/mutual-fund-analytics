# Daily Work Report - Mutual Fund EDA Analysis

**Date:** 27 June 2026  
**Project:** Mutual Fund Analytics Platform  
**Work Focus:** Exploratory Data Analysis notebook and chart exports

## Overview

Today, the main focus was to complete the exploratory data analysis deliverable for the mutual fund analytics project. The work converted the cleaned mutual fund datasets into a complete analysis notebook with visual charts, key observations, and exported report-ready images.

The final output is a structured Jupyter notebook named `EDA_Analysis.ipynb`, supported by exported PNG charts in the `charts/eda/` folder. The notebook is designed so that anyone reviewing the project can follow the analysis step by step, run the cells, and understand the findings from the charts.

## Work Completed

### 1. Reviewed Available Project Data

The cleaned datasets in `data/processed/` were checked and matched with the required analysis tasks. The available files covered all required areas:

- Fund master data
- Daily NAV history
- AUM by fund house
- Monthly SIP inflows
- Category-wise inflows
- Industry folio count
- Investor transactions
- Portfolio holdings
- Scheme performance

This confirmed that the project already had enough structured data to complete the full EDA requirement without needing new data collection.

### 2. Created EDA Notebook Generator

A script was created at:

`scripts/create_eda_analysis_notebook.py`

This script automatically generates the final notebook:

`notebooks/EDA_Analysis.ipynb`

The generator approach makes the work repeatable. If the notebook needs to be recreated or refreshed later, the script can be run again instead of manually rebuilding the notebook.

### 3. Built the Final EDA Notebook

The generated notebook includes step-by-step sections for:

- Importing libraries and setting chart paths
- Loading cleaned datasets
- Creating NAV trend analysis
- Creating AUM growth analysis
- Creating SIP inflow analysis
- Creating category inflow heatmaps
- Studying investor demographics
- Studying geographic SIP distribution
- Tracking folio count growth
- Computing NAV return correlation
- Aggregating sector allocation from portfolio holdings
- Writing key EDA findings in Markdown cells

The notebook contains both code cells and explanation cells, so it can be used as a final submission file as well as a working analysis file.

## Charts Created

A total of **20 PNG charts** were exported, exceeding the requirement of 15+ charts. Two interactive Plotly charts were also saved as HTML files.

Main charts created:

1. Daily NAV trend for all 40 schemes, 2022-2026
2. Indexed NAV growth comparison
3. AUM growth grouped bar chart by fund house
4. Latest fund house AUM ranking
5. Monthly SIP inflow time series
6. Active SIP accounts and SIP AUM growth
7. Category-wise monthly net inflow heatmap
8. Annual category inflows
9. Investor age group distribution pie chart
10. SIP amount box plot by age group
11. Gender split chart
12. SIP amount by state
13. T30 vs B30 city tier pie chart
14. Folio count growth line chart
15. Folio growth by category
16. NAV return correlation matrix for 10 selected funds
17. Sector allocation donut chart
18. Risk vs 3-year return scatter plot
19. Top schemes by alpha
20. Expense ratio distribution by category

The exported files are available in:

`charts/eda/`

## Required Highlights Added

The required business highlights were included in the analysis:

- The NAV trend chart highlights the **2023 bull run**.
- The NAV trend chart also highlights the **2024 market correction period**.
- The AUM chart annotates **SBI Mutual Fund dominance at Rs. 12.5 lakh crore**.
- The SIP time-series chart annotates the **Rs. 31,002 crore all-time high in December 2025**.
- The folio count chart shows growth from **13.26 crore in January 2022** to **26.12 crore in December 2025**.

## Key EDA Findings Documented

The notebook includes 10 Markdown insight cells. Each finding is written as one clear insight sentence with a supporting chart reference.

The key findings cover:

- NAV growth during the 2023 bull run
- Temporary NAV softness during 2024 corrections
- SBI Mutual Fund's AUM leadership
- Strong SIP inflow growth
- Growth in active SIP accounts and SIP AUM
- Monthly variation in category inflows
- Investor age group participation
- State-wise SIP concentration
- Strong folio count expansion
- Positive return correlation among selected large funds

## Technical Notes

The notebook uses:

- `pandas` for data loading and transformation
- `matplotlib` and `seaborn` for static PNG charts
- `plotly` for interactive charts
- `nbformat` to generate the notebook programmatically
- `jupyter nbconvert` to execute the notebook and save outputs

Plotly PNG export requires the `kaleido` package, which was not installed in the current environment. To handle this properly, Plotly charts were saved as interactive HTML files, and separate static PNG versions were created for final report use.

## Files Created or Updated

Created:

- `scripts/create_eda_analysis_notebook.py`
- `notebooks/EDA_Analysis.ipynb`
- `charts/eda/*.png`
- `charts/eda/*.html`
- `reports/today_work_report_2026-06-27.md`

## How to Run the Work Again

From the project root:

```powershell
cd D:\Intern_BlueStock\MutualFundAnalytics
```

Activate the virtual environment:

```powershell
.\venv\Scripts\activate
```

Generate the notebook:

```powershell
python scripts\create_eda_analysis_notebook.py
```

Execute the notebook and export charts:

```powershell
jupyter nbconvert --to notebook --execute notebooks\EDA_Analysis.ipynb --inplace --ExecutePreprocessor.timeout=600
```

Open the notebook:

```powershell
jupyter notebook
```

Then open:

`notebooks/EDA_Analysis.ipynb`

## Final Status

The EDA task is complete. The project now has a finished notebook, more than the required number of charts, exported PNG files for the final report, interactive Plotly HTML files, and documented insights that explain the analysis in a clear and review-friendly way.
