# Daily Work Report - Performance Analytics

**Date:** 29 June 2026  
**Project:** Mutual Fund Analytics Platform  
**Work Focus:** Risk-return analytics, fund ranking, alpha/beta regression, and benchmark comparison

## Overview

Today's task focused on building the performance analytics layer for all 40 mutual fund schemes. The work used cleaned NAV history, fund master data, and benchmark index data to calculate returns, risk ratios, drawdowns, benchmark regression metrics, tracking error, and a composite fund scorecard.

The final outputs are a reproducible Jupyter notebook, two CSV result files, and a benchmark comparison chart.

### Generated Deliverables

- `notebooks/Performance_Analytics.ipynb`
- `data/processed/fund_scorecard.csv`
- `data/processed/alpha_beta.csv`
- `charts/performance/benchmark_comparison_top5.png`

The notebook was executed successfully in the project environment and the metrics files were regenerated.

## Work Completed

### 1. Computed Daily Returns

Daily returns were calculated for all 40 schemes using:

```text
daily_return = NAV_t / NAV_t-1 - 1
```

The return distribution was checked to confirm that values were reasonable.

**Daily return distribution across all funds:**

| Metric             |    Value |
| ------------------ | -------: |
| Observations       |   45,960 |
| Mean daily return  |  0.0631% |
| Standard deviation |  1.0290% |
| Minimum            | -5.8102% |
| 1st percentile     | -2.5982% |
| 5th percentile     | -1.6254% |
| Median             |  0.0340% |
| 95th percentile    |  1.7842% |
| 99th percentile    |  2.7617% |
| Maximum            |  6.4713% |

The distribution is centered close to zero with realistic equity-style tails.

### 2. Computed CAGR

CAGR was calculated for 1-year and 3-year periods using:

```text
CAGR = (NAV_end / NAV_start) ^ (1 / n) - 1
```

The available NAV history runs from **03 January 2022** to **29 May 2026**. Because the data does not contain a complete 5-year history, true 5-year CAGR is unavailable and the 5-year CAGR column is left blank in the scorecard.

**Top 5 funds by final score with return values:**

| Rank | Fund                                               | Score | 1Y CAGR | 3Y CAGR |
| ---: | -------------------------------------------------- | ----: | ------: | ------: |
|    1 | Mirae Asset Large Cap Fund - Regular - Growth      | 86.25 |  20.36% |  34.00% |
|    2 | ICICI Pru Midcap Fund - Regular - Growth           | 82.25 |  29.60% |  31.78% |
|    3 | Kotak Flexicap Fund - Regular - Growth             | 82.00 |  26.66% |  29.58% |
|    4 | HDFC Mid-Cap Opportunities Fund - Regular - Growth | 80.75 |  53.23% |  32.44% |
|    5 | ICICI Pru Bluechip Fund - Direct - Growth          | 80.00 |  13.06% |  32.49% |

### 3. Computed Sharpe Ratio

Sharpe Ratio was calculated using an annual risk-free rate of **6.5%**, based on the RBI repo rate proxy:

```text
Sharpe Ratio = (Rp - Rf) / Std(Rp) * sqrt(252)
```

**Top 5 funds by Sharpe Ratio:**

| Fund                                          | Sharpe Ratio | Annualized Volatility |
| --------------------------------------------- | -----------: | --------------------: |
| Mirae Asset Large Cap Fund - Regular - Growth |       1.4483 |                14.19% |
| Kotak Flexicap Fund - Regular - Growth        |       1.3067 |                15.89% |
| Mirae Asset Tax Saver Fund - Regular - Growth |       1.2349 |                17.67% |
| SBI Bluechip Fund - Regular Plan - Growth     |       1.2083 |                13.74% |
| ICICI Pru Midcap Fund - Regular - Growth      |       1.1801 |                19.29% |

### 4. Computed Sortino Ratio

Sortino Ratio was calculated with downside deviation using only negative daily returns.

**Top 5 funds by Sortino Ratio:**

| Fund                                          | Sortino Ratio |
| --------------------------------------------- | ------------: |
| Mirae Asset Large Cap Fund - Regular - Growth |        2.3856 |
| Kotak Flexicap Fund - Regular - Growth        |        2.3643 |
| Mirae Asset Tax Saver Fund - Regular - Growth |        2.1469 |
| SBI Bluechip Fund - Regular Plan - Growth     |        2.1403 |
| ICICI Pru Midcap Fund - Regular - Growth      |        2.0294 |

### 5. Computed Alpha and Beta

Alpha and beta were calculated using OLS regression of each fund's daily returns against NIFTY100 daily returns through `scipy.stats.linregress`.

```text
Alpha = regression_intercept * 252
Beta = regression_slope
```

**Top 5 funds by annualized alpha:**

| Fund                                          |  Alpha |    Beta | R-Squared |
| --------------------------------------------- | -----: | ------: | --------: |
| SBI Small Cap Fund - Regular Plan - Growth    | 30.34% | -0.0232 |    0.0001 |
| DSP Small Cap Fund - Regular - Growth         | 30.06% |  0.0115 |    0.0000 |
| ICICI Pru Midcap Fund - Regular - Growth      | 29.26% |  0.0005 |    0.0000 |
| Mirae Asset Tax Saver Fund - Regular - Growth | 28.27% |  0.0181 |    0.0002 |
| Kotak Flexicap Fund - Regular - Growth        | 27.33% | -0.0228 |    0.0003 |

The complete alpha and beta table was exported to:

```text
data/processed/alpha_beta.csv
```

### 6. Computed Maximum Drawdown

Maximum drawdown was calculated for each fund using:

```text
drawdown = NAV / running_max - 1
```

The analysis also captured the peak date, trough date, and recovery date where available.

**Worst 5 maximum drawdowns:**

| Fund                                       | Max Drawdown | Peak Date  | Trough Date | Recovery Date |
| ------------------------------------------ | -----------: | ---------- | ----------- | ------------- |
| SBI Small Cap Fund - Direct Plan - Growth  |      -52.57% | 2023-01-17 | 2025-10-28  | Not recovered |
| Axis Small Cap Fund - Regular - Growth     |      -51.68% | 2025-05-22 | 2026-05-11  | Not recovered |
| ABSL Small Cap Fund - Regular - Growth     |      -35.45% | 2024-11-21 | 2026-05-11  | Not recovered |
| DSP Small Cap Fund - Regular - Growth      |      -31.17% | 2024-05-03 | 2025-01-03  | 2025-06-13    |
| SBI Small Cap Fund - Regular Plan - Growth |      -28.71% | 2024-08-28 | 2025-05-14  | 2025-09-29    |

### 7. Created Fund Scorecard

A 0-100 composite score was built using the required weights:

| Component                   | Weight |
| --------------------------- | -----: |
| 3-year return rank          |    30% |
| Sharpe Ratio rank           |    25% |
| Alpha rank                  |    20% |
| Expense ratio rank, inverse |    15% |
| Max drawdown rank, inverse  |    10% |

The complete scorecard was exported to:

```text
data/processed/fund_scorecard.csv
```

**Top 10 funds by composite score:**

| Rank | Fund                                               | Score | 3Y CAGR | Sharpe |  Alpha |  Max DD |
| ---: | -------------------------------------------------- | ----: | ------: | -----: | -----: | ------: |
|    1 | Mirae Asset Large Cap Fund - Regular - Growth      | 86.25 |  34.00% | 1.4483 | 26.98% | -11.27% |
|    2 | ICICI Pru Midcap Fund - Regular - Growth           | 82.25 |  31.78% | 1.1801 | 29.26% | -18.19% |
|    3 | Kotak Flexicap Fund - Regular - Growth             | 82.00 |  29.58% | 1.3067 | 27.33% | -12.97% |
|    4 | HDFC Mid-Cap Opportunities Fund - Regular - Growth | 80.75 |  32.44% | 1.0937 | 27.20% | -16.22% |
|    5 | ICICI Pru Bluechip Fund - Direct - Growth          | 80.00 |  32.49% | 1.0265 | 21.19% | -12.59% |
|    6 | Axis Midcap Fund - Regular - Growth                | 77.00 |  35.11% | 0.9982 | 26.08% | -20.96% |
|    7 | SBI Bluechip Fund - Regular Plan - Growth          | 74.81 |  30.46% | 1.2083 | 23.20% | -15.01% |
|    8 | Mirae Asset Tax Saver Fund - Regular - Growth      | 73.69 |  29.18% | 1.2349 | 28.27% | -16.40% |
|    9 | ABSL Frontline Equity Fund - Regular - Growth      | 68.19 |  28.97% | 1.0272 | 21.40% | -11.29% |
|   10 | SBI Small Cap Fund - Regular Plan - Growth         | 67.38 |  26.67% | 0.9453 | 30.34% | -28.71% |

### 8. Created Benchmark Comparison Chart

A benchmark comparison chart was created for the top 5 scorecard funds against NIFTY50 and NIFTY100 over the latest 3-year period.

Chart exported to:

```text
charts/performance/benchmark_comparison_top5.png
```

**Tracking error for top 5 funds:**

| Fund                                               | Benchmark | Tracking Error |
| -------------------------------------------------- | --------- | -------------: |
| Mirae Asset Large Cap Fund - Regular - Growth      | NIFTY50   |         19.18% |
| Mirae Asset Large Cap Fund - Regular - Growth      | NIFTY100  |         18.79% |
| ICICI Pru Midcap Fund - Regular - Growth           | NIFTY50   |         22.83% |
| ICICI Pru Midcap Fund - Regular - Growth           | NIFTY100  |         23.25% |
| Kotak Flexicap Fund - Regular - Growth             | NIFTY50   |         20.49% |
| Kotak Flexicap Fund - Regular - Growth             | NIFTY100  |         20.64% |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth | NIFTY50   |         22.81% |
| HDFC Mid-Cap Opportunities Fund - Regular - Growth | NIFTY100  |         22.48% |
| ICICI Pru Bluechip Fund - Direct - Growth          | NIFTY50   |         18.84% |
| ICICI Pru Bluechip Fund - Direct - Growth          | NIFTY100  |         18.73% |

## Files Created

The following files were created for today's performance analytics task:

- `scripts/create_performance_analytics_notebook.py`
- `notebooks/Performance_Analytics.ipynb`
- `data/processed/fund_scorecard.csv`
- `data/processed/alpha_beta.csv`
- `charts/performance/benchmark_comparison_top5.png`
- `reports/today_work_report_2026-06-29.md`

## How to Reproduce

From the project root:

```powershell
cd D:\Intern_BlueStock\MutualFundAnalytics
```

Generate the notebook:

```powershell
python scripts\create_performance_analytics_notebook.py
```

Execute the notebook and regenerate outputs:

```powershell
python -m jupyter nbconvert --to notebook --execute notebooks\Performance_Analytics.ipynb --inplace
```

## Final Outcome

The performance analytics task is complete. All 40 schemes were ranked using return, risk, alpha, expense ratio, and drawdown metrics. The final scorecard identifies **Mirae Asset Large Cap Fund - Regular - Growth** as the highest-ranked fund with a composite score of **86.25**.
