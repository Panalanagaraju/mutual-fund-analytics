# Advanced Analytics Report

**Date:** 01 July 2026  
**Project:** Mutual Fund Analytics Platform  
**Work Focus:** Tail risk, rolling Sharpe, investor cohorts, SIP continuity, recommender, and portfolio concentration

## Overview

This report summarizes the advanced analytics work completed for all 40 mutual fund schemes. The analysis used cleaned NAV history, fund master data, investor transactions, portfolio holdings, and the existing scorecard to compute fund risk, investor behavior, and recommendation outputs.

### Generated Deliverables

- `Advanced_Analytics.ipynb`
- `var_cvar_report.csv`
- `rolling_sharpe_chart.png`
- `recommender.py`
- `scripts/create_advanced_analytics.py`

The notebook was executed successfully and the CSV/chart outputs were regenerated from local cleaned datasets.

## Work Completed

### 1. Historical VaR and CVaR

Daily returns were calculated from NAV history:

```text
daily_return = NAV_t / NAV_t-1 - 1
```

Historical VaR at 95% confidence was calculated as the 5th percentile of each fund's daily return distribution. CVaR was calculated as the average return below the VaR threshold.

```text
VaR 95% = 5th percentile of daily returns
CVaR 95% = mean(daily returns <= VaR 95%)
```

The output file `var_cvar_report.csv` contains all 40 schemes.

**Highest downside VaR funds:**

| Fund | Category | Risk | VaR 95% | CVaR 95% |
| --- | --- | --- | ---: | ---: |
| SBI Small Cap Fund - Direct Plan - Growth | Small Cap | Very High | -2.69% | -3.24% |
| Axis Small Cap Fund - Regular - Growth | Small Cap | Very High | -2.62% | -3.17% |
| ABSL Small Cap Fund - Regular - Growth | Small Cap | Very High | -2.60% | -3.25% |
| Nippon India Small Cap Fund - Regular - Growth | Small Cap | Very High | -2.54% | -3.23% |
| SBI Small Cap Fund - Regular Plan - Growth | Small Cap | Very High | -2.45% | -3.06% |

**Observation:** Small-cap schemes dominate the left-tail risk list, which matches their higher volatility profile.

### 2. Rolling 90-Day Sharpe

Rolling Sharpe was calculated for the top 5 scorecard funds:

```text
Rolling Sharpe = returns.rolling(90).mean() / returns.rolling(90).std() * sqrt(252)
```

The chart was saved as `rolling_sharpe_chart.png`.

The plotted funds are:

| Rank | Fund |
| ---: | --- |
| 1 | Mirae Asset Large Cap Fund - Regular - Growth |
| 2 | ICICI Pru Midcap Fund - Regular - Growth |
| 3 | Kotak Flexicap Fund - Regular - Growth |
| 4 | HDFC Mid-Cap Opportunities Fund - Regular - Growth |
| 5 | ICICI Pru Bluechip Fund - Direct - Growth |

### 3. Investor Cohort Analysis

Investors were grouped by first transaction year. For each cohort, the analysis computed investor count, average SIP amount, total invested amount, and top fund preference by invested amount.

| First Transaction Year | Investors | Avg SIP Amount | Total Invested | Top Fund Preference |
| ---: | ---: | ---: | ---: | --- |
| 2024 | 4,803 | INR 10,996.89 | INR 2,258,062,304 | Axis Small Cap Fund - Regular - Growth |
| 2025 | 197 | INR 13,505.21 | INR 18,992,635 | Axis Midcap Fund - Regular - Growth |

**Observation:** The 2024 cohort contributes the largest investment pool by a wide margin. The 2025 cohort is smaller but has a higher average SIP ticket size.

### 4. SIP Continuity Analysis

For investors with 6 or more SIP transactions, average transaction gaps were computed. Investors with average gap above 35 days were flagged as at-risk.

```text
At-risk SIP investor = avg_gap_days > 35
```

| Metric | Value |
| --- | ---: |
| Eligible SIP investors | 1,362 |
| Continuous investors | 30 |
| At-risk investors | 1,332 |
| Continuity rate | 2.2% |
| Average gap | 64.89 days |
| Median gap | 64.69 days |
| Maximum average gap | 102.60 days |

**Observation:** SIP continuity is weak under a strict 35-day gap rule. This suggests many investors are skipping monthly SIP cycles or transactions are not recorded at regular monthly frequency.

### 5. Simple Fund Recommender

The recommender takes one input:

```text
Low / Moderate / High
```

It filters funds by matching `risk_category` and prints the top 3 funds by Sharpe ratio.

Example command:

```text
.\.venv\Scripts\python.exe recommender.py Moderate
```

**Top Moderate-risk recommendations:**

| Fund | Risk Category | Sharpe Ratio | Fund Score |
| --- | --- | ---: | ---: |
| Mirae Asset Large Cap Fund - Regular - Growth | Moderate | 1.448 | 86.25 |
| Kotak Flexicap Fund - Regular - Growth | Moderately High | 1.307 | 82.00 |
| SBI Bluechip Fund - Regular Plan - Growth | Moderate | 1.208 | 74.81 |

### 6. Sector HHI Concentration

Portfolio concentration was measured using the Herfindahl-Hirschman Index:

```text
HHI = sum(weight_i ^ 2)
```

Higher HHI indicates a more concentrated portfolio. The analysis used latest available portfolio holdings.

**Most concentrated equity funds:**

| Fund | Sub Category | HHI | Band |
| --- | --- | ---: | --- |
| Axis Bluechip Fund - Regular - Growth | Large Cap | 0.206 | Concentrated |
| ABSL Small Cap Fund - Regular - Growth | Small Cap | 0.201 | Concentrated |
| SBI Small Cap Fund - Direct Plan - Growth | Small Cap | 0.175 | Moderate |
| UTI Nifty 50 Index Fund - Regular - Growth | Index | 0.175 | Moderate |
| Nippon India Large Cap Fund - Regular - Growth | Large Cap | 0.168 | Moderate |

**Observation:** Axis Bluechip Fund has the highest concentration score among equity schemes in the latest holdings snapshot.

## Advanced Insights

1. SBI Small Cap Fund - Direct Plan - Growth has the deepest 95% historical VaR at -2.69% daily return.
2. ABSL Small Cap Fund - Regular - Growth has the harshest CVaR at -3.25%, meaning its losses beyond the VaR threshold are the most severe on average.
3. The 2024 investor cohort contributes the highest total investment at INR 2,258,062,304.
4. SIP continuity is low: only 30 of 1,362 eligible investors are continuous by the 35-day average-gap rule.
5. Axis Bluechip Fund - Regular - Growth has the highest portfolio concentration with HHI of 0.206.

## Conclusion

The advanced analytics layer adds risk, behavior, and recommendation depth to the mutual fund platform. Tail-risk metrics separate volatile small-cap schemes from steadier debt/liquid funds, rolling Sharpe shows time-varying performance quality, cohort analysis highlights where investor value is concentrated, SIP continuity reveals retention risk, and HHI exposes portfolio concentration across equity funds.
