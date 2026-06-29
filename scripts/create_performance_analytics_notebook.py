from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "Performance_Analytics.ipynb"


cells = [
    nbf.v4.new_markdown_cell(
        """# Performance Analytics

This notebook computes fund-level return, risk, benchmark, and scorecard metrics for the 40 mutual fund schemes using cleaned NAV, fund master, and benchmark index data.

Outputs:
- `data/processed/fund_scorecard.csv`
- `data/processed/alpha_beta.csv`
- `charts/performance/benchmark_comparison_top5.png`
"""
    ),
    nbf.v4.new_code_cell(
        """from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import linregress

warnings.filterwarnings("ignore")

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA_DIR = ROOT / "data" / "processed"
CHART_DIR = ROOT / "charts" / "performance"
CHART_DIR.mkdir(parents=True, exist_ok=True)

NAV_PATH = DATA_DIR / "cleaned_nav_history.csv"
FUND_MASTER_PATH = DATA_DIR / "cleaned_fund_master.csv"
BENCHMARK_PATH = DATA_DIR / "cleaned_benchmark_indices.csv"

RISK_FREE_RATE = 0.065
TRADING_DAYS = 252

sns.set_theme(style="whitegrid", palette="Set2")
pd.set_option("display.max_columns", 80)
pd.set_option("display.float_format", lambda x: f"{x:,.4f}")"""
    ),
    nbf.v4.new_markdown_cell("## Load and Prepare Data"),
    nbf.v4.new_code_cell(
        """nav = pd.read_csv(NAV_PATH, parse_dates=["date"])
fund_master = pd.read_csv(FUND_MASTER_PATH, parse_dates=["launch_date"])
benchmarks = pd.read_csv(BENCHMARK_PATH, parse_dates=["date"])

nav = nav.sort_values(["amfi_code", "date"]).copy()
fund_master["amfi_code"] = fund_master["amfi_code"].astype(nav["amfi_code"].dtype)

nav_wide = nav.pivot(index="date", columns="amfi_code", values="nav").sort_index()
benchmark_wide = (
    benchmarks.pivot(index="date", columns="index_name", values="close_value")
    .sort_index()
)

print(f"NAV rows: {len(nav):,}")
print(f"Schemes: {nav['amfi_code'].nunique()}")
print(f"NAV date range: {nav['date'].min().date()} to {nav['date'].max().date()}")
print(f"Benchmarks: {', '.join(benchmark_wide.columns)}")"""
    ),
    nbf.v4.new_markdown_cell("## Daily Returns and Distribution Validation"),
    nbf.v4.new_code_cell(
        """daily_returns = nav_wide.pct_change()
benchmark_returns = benchmark_wide.pct_change()

return_distribution = (
    daily_returns.stack()
    .rename("daily_return")
    .reset_index()
    .groupby("amfi_code")["daily_return"]
    .agg(["count", "mean", "std", "min", "median", "max"])
    .reset_index()
    .merge(fund_master[["amfi_code", "scheme_name", "fund_house", "category", "plan"]], on="amfi_code", how="left")
)

all_daily_returns = daily_returns.stack().dropna()
distribution_summary = all_daily_returns.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])
print(distribution_summary)

fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(all_daily_returns, bins=100, kde=True, ax=ax)
ax.axvline(all_daily_returns.mean(), color="black", linestyle="--", linewidth=1, label="Mean")
ax.set_title("Distribution of Daily Fund Returns")
ax.set_xlabel("Daily return")
ax.set_ylabel("Observation count")
ax.legend()
plt.show()

return_distribution.head()"""
    ),
    nbf.v4.new_markdown_cell("## CAGR for 1 Year, 3 Years, and 5 Years"),
    nbf.v4.new_code_cell(
        """def cagr_from_nav(nav_series: pd.Series, years: int) -> float:
    series = nav_series.dropna().sort_index()
    if series.empty:
        return np.nan

    end_date = series.index.max()
    target_start = end_date - pd.DateOffset(years=years)
    candidates = series.loc[series.index <= target_start]
    if candidates.empty:
        return np.nan

    start_nav = candidates.iloc[-1]
    end_nav = series.loc[end_date]
    return (end_nav / start_nav) ** (1 / years) - 1


def available_period_cagr(nav_series: pd.Series) -> float:
    series = nav_series.dropna().sort_index()
    elapsed_years = (series.index.max() - series.index.min()).days / 365.25
    if elapsed_years <= 0:
        return np.nan
    return (series.iloc[-1] / series.iloc[0]) ** (1 / elapsed_years) - 1


cagr_rows = []
for amfi_code, series in nav_wide.items():
    cagr_rows.append(
        {
            "amfi_code": amfi_code,
            "cagr_1yr_pct": cagr_from_nav(series, 1) * 100,
            "cagr_3yr_pct": cagr_from_nav(series, 3) * 100,
            "cagr_5yr_pct": cagr_from_nav(series, 5) * 100,
            "cagr_available_period_pct": available_period_cagr(series) * 100,
            "available_start_date": series.dropna().index.min().date(),
            "available_end_date": series.dropna().index.max().date(),
        }
    )

cagr_table = (
    pd.DataFrame(cagr_rows)
    .merge(fund_master[["amfi_code", "scheme_name", "fund_house", "category", "plan"]], on="amfi_code", how="left")
    .sort_values("cagr_3yr_pct", ascending=False)
)

if cagr_table["cagr_5yr_pct"].isna().all():
    print("True 5-year CAGR is unavailable because NAV history starts after the required 5-year lookback date.")

cagr_table.head(10)"""
    ),
    nbf.v4.new_markdown_cell("## Risk Metrics, Alpha/Beta, and Maximum Drawdown"),
    nbf.v4.new_code_cell(
        """def annualized_return(returns: pd.Series) -> float:
    clean = returns.dropna()
    if clean.empty:
        return np.nan
    return (1 + clean).prod() ** (TRADING_DAYS / len(clean)) - 1


def sharpe_ratio(returns: pd.Series) -> float:
    clean = returns.dropna()
    if clean.std(ddof=1) == 0 or clean.empty:
        return np.nan
    excess_daily = clean.mean() - (RISK_FREE_RATE / TRADING_DAYS)
    return excess_daily / clean.std(ddof=1) * np.sqrt(TRADING_DAYS)


def sortino_ratio(returns: pd.Series) -> float:
    clean = returns.dropna()
    downside = clean[clean < 0]
    if downside.std(ddof=1) == 0 or downside.empty:
        return np.nan
    excess_daily = clean.mean() - (RISK_FREE_RATE / TRADING_DAYS)
    return excess_daily / downside.std(ddof=1) * np.sqrt(TRADING_DAYS)


def max_drawdown_details(nav_series: pd.Series) -> dict:
    series = nav_series.dropna().sort_index()
    running_max = series.cummax()
    drawdown = series / running_max - 1
    trough_date = drawdown.idxmin()
    peak_date = series.loc[:trough_date].idxmax()
    recovery = series.loc[trough_date:][series.loc[trough_date:] >= series.loc[peak_date]]
    recovery_date = recovery.index[0] if not recovery.empty else pd.NaT
    return {
        "max_drawdown_pct": drawdown.min() * 100,
        "max_drawdown_peak_date": peak_date,
        "max_drawdown_trough_date": trough_date,
        "max_drawdown_recovery_date": recovery_date,
    }


nifty100_returns = benchmark_returns["NIFTY100"].dropna()

metric_rows = []
for amfi_code, returns in daily_returns.items():
    fund_returns = returns.dropna()
    aligned = pd.concat([fund_returns.rename("fund_return"), nifty100_returns.rename("nifty100_return")], axis=1).dropna()

    if len(aligned) >= 2:
        regression = linregress(aligned["nifty100_return"], aligned["fund_return"])
        beta = regression.slope
        alpha = regression.intercept * TRADING_DAYS
        r_value = regression.rvalue
        p_value = regression.pvalue
    else:
        beta = alpha = r_value = p_value = np.nan

    row = {
        "amfi_code": amfi_code,
        "annualized_return_pct": annualized_return(fund_returns) * 100,
        "annualized_volatility_pct": fund_returns.std(ddof=1) * np.sqrt(TRADING_DAYS) * 100,
        "sharpe_ratio": sharpe_ratio(fund_returns),
        "sortino_ratio": sortino_ratio(fund_returns),
        "alpha_pct": alpha * 100,
        "beta": beta,
        "r_squared": r_value ** 2 if pd.notna(r_value) else np.nan,
        "regression_p_value": p_value,
    }
    row.update(max_drawdown_details(nav_wide[amfi_code]))
    metric_rows.append(row)

metrics = (
    pd.DataFrame(metric_rows)
    .merge(cagr_table[["amfi_code", "cagr_1yr_pct", "cagr_3yr_pct", "cagr_5yr_pct", "cagr_available_period_pct"]], on="amfi_code", how="left")
    .merge(fund_master[["amfi_code", "scheme_name", "fund_house", "category", "plan", "benchmark", "expense_ratio_pct"]], on="amfi_code", how="left")
)

alpha_beta = metrics[
    [
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "plan",
        "alpha_pct",
        "beta",
        "r_squared",
        "regression_p_value",
    ]
].sort_values("alpha_pct", ascending=False)

alpha_beta.to_csv(DATA_DIR / "alpha_beta.csv", index=False)
alpha_beta.head(10)"""
    ),
    nbf.v4.new_markdown_cell("## Fund Scorecard"),
    nbf.v4.new_code_cell(
        """def percentile_score(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    return series.rank(ascending=higher_is_better, pct=True) * 100


scorecard = metrics.copy()
scorecard["return_3yr_score"] = percentile_score(scorecard["cagr_3yr_pct"], higher_is_better=True)
scorecard["sharpe_score"] = percentile_score(scorecard["sharpe_ratio"], higher_is_better=True)
scorecard["alpha_score"] = percentile_score(scorecard["alpha_pct"], higher_is_better=True)
scorecard["expense_ratio_score"] = percentile_score(scorecard["expense_ratio_pct"], higher_is_better=False)
scorecard["max_drawdown_abs_pct"] = scorecard["max_drawdown_pct"].abs()
scorecard["max_drawdown_score"] = percentile_score(scorecard["max_drawdown_abs_pct"], higher_is_better=False)

scorecard["fund_score"] = (
    0.30 * scorecard["return_3yr_score"]
    + 0.25 * scorecard["sharpe_score"]
    + 0.20 * scorecard["alpha_score"]
    + 0.15 * scorecard["expense_ratio_score"]
    + 0.10 * scorecard["max_drawdown_score"]
).round(2)

scorecard["score_rank"] = scorecard["fund_score"].rank(ascending=False, method="dense").astype(int)

scorecard_cols = [
    "score_rank",
    "fund_score",
    "amfi_code",
    "scheme_name",
    "fund_house",
    "category",
    "plan",
    "cagr_1yr_pct",
    "cagr_3yr_pct",
    "cagr_5yr_pct",
    "cagr_available_period_pct",
    "sharpe_ratio",
    "sortino_ratio",
    "alpha_pct",
    "beta",
    "annualized_return_pct",
    "annualized_volatility_pct",
    "expense_ratio_pct",
    "max_drawdown_pct",
    "max_drawdown_peak_date",
    "max_drawdown_trough_date",
    "max_drawdown_recovery_date",
    "return_3yr_score",
    "sharpe_score",
    "alpha_score",
    "expense_ratio_score",
    "max_drawdown_score",
]

fund_scorecard = scorecard[scorecard_cols].sort_values(["score_rank", "fund_score"], ascending=[True, False])
fund_scorecard.to_csv(DATA_DIR / "fund_scorecard.csv", index=False)
fund_scorecard.head(10)"""
    ),
    nbf.v4.new_markdown_cell("## Benchmark Comparison and Tracking Error"),
    nbf.v4.new_code_cell(
        """top5_codes = fund_scorecard.head(5)["amfi_code"].tolist()
end_date = nav_wide.index.max()
start_3yr = end_date - pd.DateOffset(years=3)

top5_nav = nav_wide.loc[nav_wide.index >= start_3yr, top5_codes].dropna(how="all")
top_benchmarks = benchmark_wide.loc[benchmark_wide.index >= start_3yr, ["NIFTY50", "NIFTY100"]]

indexed_funds = top5_nav / top5_nav.iloc[0] * 100
indexed_benchmarks = top_benchmarks / top_benchmarks.iloc[0] * 100

tracking_rows = []
for amfi_code in top5_codes:
    fund_return = daily_returns.loc[daily_returns.index >= start_3yr, amfi_code]
    scheme_name = fund_master.loc[fund_master["amfi_code"] == amfi_code, "scheme_name"].iloc[0]
    for benchmark_name in ["NIFTY50", "NIFTY100"]:
        aligned = pd.concat(
            [
                fund_return.rename("fund_return"),
                benchmark_returns.loc[benchmark_returns.index >= start_3yr, benchmark_name].rename("benchmark_return"),
            ],
            axis=1,
        ).dropna()
        tracking_error = (aligned["fund_return"] - aligned["benchmark_return"]).std(ddof=1) * np.sqrt(TRADING_DAYS)
        tracking_rows.append(
            {
                "amfi_code": amfi_code,
                "scheme_name": scheme_name,
                "benchmark": benchmark_name,
                "tracking_error_pct": tracking_error * 100,
            }
        )

tracking_error_table = pd.DataFrame(tracking_rows)

label_map = fund_master.set_index("amfi_code")["scheme_name"].to_dict()
fig, ax = plt.subplots(figsize=(13, 7))
for amfi_code in top5_codes:
    short_name = label_map[amfi_code].replace(" - Growth", "").replace(" Fund", "")
    ax.plot(indexed_funds.index, indexed_funds[amfi_code], linewidth=1.9, label=short_name)

for benchmark_name, line_style in [("NIFTY50", "--"), ("NIFTY100", ":")]:
    ax.plot(indexed_benchmarks.index, indexed_benchmarks[benchmark_name], color="black", linestyle=line_style, linewidth=2.2, label=benchmark_name)

ax.set_title("Top 5 Funds vs NIFTY50 and NIFTY100 - Indexed Growth Over 3 Years")
ax.set_xlabel("Date")
ax.set_ylabel("Indexed value (start = 100)")
ax.legend(loc="upper left", fontsize=8)
ax.grid(True, alpha=0.25)
fig.tight_layout()
chart_path = CHART_DIR / "benchmark_comparison_top5.png"
fig.savefig(chart_path, dpi=180, bbox_inches="tight")
plt.show()

print(f"Saved chart to {chart_path.relative_to(ROOT)}")
tracking_error_table"""
    ),
    nbf.v4.new_markdown_cell("## Ranked Outputs"),
    nbf.v4.new_code_cell(
        """print("Top 10 funds by score")
display(fund_scorecard.head(10))

print("Top 10 funds by Sharpe Ratio")
display(fund_scorecard.sort_values("sharpe_ratio", ascending=False).head(10))

print("Worst maximum drawdowns")
display(fund_scorecard.sort_values("max_drawdown_pct").head(10))

print("Tracking error for top 5 funds")
display(tracking_error_table.sort_values(["benchmark", "tracking_error_pct"]))"""
    ),
]


def main() -> None:
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    notebook = nbf.v4.new_notebook()
    notebook["cells"] = cells
    notebook["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "pygments_lexer": "ipython3",
        },
    }
    nbf.write(notebook, NOTEBOOK_PATH)
    print(f"Wrote {NOTEBOOK_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
