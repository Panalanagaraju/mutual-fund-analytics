from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nbformat as nbf
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"

VAR_CVAR_PATH = ROOT / "var_cvar_report.csv"
ROLLING_SHARPE_PATH = ROOT / "rolling_sharpe_chart.png"
NOTEBOOK_PATH = ROOT / "Advanced_Analytics.ipynb"

TRADING_DAYS = 252


def load_data():
    nav = pd.read_csv(DATA_DIR / "cleaned_nav_history.csv", parse_dates=["date"])
    funds = pd.read_csv(DATA_DIR / "cleaned_fund_master.csv", parse_dates=["launch_date"])
    txns = pd.read_csv(DATA_DIR / "cleaned_investor_transactions.csv", parse_dates=["transaction_date"])
    holdings = pd.read_csv(DATA_DIR / "cleaned_portfolio_holdings.csv", parse_dates=["portfolio_date"])
    scorecard = pd.read_csv(DATA_DIR / "fund_scorecard.csv")

    nav["amfi_code"] = nav["amfi_code"].astype(int)
    funds["amfi_code"] = funds["amfi_code"].astype(int)
    txns["amfi_code"] = txns["amfi_code"].astype(int)
    holdings["amfi_code"] = holdings["amfi_code"].astype(int)
    scorecard["amfi_code"] = scorecard["amfi_code"].astype(int)
    return nav, funds, txns, holdings, scorecard


def compute_returns(nav):
    nav_wide = nav.sort_values(["date", "amfi_code"]).pivot(index="date", columns="amfi_code", values="nav")
    return nav_wide.pct_change()


def compute_var_cvar(returns, funds):
    rows = []
    for amfi_code in returns.columns:
        series = returns[amfi_code].dropna()
        if series.empty:
            continue
        var_95 = series.quantile(0.05)
        cvar_95 = series[series <= var_95].mean()
        rows.append(
            {
                "amfi_code": int(amfi_code),
                "observations": int(series.count()),
                "var_95_daily_return": var_95,
                "cvar_95_daily_return": cvar_95,
                "var_95_pct": var_95 * 100,
                "cvar_95_pct": cvar_95 * 100,
            }
        )

    report = pd.DataFrame(rows).merge(
        funds[["amfi_code", "scheme_name", "fund_house", "category", "sub_category", "risk_category"]],
        on="amfi_code",
        how="left",
    )
    cols = [
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "sub_category",
        "risk_category",
        "observations",
        "var_95_daily_return",
        "cvar_95_daily_return",
        "var_95_pct",
        "cvar_95_pct",
    ]
    return report[cols].sort_values("var_95_daily_return")


def plot_rolling_sharpe(returns, scorecard):
    top_codes = scorecard.sort_values("score_rank").head(5)["amfi_code"].astype(int).tolist()
    names = scorecard.set_index("amfi_code")["scheme_name"].to_dict()
    rolling = returns[top_codes].rolling(90).mean() / returns[top_codes].rolling(90).std() * np.sqrt(TRADING_DAYS)

    sns.set_theme(style="whitegrid", palette="Set2")
    fig, ax = plt.subplots(figsize=(14, 7))
    for amfi_code in top_codes:
        label = names.get(amfi_code, str(amfi_code)).replace(" - Growth", "")
        ax.plot(rolling.index, rolling[amfi_code], linewidth=1.8, label=label)
    ax.axhline(0, color="#555555", linewidth=0.9, alpha=0.7)
    ax.set_title("Rolling 90-Day Sharpe Ratio: Top 5 Scorecard Funds")
    ax.set_xlabel("Date")
    ax.set_ylabel("Annualized Sharpe")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(ROLLING_SHARPE_PATH, dpi=160)
    plt.close(fig)
    return rolling, top_codes


def compute_cohorts(txns, funds):
    invested_types = {"sip", "purchase", "lumpsum", "switch_in"}
    txns = txns.copy()
    txns["txn_type_norm"] = txns["transaction_type"].str.lower().str.replace(" ", "_")
    txns["is_investment"] = txns["txn_type_norm"].isin(invested_types)
    txns["is_sip"] = txns["txn_type_norm"].eq("sip")
    first_year = txns.groupby("investor_id")["transaction_date"].min().dt.year.rename("first_transaction_year")
    txns = txns.join(first_year, on="investor_id")

    base = (
        txns.groupby("first_transaction_year")
        .agg(
            investor_count=("investor_id", "nunique"),
            avg_sip_amount=("amount_inr", lambda s: s[txns.loc[s.index, "is_sip"]].mean()),
            total_invested=("amount_inr", lambda s: s[txns.loc[s.index, "is_investment"]].sum()),
        )
        .reset_index()
    )

    pref = (
        txns[txns["is_investment"]]
        .groupby(["first_transaction_year", "amfi_code"], as_index=False)["amount_inr"]
        .sum()
        .sort_values(["first_transaction_year", "amount_inr"], ascending=[True, False])
        .drop_duplicates("first_transaction_year")
        .merge(funds[["amfi_code", "scheme_name"]], on="amfi_code", how="left")
        .rename(columns={"scheme_name": "top_fund_preference", "amount_inr": "top_fund_invested"})
    )
    return base.merge(
        pref[["first_transaction_year", "top_fund_preference", "top_fund_invested"]],
        on="first_transaction_year",
        how="left",
    ).sort_values("first_transaction_year")


def compute_sip_continuity(txns):
    sip = txns[txns["transaction_type"].str.lower().str.replace(" ", "_").eq("sip")].copy()
    sip = sip.sort_values(["investor_id", "transaction_date"])
    eligible = sip.groupby("investor_id").filter(lambda frame: len(frame) >= 6).copy()
    eligible["gap_days"] = eligible.groupby("investor_id")["transaction_date"].diff().dt.days
    continuity = (
        eligible.groupby("investor_id")
        .agg(
            sip_transactions=("transaction_date", "count"),
            avg_gap_days=("gap_days", "mean"),
            max_gap_days=("gap_days", "max"),
            total_sip_amount=("amount_inr", "sum"),
        )
        .reset_index()
    )
    continuity["status"] = np.where(continuity["avg_gap_days"] > 35, "at-risk", "continuous")
    return continuity.sort_values(["status", "avg_gap_days"], ascending=[True, False])


def compute_hhi(holdings, funds):
    latest = holdings["portfolio_date"].max()
    hhi = (
        holdings[holdings["portfolio_date"].eq(latest)]
        .assign(weight_share=lambda frame: frame["weight_pct"] / 100)
        .groupby("amfi_code", as_index=False)
        .agg(hhi=("weight_share", lambda s: float(np.square(s).sum())), holdings_count=("stock_symbol", "nunique"))
        .merge(funds[["amfi_code", "scheme_name", "category", "sub_category"]], on="amfi_code", how="left")
    )
    hhi = hhi[hhi["category"].str.lower().eq("equity")].copy()
    hhi["concentration_band"] = pd.cut(
        hhi["hhi"],
        bins=[-np.inf, 0.10, 0.18, np.inf],
        labels=["Diversified", "Moderate", "Concentrated"],
    )
    return hhi.sort_values("hhi", ascending=False)


def recommendation_table(scorecard, funds):
    merged = scorecard.merge(funds[["amfi_code", "risk_category", "sub_category"]], on="amfi_code", how="left")
    return merged[["scheme_name", "fund_house", "sub_category", "risk_category", "sharpe_ratio", "fund_score"]]


def build_insights(var_cvar, cohorts, continuity, hhi):
    worst_var = var_cvar.iloc[0]
    worst_cvar = var_cvar.sort_values("cvar_95_daily_return").iloc[0]
    top_cohort = cohorts.sort_values("total_invested", ascending=False).iloc[0]
    eligible = len(continuity)
    at_risk = int((continuity["status"] == "at-risk").sum())
    continuity_rate = (eligible - at_risk) / eligible if eligible else np.nan
    concentrated = hhi.iloc[0]

    return [
        f"{worst_var['scheme_name']} has the deepest 95% historical VaR at {worst_var['var_95_pct']:.2f}% daily return, making it the weakest left-tail fund in the sample.",
        f"{worst_cvar['scheme_name']} has the harshest CVaR at {worst_cvar['cvar_95_pct']:.2f}%, so losses beyond its VaR threshold are the most severe on average.",
        f"The {int(top_cohort['first_transaction_year'])} investor cohort contributes the highest total investment at INR {top_cohort['total_invested']:,.0f}; its preferred fund is {top_cohort['top_fund_preference']}.",
        f"Among {eligible:,} investors with at least 6 SIPs, {continuity_rate:.1%} remain continuous by the 35-day average-gap rule and {at_risk:,} are flagged at-risk.",
        f"{concentrated['scheme_name']} is the most sector/security concentrated equity portfolio with HHI {concentrated['hhi']:.3f}, based on the latest holdings snapshot.",
    ]


def create_notebook(insights):
    cells = [
        nbf.v4.new_markdown_cell(
            """# Advanced Analytics

This notebook covers tail risk, rolling Sharpe, investor cohorts, SIP continuity, risk-appetite recommendations, and equity portfolio concentration for the 40 mutual fund schemes."""
        ),
        nbf.v4.new_code_cell(
            """from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path.cwd()
DATA_DIR = ROOT / "data" / "processed"
TRADING_DAYS = 252

nav = pd.read_csv(DATA_DIR / "cleaned_nav_history.csv", parse_dates=["date"])
funds = pd.read_csv(DATA_DIR / "cleaned_fund_master.csv", parse_dates=["launch_date"])
txns = pd.read_csv(DATA_DIR / "cleaned_investor_transactions.csv", parse_dates=["transaction_date"])
holdings = pd.read_csv(DATA_DIR / "cleaned_portfolio_holdings.csv", parse_dates=["portfolio_date"])
scorecard = pd.read_csv(DATA_DIR / "fund_scorecard.csv")

for frame in [nav, funds, txns, holdings, scorecard]:
    if "amfi_code" in frame.columns:
        frame["amfi_code"] = frame["amfi_code"].astype(int)

returns = nav.sort_values(["date", "amfi_code"]).pivot(index="date", columns="amfi_code", values="nav").pct_change()
print(f"Schemes: {returns.shape[1]}; NAV dates: {returns.index.min().date()} to {returns.index.max().date()}")"""
        ),
        nbf.v4.new_markdown_cell("## Historical VaR and CVaR"),
        nbf.v4.new_code_cell(
            """var_cvar = []
for amfi_code in returns.columns:
    r = returns[amfi_code].dropna()
    var_95 = r.quantile(0.05)
    cvar_95 = r[r <= var_95].mean()
    var_cvar.append({"amfi_code": int(amfi_code), "observations": len(r), "var_95_daily_return": var_95, "cvar_95_daily_return": cvar_95, "var_95_pct": var_95 * 100, "cvar_95_pct": cvar_95 * 100})

var_cvar_report = pd.DataFrame(var_cvar).merge(
    funds[["amfi_code", "scheme_name", "fund_house", "category", "sub_category", "risk_category"]],
    on="amfi_code",
    how="left",
).sort_values("var_95_daily_return")
var_cvar_report.to_csv(ROOT / "var_cvar_report.csv", index=False)
var_cvar_report.head(10)"""
        ),
        nbf.v4.new_markdown_cell("## Rolling 90-Day Sharpe"),
        nbf.v4.new_code_cell(
            """top_codes = scorecard.sort_values("score_rank").head(5)["amfi_code"].astype(int).tolist()
rolling_sharpe = returns[top_codes].rolling(90).mean() / returns[top_codes].rolling(90).std() * np.sqrt(TRADING_DAYS)
names = scorecard.set_index("amfi_code")["scheme_name"].to_dict()

sns.set_theme(style="whitegrid", palette="Set2")
fig, ax = plt.subplots(figsize=(14, 7))
for amfi_code in top_codes:
    ax.plot(rolling_sharpe.index, rolling_sharpe[amfi_code], label=names.get(amfi_code, str(amfi_code)).replace(" - Growth", ""))
ax.axhline(0, color="#555555", linewidth=0.9, alpha=0.7)
ax.set_title("Rolling 90-Day Sharpe Ratio: Top 5 Scorecard Funds")
ax.set_xlabel("Date")
ax.set_ylabel("Annualized Sharpe")
ax.legend(loc="best", fontsize=8)
fig.tight_layout()
fig.savefig(ROOT / "rolling_sharpe_chart.png", dpi=160)
plt.show()"""
        ),
        nbf.v4.new_markdown_cell("## Investor Cohort Analysis"),
        nbf.v4.new_code_cell(
            """tx = txns.copy()
tx["txn_type_norm"] = tx["transaction_type"].str.lower().str.replace(" ", "_")
tx["is_investment"] = tx["txn_type_norm"].isin(["sip", "purchase", "lumpsum", "switch_in"])
tx["is_sip"] = tx["txn_type_norm"].eq("sip")
tx["first_transaction_year"] = tx.groupby("investor_id")["transaction_date"].transform("min").dt.year

cohorts = tx.groupby("first_transaction_year").agg(
    investor_count=("investor_id", "nunique"),
    avg_sip_amount=("amount_inr", lambda s: s[tx.loc[s.index, "is_sip"]].mean()),
    total_invested=("amount_inr", lambda s: s[tx.loc[s.index, "is_investment"]].sum()),
).reset_index()

top_funds = (
    tx[tx["is_investment"]]
    .groupby(["first_transaction_year", "amfi_code"], as_index=False)["amount_inr"]
    .sum()
    .sort_values(["first_transaction_year", "amount_inr"], ascending=[True, False])
    .drop_duplicates("first_transaction_year")
    .merge(funds[["amfi_code", "scheme_name"]], on="amfi_code", how="left")
)
cohorts = cohorts.merge(top_funds[["first_transaction_year", "scheme_name", "amount_inr"]], on="first_transaction_year", how="left")
cohorts.rename(columns={"scheme_name": "top_fund_preference", "amount_inr": "top_fund_invested"}, inplace=True)
cohorts"""
        ),
        nbf.v4.new_markdown_cell("## SIP Continuity Analysis"),
        nbf.v4.new_code_cell(
            """sip = tx[tx["is_sip"]].sort_values(["investor_id", "transaction_date"]).copy()
eligible = sip.groupby("investor_id").filter(lambda frame: len(frame) >= 6)
eligible["gap_days"] = eligible.groupby("investor_id")["transaction_date"].diff().dt.days
sip_continuity = eligible.groupby("investor_id").agg(
    sip_transactions=("transaction_date", "count"),
    avg_gap_days=("gap_days", "mean"),
    max_gap_days=("gap_days", "max"),
    total_sip_amount=("amount_inr", "sum"),
).reset_index()
sip_continuity["status"] = np.where(sip_continuity["avg_gap_days"] > 35, "at-risk", "continuous")
sip_continuity["status"].value_counts(normalize=True).rename("share")"""
        ),
        nbf.v4.new_markdown_cell("## Simple Fund Recommender"),
        nbf.v4.new_code_cell(
            """risk_map = {
    "Low": ["Low", "Low to Moderate", "Moderately Low"],
    "Moderate": ["Moderate", "Moderately High"],
    "High": ["High", "Very High"],
}

def recommend(risk_appetite):
    grades = risk_map[risk_appetite]
    table = scorecard.merge(funds[["amfi_code", "risk_category", "sub_category"]], on="amfi_code", how="left")
    return table[table["risk_category"].isin(grades)].sort_values("sharpe_ratio", ascending=False).head(3)[
        ["scheme_name", "fund_house", "sub_category", "risk_category", "sharpe_ratio", "fund_score"]
    ]

recommend("Moderate")"""
        ),
        nbf.v4.new_markdown_cell("## Sector HHI Concentration"),
        nbf.v4.new_code_cell(
            """latest_portfolio_date = holdings["portfolio_date"].max()
hhi = (
    holdings[holdings["portfolio_date"].eq(latest_portfolio_date)]
    .assign(weight_share=lambda frame: frame["weight_pct"] / 100)
    .groupby("amfi_code", as_index=False)
    .agg(hhi=("weight_share", lambda s: float(np.square(s).sum())), holdings_count=("stock_symbol", "nunique"))
    .merge(funds[["amfi_code", "scheme_name", "category", "sub_category"]], on="amfi_code", how="left")
)
hhi = hhi[hhi["category"].str.lower().eq("equity")].sort_values("hhi", ascending=False)
hhi.head(10)"""
        ),
        nbf.v4.new_markdown_cell(
            "## Advanced Insights\n\n" + "\n".join(f"{idx}. {text}" for idx, text in enumerate(insights, start=1))
        ),
    ]
    notebook = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}})
    nbf.write(notebook, NOTEBOOK_PATH)


def main():
    nav, funds, txns, holdings, scorecard = load_data()
    returns = compute_returns(nav)
    var_cvar = compute_var_cvar(returns, funds)
    var_cvar.to_csv(VAR_CVAR_PATH, index=False)
    plot_rolling_sharpe(returns, scorecard)
    cohorts = compute_cohorts(txns, funds)
    continuity = compute_sip_continuity(txns)
    hhi = compute_hhi(holdings, funds)
    insights = build_insights(var_cvar, cohorts, continuity, hhi)
    create_notebook(insights)

    print(f"Wrote {VAR_CVAR_PATH.relative_to(ROOT)} ({len(var_cvar)} funds)")
    print(f"Wrote {ROLLING_SHARPE_PATH.relative_to(ROOT)}")
    print(f"Wrote {NOTEBOOK_PATH.relative_to(ROOT)}")
    print("Advanced insights:")
    for insight in insights:
        print(f"- {insight}")


if __name__ == "__main__":
    main()
