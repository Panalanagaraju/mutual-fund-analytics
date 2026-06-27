from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "EDA_Analysis.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


cells = [
    md(
        """
        # Mutual Fund EDA Analysis

        This notebook completes the EDA deliverables:

        1. NAV trend analysis for all 40 schemes from 2022-2026.
        2. AUM growth grouped bar chart by fund house from 2022-2025.
        3. SIP inflow time series from Jan 2022-Dec 2025.
        4. Category inflow heatmap.
        5. Investor demographics charts.
        6. Geographic SIP distribution charts.
        7. Folio count growth analysis.
        8. NAV return correlation matrix for 10 selected funds.
        9. Sector allocation donut from portfolio holdings.
        10. Ten EDA findings with chart references.

        PNG charts are exported to `../charts/eda/`.
        """
    ),
    md(
        """
        ## Step 1: Import libraries and define paths

        Run this cell first. It loads plotting libraries, sets chart styling, and creates the chart export folder.
        """
    ),
    code(
        r"""
        from pathlib import Path
        import warnings

        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
        import plotly.express as px
        import plotly.graph_objects as go

        warnings.filterwarnings("ignore")

        PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
        DATA_DIR = PROJECT_ROOT / "data" / "processed"
        CHART_DIR = PROJECT_ROOT / "charts" / "eda"
        CHART_DIR.mkdir(parents=True, exist_ok=True)

        sns.set_theme(style="whitegrid", palette="Set2")
        plt.rcParams["figure.figsize"] = (12, 6)
        plt.rcParams["axes.titlesize"] = 14
        plt.rcParams["axes.labelsize"] = 11
        plt.rcParams["savefig.dpi"] = 180

        def save_matplotlib(name: str):
            # Save the current Matplotlib/Seaborn figure as a PNG.
            path = CHART_DIR / f"{name}.png"
            plt.tight_layout()
            plt.savefig(path, bbox_inches="tight")
            print(f"Saved: {path.relative_to(PROJECT_ROOT)}")

        def save_plotly_html(fig, name: str):
            # Save interactive Plotly output as HTML. Static PNG counterparts are created separately.
            path = CHART_DIR / f"{name}.html"
            fig.write_html(path)
            print(f"Saved: {path.relative_to(PROJECT_ROOT)}")
        """
    ),
    md(
        """
        ## Step 2: Load cleaned datasets

        The project already has cleaned CSVs in `data/processed`. We parse date columns immediately so filtering and plotting behave correctly.
        """
    ),
    code(
        r"""
        fund_master = pd.read_csv(DATA_DIR / "cleaned_fund_master.csv", parse_dates=["launch_date"])
        nav = pd.read_csv(DATA_DIR / "cleaned_nav_history.csv", parse_dates=["date"])
        aum = pd.read_csv(DATA_DIR / "cleaned_aum_by_fund_house.csv", parse_dates=["date"])
        sip = pd.read_csv(DATA_DIR / "cleaned_monthly_sip_inflows.csv")
        category_inflows = pd.read_csv(DATA_DIR / "cleaned_category_inflows.csv")
        folios = pd.read_csv(DATA_DIR / "cleaned_industry_folio_count.csv")
        transactions = pd.read_csv(DATA_DIR / "cleaned_investor_transactions.csv", parse_dates=["transaction_date"])
        holdings = pd.read_csv(DATA_DIR / "cleaned_portfolio_holdings.csv", parse_dates=["portfolio_date"])
        performance = pd.read_csv(DATA_DIR / "cleaned_scheme_performance.csv")

        sip["month"] = pd.to_datetime(sip["month"])
        category_inflows["month"] = pd.to_datetime(category_inflows["month"])
        folios["month"] = pd.to_datetime(folios["month"])

        nav = nav.merge(
            fund_master[["amfi_code", "scheme_name", "fund_house", "category", "sub_category", "plan"]],
            on="amfi_code",
            how="left",
        )

        print("Fund schemes:", fund_master["amfi_code"].nunique())
        print("NAV date range:", nav["date"].min().date(), "to", nav["date"].max().date())
        print("SIP date range:", sip["month"].min().date(), "to", sip["month"].max().date())
        """
    ),
    md(
        """
        ## Step 3: NAV trend analysis for all 40 schemes

        Chart 1 uses Plotly and highlights the 2023 bull run plus 2024 correction period with shaded regions.
        """
    ),
    code(
        r"""
        nav_2022_2026 = nav[(nav["date"] >= "2022-01-01") & (nav["date"] <= "2026-12-31")].copy()

        fig = px.line(
            nav_2022_2026,
            x="date",
            y="nav",
            color="scheme_name",
            hover_data=["fund_house", "sub_category", "plan"],
            title="Chart 1: Daily NAV Trend for All 40 Schemes, 2022-2026",
            labels={"date": "Date", "nav": "NAV", "scheme_name": "Scheme"},
        )
        fig.add_vrect(
            x0="2023-03-01", x1="2023-12-31",
            fillcolor="rgba(34, 139, 34, 0.15)", line_width=0,
            annotation_text="2023 bull run", annotation_position="top left",
        )
        fig.add_vrect(
            x0="2024-06-01", x1="2024-11-30",
            fillcolor="rgba(220, 20, 60, 0.12)", line_width=0,
            annotation_text="2024 corrections", annotation_position="top left",
        )
        fig.update_layout(height=720, legend=dict(font=dict(size=8)))
        save_plotly_html(fig, "01_nav_trend_all_40_plotly")
        fig.show()
        """
    ),
    code(
        r"""
        plt.figure(figsize=(15, 8))
        sns.lineplot(data=nav_2022_2026, x="date", y="nav", hue="scheme_name", linewidth=0.8, legend=False)
        plt.axvspan(pd.Timestamp("2023-03-01"), pd.Timestamp("2023-12-31"), color="green", alpha=0.10, label="2023 bull run")
        plt.axvspan(pd.Timestamp("2024-06-01"), pd.Timestamp("2024-11-30"), color="red", alpha=0.08, label="2024 corrections")
        plt.title("Chart 1 PNG: Daily NAV Trend for All 40 Schemes, 2022-2026")
        plt.xlabel("Date")
        plt.ylabel("NAV")
        plt.legend()
        save_matplotlib("01_nav_trend_all_40")
        plt.show()
        """
    ),
    md(
        """
        ## Step 4: Indexed NAV comparison

        Chart 2 rebases every scheme to 100 on its first available NAV date. This makes relative growth easier to compare than raw NAV levels.
        """
    ),
    code(
        r"""
        nav_indexed = nav_2022_2026.sort_values(["amfi_code", "date"]).copy()
        nav_indexed["base_nav"] = nav_indexed.groupby("amfi_code")["nav"].transform("first")
        nav_indexed["indexed_nav"] = nav_indexed["nav"] / nav_indexed["base_nav"] * 100

        plt.figure(figsize=(15, 8))
        sns.lineplot(data=nav_indexed, x="date", y="indexed_nav", hue="scheme_name", linewidth=0.8, legend=False)
        plt.axvspan(pd.Timestamp("2023-03-01"), pd.Timestamp("2023-12-31"), color="green", alpha=0.10)
        plt.axvspan(pd.Timestamp("2024-06-01"), pd.Timestamp("2024-11-30"), color="red", alpha=0.08)
        plt.title("Chart 2: Indexed NAV Growth for All Schemes, Base = 100")
        plt.xlabel("Date")
        plt.ylabel("Indexed NAV")
        save_matplotlib("02_indexed_nav_growth")
        plt.show()
        """
    ),
    md(
        """
        ## Step 5: AUM growth grouped bar chart by fund house

        Chart 3 groups annual AUM by fund house and highlights SBI Mutual Fund's `12.5` lakh crore dominance.
        """
    ),
    code(
        r"""
        aum["year"] = aum["date"].dt.year
        annual_aum = (
            aum[aum["year"].between(2022, 2025)]
            .sort_values("date")
            .groupby(["year", "fund_house"], as_index=False)
            .tail(1)
        )

        plt.figure(figsize=(15, 7))
        ax = sns.barplot(data=annual_aum, x="fund_house", y="aum_lakh_crore", hue="year", palette="viridis")
        sbi_2025 = annual_aum[(annual_aum["fund_house"].str.contains("SBI", case=False)) & (annual_aum["year"] == 2025)]
        if not sbi_2025.empty:
            row = sbi_2025.iloc[0]
            ax.annotate(
                "SBI dominance: ₹12.5L Cr",
                xy=(list(annual_aum["fund_house"].unique()).index(row["fund_house"]), row["aum_lakh_crore"]),
                xytext=(0, 25),
                textcoords="offset points",
                ha="center",
                arrowprops=dict(arrowstyle="->", color="black"),
                fontsize=11,
                weight="bold",
            )
        plt.title("Chart 3: AUM Growth by Fund House, 2022-2025")
        plt.xlabel("Fund House")
        plt.ylabel("AUM (₹ lakh crore)")
        plt.xticks(rotation=45, ha="right")
        save_matplotlib("03_aum_grouped_bar_fund_house")
        plt.show()
        """
    ),
    code(
        r"""
        plt.figure(figsize=(11, 6))
        latest_aum = annual_aum[annual_aum["year"] == annual_aum["year"].max()].sort_values("aum_lakh_crore", ascending=False)
        sns.barplot(data=latest_aum, y="fund_house", x="aum_lakh_crore", palette="crest")
        plt.title("Chart 4: Latest Fund House AUM Ranking")
        plt.xlabel("AUM (₹ lakh crore)")
        plt.ylabel("Fund House")
        save_matplotlib("04_latest_aum_ranking")
        plt.show()
        """
    ),
    md(
        """
        ## Step 6: SIP inflow time series

        Chart 5 uses Plotly for monthly SIP inflows from Jan 2022-Dec 2025 and annotates the all-time high of `₹31,002 Cr` in Dec 2025.
        """
    ),
    code(
        r"""
        fig = px.line(
            sip,
            x="month",
            y="sip_inflow_crore",
            markers=True,
            title="Chart 5: Monthly SIP Inflow Trend, Jan 2022-Dec 2025",
            labels={"month": "Month", "sip_inflow_crore": "SIP Inflow (₹ crore)"},
        )
        max_sip = sip.loc[sip["sip_inflow_crore"].idxmax()]
        fig.add_annotation(
            x=max_sip["month"],
            y=max_sip["sip_inflow_crore"],
            text=f"All-time high: ₹{max_sip['sip_inflow_crore']:,.0f} Cr<br>{max_sip['month'].strftime('%b %Y')}",
            showarrow=True,
            arrowhead=2,
            ax=-90,
            ay=-70,
        )
        fig.update_layout(height=520)
        save_plotly_html(fig, "05_sip_inflow_time_series_plotly")
        fig.show()
        """
    ),
    code(
        r"""
        plt.figure(figsize=(14, 6))
        sns.lineplot(data=sip, x="month", y="sip_inflow_crore", marker="o", linewidth=2.2)
        plt.scatter(max_sip["month"], max_sip["sip_inflow_crore"], color="crimson", s=90, zorder=5)
        plt.annotate(
            f"₹{max_sip['sip_inflow_crore']:,.0f} Cr all-time high\n{max_sip['month'].strftime('%b %Y')}",
            xy=(max_sip["month"], max_sip["sip_inflow_crore"]),
            xytext=(-140, -65),
            textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color="black"),
            fontsize=10,
        )
        plt.title("Chart 5 PNG: Monthly SIP Inflow Trend")
        plt.xlabel("Month")
        plt.ylabel("SIP Inflow (₹ crore)")
        save_matplotlib("05_sip_inflow_time_series")
        plt.show()
        """
    ),
    code(
        r"""
        plt.figure(figsize=(14, 6))
        sns.lineplot(data=sip, x="month", y="active_sip_accounts_crore", marker="o", label="Active SIP accounts")
        sns.lineplot(data=sip, x="month", y="sip_aum_lakh_crore", marker="s", label="SIP AUM")
        plt.title("Chart 6: Active SIP Accounts and SIP AUM Growth")
        plt.xlabel("Month")
        plt.ylabel("Count / AUM")
        plt.legend()
        save_matplotlib("06_sip_accounts_and_aum")
        plt.show()
        """
    ),
    md(
        """
        ## Step 7: Category inflow heatmap

        Chart 7 puts months on the X-axis, fund categories on the Y-axis, and net inflow as colour intensity.
        """
    ),
    code(
        r"""
        category_inflows["month_label"] = category_inflows["month"].dt.strftime("%Y-%m")
        heatmap_data = category_inflows.pivot_table(
            index="category",
            columns="month_label",
            values="net_inflow_crore",
            aggfunc="sum",
        )

        plt.figure(figsize=(18, 5))
        sns.heatmap(heatmap_data, cmap="RdYlGn", center=0, linewidths=0.2, linecolor="white")
        plt.title("Chart 7: Category-wise Monthly Net Inflow Heatmap")
        plt.xlabel("Month")
        plt.ylabel("Fund Category")
        save_matplotlib("07_category_inflow_heatmap")
        plt.show()
        """
    ),
    code(
        r"""
        category_annual = category_inflows.assign(year=category_inflows["month"].dt.year)
        category_annual = category_annual.groupby(["year", "category"], as_index=False)["net_inflow_crore"].sum()

        plt.figure(figsize=(13, 6))
        sns.barplot(data=category_annual, x="year", y="net_inflow_crore", hue="category", palette="tab10")
        plt.title("Chart 8: Annual Net Inflows by Fund Category")
        plt.xlabel("Year")
        plt.ylabel("Net Inflow (₹ crore)")
        save_matplotlib("08_annual_category_inflows")
        plt.show()
        """
    ),
    md(
        """
        ## Step 8: Investor demographics

        These charts cover age group distribution, SIP amount by age group, and gender split.
        """
    ),
    code(
        r"""
        sip_txn = transactions[transactions["transaction_type"].str.upper().eq("SIP")].copy()

        age_counts = transactions["age_group"].value_counts().sort_index()
        plt.figure(figsize=(8, 8))
        plt.pie(age_counts, labels=age_counts.index, autopct="%1.1f%%", startangle=90, wedgeprops=dict(width=0.95))
        plt.title("Chart 9: Investor Age Group Distribution")
        save_matplotlib("09_age_group_distribution_pie")
        plt.show()
        """
    ),
    code(
        r"""
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=sip_txn, x="age_group", y="amount_inr", palette="Set3")
        plt.title("Chart 10: SIP Amount Distribution by Age Group")
        plt.xlabel("Age Group")
        plt.ylabel("SIP Amount (₹)")
        save_matplotlib("10_sip_amount_boxplot_age_group")
        plt.show()
        """
    ),
    code(
        r"""
        gender_counts = transactions["gender"].value_counts()
        plt.figure(figsize=(8, 6))
        sns.barplot(x=gender_counts.index, y=gender_counts.values, palette="muted")
        plt.title("Chart 11: Investor Gender Split")
        plt.xlabel("Gender")
        plt.ylabel("Number of Transactions")
        for i, v in enumerate(gender_counts.values):
            plt.text(i, v, f"{v:,}", ha="center", va="bottom")
        save_matplotlib("11_gender_split")
        plt.show()
        """
    ),
    md(
        """
        ## Step 9: Geographic distribution

        These charts show SIP amount by state and T30 versus B30 city tier contribution.
        """
    ),
    code(
        r"""
        state_sip = (
            sip_txn.groupby("state", as_index=False)["amount_inr"]
            .sum()
            .sort_values("amount_inr", ascending=False)
            .head(15)
        )
        state_sip["amount_crore"] = state_sip["amount_inr"] / 1e7

        plt.figure(figsize=(12, 8))
        sns.barplot(data=state_sip, y="state", x="amount_crore", palette="mako")
        plt.title("Chart 12: Top States by SIP Amount")
        plt.xlabel("SIP Amount (₹ crore)")
        plt.ylabel("State")
        save_matplotlib("12_sip_amount_by_state")
        plt.show()
        """
    ),
    code(
        r"""
        tier_sip = sip_txn.groupby("city_tier", as_index=False)["amount_inr"].sum()
        plt.figure(figsize=(7, 7))
        plt.pie(tier_sip["amount_inr"], labels=tier_sip["city_tier"], autopct="%1.1f%%", startangle=90)
        plt.title("Chart 13: SIP Amount Split by City Tier, T30 vs B30")
        save_matplotlib("13_t30_b30_city_tier_pie")
        plt.show()
        """
    ),
    md(
        """
        ## Step 10: Folio count growth

        Chart 14 traces total folios from `13.26 Cr` in Jan 2022 to `26.12 Cr` in Dec 2025 and marks key milestones.
        """
    ),
    code(
        r"""
        plt.figure(figsize=(14, 6))
        sns.lineplot(data=folios, x="month", y="total_folios_crore", marker="o", linewidth=2.4)

        milestone_values = [15, 20, 25]
        for milestone in milestone_values:
            reached = folios[folios["total_folios_crore"] >= milestone]
            if not reached.empty:
                row = reached.iloc[0]
                plt.scatter(row["month"], row["total_folios_crore"], s=80)
                plt.annotate(
                    f"{milestone} Cr milestone\n{row['month'].strftime('%b %Y')}",
                    xy=(row["month"], row["total_folios_crore"]),
                    xytext=(10, 20),
                    textcoords="offset points",
                    arrowprops=dict(arrowstyle="->"),
                    fontsize=9,
                )

        first, last = folios.iloc[0], folios.iloc[-1]
        plt.annotate(f"{first['total_folios_crore']:.2f} Cr", xy=(first["month"], first["total_folios_crore"]), xytext=(8, -28), textcoords="offset points")
        plt.annotate(f"{last['total_folios_crore']:.2f} Cr", xy=(last["month"], last["total_folios_crore"]), xytext=(-70, 15), textcoords="offset points")
        plt.title("Chart 14: Industry Folio Count Growth")
        plt.xlabel("Month")
        plt.ylabel("Total Folios (crore)")
        save_matplotlib("14_folio_count_growth")
        plt.show()
        """
    ),
    code(
        r"""
        folio_long = folios.melt(
            id_vars="month",
            value_vars=["equity_folios_crore", "debt_folios_crore", "hybrid_folios_crore", "others_folios_crore"],
            var_name="folio_type",
            value_name="folios_crore",
        )
        folio_long["folio_type"] = folio_long["folio_type"].str.replace("_folios_crore", "", regex=False).str.title()

        plt.figure(figsize=(14, 6))
        sns.lineplot(data=folio_long, x="month", y="folios_crore", hue="folio_type", marker="o")
        plt.title("Chart 15: Folio Growth by Category")
        plt.xlabel("Month")
        plt.ylabel("Folios (crore)")
        save_matplotlib("15_folio_growth_by_category")
        plt.show()
        """
    ),
    md(
        """
        ## Step 11: NAV return correlation matrix

        Chart 16 computes daily percentage returns for 10 selected funds and plots their pairwise correlations.
        """
    ),
    code(
        r"""
        selected_codes = (
            performance.sort_values("aum_crore", ascending=False)
            .head(10)["amfi_code"]
            .tolist()
        )
        selected_nav = nav[nav["amfi_code"].isin(selected_codes)].copy()
        selected_names = fund_master.set_index("amfi_code").loc[selected_codes, "scheme_name"].to_dict()
        selected_nav["scheme_label"] = selected_nav["amfi_code"].map(selected_names).str.replace(" - Growth", "", regex=False).str.slice(0, 32)

        nav_wide = selected_nav.pivot_table(index="date", columns="scheme_label", values="nav").sort_index()
        returns = nav_wide.pct_change().dropna(how="all")
        corr = returns.corr()

        plt.figure(figsize=(11, 9))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", vmin=-1, vmax=1, square=True, linewidths=0.5)
        plt.title("Chart 16: Daily NAV Return Correlation Matrix for 10 Selected Funds")
        save_matplotlib("16_nav_return_correlation_heatmap")
        plt.show()
        """
    ),
    md(
        """
        ## Step 12: Sector allocation donut

        Chart 17 aggregates sector weights from `portfolio_holdings.csv` across all equity funds.
        """
    ),
    code(
        r"""
        equity_codes = fund_master[fund_master["category"].str.contains("Equity", case=False, na=False)]["amfi_code"]
        sector_alloc = (
            holdings[holdings["amfi_code"].isin(equity_codes)]
            .groupby("sector", as_index=False)["weight_pct"]
            .sum()
            .sort_values("weight_pct", ascending=False)
        )

        plt.figure(figsize=(9, 9))
        plt.pie(
            sector_alloc["weight_pct"],
            labels=sector_alloc["sector"],
            autopct="%1.1f%%",
            startangle=90,
            pctdistance=0.78,
            wedgeprops=dict(width=0.38, edgecolor="white"),
        )
        plt.title("Chart 17: Aggregate Equity Fund Sector Allocation")
        save_matplotlib("17_sector_allocation_donut")
        plt.show()
        """
    ),
    md(
        """
        ## Step 13: Extra EDA charts for final report

        These additional charts help the report cross the 15-chart requirement and give broader context.
        """
    ),
    code(
        r"""
        plt.figure(figsize=(12, 6))
        sns.scatterplot(
            data=performance,
            x="std_dev_ann_pct",
            y="return_3yr_pct",
            hue="category",
            size="aum_crore",
            sizes=(40, 500),
            alpha=0.75,
        )
        plt.title("Chart 18: Risk vs 3-Year Return by Scheme")
        plt.xlabel("Annualized Standard Deviation (%)")
        plt.ylabel("3-Year Return (%)")
        save_matplotlib("18_risk_return_scatter")
        plt.show()
        """
    ),
    code(
        r"""
        plt.figure(figsize=(12, 6))
        top_alpha = performance.sort_values("alpha", ascending=False).head(12)
        sns.barplot(data=top_alpha, y="scheme_name", x="alpha", palette="flare")
        plt.title("Chart 19: Top Schemes by Alpha")
        plt.xlabel("Alpha")
        plt.ylabel("Scheme")
        save_matplotlib("19_top_schemes_by_alpha")
        plt.show()
        """
    ),
    code(
        r"""
        plt.figure(figsize=(11, 6))
        sns.boxplot(data=performance, x="category", y="expense_ratio_pct", palette="Pastel1")
        plt.title("Chart 20: Expense Ratio Distribution by Category")
        plt.xlabel("Category")
        plt.ylabel("Expense Ratio (%)")
        save_matplotlib("20_expense_ratio_by_category")
        plt.show()
        """
    ),
    md(
        """
        ## Step 14: Ten key EDA findings

        Each finding is one insight sentence and references its supporting chart.
        """
    ),
    md("1. **NAV growth was broadly positive across schemes during the highlighted 2023 bull run**, visible in Chart 1 and clearer after rebasing in Chart 2."),
    md("2. **The 2024 correction period created visible temporary NAV softness across many schemes**, especially in the shaded region of Charts 1 and 2."),
    md("3. **SBI Mutual Fund is the dominant AMC by AUM at ₹12.5 lakh crore**, directly annotated in Chart 3 and ranked first in Chart 4."),
    md("4. **Monthly SIP inflows rose strongly from 2022 to 2025 and reached a high of ₹31,002 crore in Dec 2025**, shown in Chart 5."),
    md("5. **Active SIP accounts and SIP AUM expanded alongside inflows**, indicating that growth came from both participation and asset accumulation, as shown in Chart 6."),
    md("6. **Category inflows vary materially month to month, with stronger and weaker pockets visible by colour intensity**, shown in Chart 7."),
    md("7. **Investor participation is concentrated in specific age groups, while SIP ticket sizes differ by age band**, shown in Charts 9 and 10."),
    md("8. **Top states contribute a disproportionate share of SIP amount**, shown by the steep ranking in Chart 12."),
    md("9. **Industry folios almost doubled from 13.26 crore in Jan 2022 to 26.12 crore in Dec 2025**, with milestones marked in Chart 14."),
    md("10. **Selected large funds show meaningful positive daily-return correlation, suggesting shared market-factor exposure**, shown in Chart 16."),
    md(
        """
        ## Step 15: Export checklist

        After running all cells, confirm that `../charts/eda/` contains at least 15 PNG files plus the Plotly HTML files.
        """
    ),
    code(
        r"""
        exported_pngs = sorted(CHART_DIR.glob("*.png"))
        exported_html = sorted(CHART_DIR.glob("*.html"))

        print(f"PNG charts exported: {len(exported_pngs)}")
        for path in exported_pngs:
            print("-", path.name)

        print(f"\nPlotly HTML files exported: {len(exported_html)}")
        for path in exported_html:
            print("-", path.name)
        """
    ),
]


def main():
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
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
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, NOTEBOOK_PATH)
    print(f"Created {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
