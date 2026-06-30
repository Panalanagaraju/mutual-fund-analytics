from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Rectangle


DB_PATH = ROOT / "bluestock_mf.db"
OUT_DIR = ROOT / "dashboard"
PNG_DIR = OUT_DIR / "page_exports"

BLUE = "#0B5FFF"
NAVY = "#083B78"
CYAN = "#00AEEF"
GREEN = "#17A673"
ORANGE = "#FF9F1C"
RED = "#D64550"
INK = "#172033"
MUTED = "#697386"
GRID = "#DDE5F0"
BG = "#F7FAFF"
CARD = "#FFFFFF"


def read_sql(con: sqlite3.Connection, query: str, params: tuple = ()) -> pd.DataFrame:
    return pd.read_sql_query(query, con, params=params)


def style_axes(ax, title: str = ""):
    ax.set_facecolor(CARD)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(True, axis="y", color=GRID, linewidth=0.8)
    ax.tick_params(colors=MUTED, labelsize=8)
    if title:
        ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color=INK, pad=10)


def add_header(fig, title: str, subtitle: str):
    fig.patch.set_facecolor(BG)
    fig.text(0.055, 0.955, "Bluestock", fontsize=18, fontweight="bold", color=NAVY)
    fig.text(0.055, 0.925, title, fontsize=24, fontweight="bold", color=INK)
    fig.text(0.055, 0.897, subtitle, fontsize=10, color=MUTED)
    fig.patches.append(Circle((0.035, 0.948), 0.014, transform=fig.transFigure, color=BLUE, zorder=10))
    fig.patches.append(Circle((0.044, 0.948), 0.014, transform=fig.transFigure, color=CYAN, zorder=9))


def add_card(fig, x: float, y: float, w: float, h: float, label: str, value: str, color: str):
    fig.patches.append(
        Rectangle((x, y), w, h, transform=fig.transFigure, facecolor=CARD, edgecolor=GRID, linewidth=1)
    )
    fig.patches.append(Rectangle((x, y), 0.006, h, transform=fig.transFigure, facecolor=color, edgecolor=color))
    fig.text(x + 0.018, y + h - 0.035, label.upper(), fontsize=8, color=MUTED, fontweight="bold")
    fig.text(x + 0.018, y + 0.028, value, fontsize=21, color=INK, fontweight="bold")


def create_brand_assets():
    OUT_DIR.mkdir(exist_ok=True)
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    theme = {
        "name": "Bluestock Mutual Fund Theme",
        "dataColors": [BLUE, CYAN, GREEN, ORANGE, RED, NAVY, "#6C63FF", "#7A869A"],
        "background": BG,
        "foreground": INK,
        "tableAccent": BLUE,
        "visualStyles": {
            "*": {
                "*": {
                    "title": [{"fontColor": {"solid": {"color": INK}}, "fontFamily": "Segoe UI"}],
                    "labels": [{"color": {"solid": {"color": MUTED}}, "fontFamily": "Segoe UI"}],
                }
            }
        },
    }
    (OUT_DIR / "bluestock_powerbi_theme.json").write_text(json.dumps(theme, indent=2), encoding="utf-8")

    logo_fig = plt.figure(figsize=(4.2, 1.0), dpi=200)
    logo_fig.patch.set_alpha(0)
    logo_fig.patches.append(Circle((0.12, 0.5), 0.16, transform=logo_fig.transFigure, color=BLUE))
    logo_fig.patches.append(Circle((0.20, 0.5), 0.16, transform=logo_fig.transFigure, color=CYAN))
    logo_fig.text(0.33, 0.42, "Bluestock", fontsize=28, fontweight="bold", color=NAVY)
    logo_fig.savefig(OUT_DIR / "bluestock_logo.png", transparent=True, bbox_inches="tight", pad_inches=0.05)
    plt.close(logo_fig)


def page_1(con: sqlite3.Connection) -> Path:
    aum = read_sql(
        con,
        """
        select date, fund_house, aum_lakh_crore, aum_crore, num_schemes
        from fact_aum
        order by date
        """,
    )
    aum["date"] = pd.to_datetime(aum["date"])
    trend = aum.groupby("date", as_index=False)["aum_lakh_crore"].sum()
    latest = aum[aum["date"] == aum["date"].max()].sort_values("aum_crore", ascending=True)

    fig = plt.figure(figsize=(16, 9), dpi=150)
    add_header(fig, "Industry Overview", "AUM, SIP, folios and scheme landscape from the cleaned model")
    cards = [
        ("Total AUM", "Rs 81L Cr", BLUE),
        ("SIP Inflows", "Rs 31K Cr", CYAN),
        ("Folios", "26.12 Cr", GREEN),
        ("Schemes", "1,908", ORANGE),
    ]
    for i, card in enumerate(cards):
        add_card(fig, 0.055 + i * 0.225, 0.765, 0.195, 0.105, *card)

    gs = fig.add_gridspec(2, 2, left=0.055, right=0.965, bottom=0.075, top=0.71, wspace=0.22, hspace=0.28)
    ax1 = fig.add_subplot(gs[:, 0])
    style_axes(ax1, "Industry AUM Trend, 2022-2025")
    ax1.plot(trend["date"], trend["aum_lakh_crore"], color=BLUE, linewidth=3)
    ax1.fill_between(trend["date"], trend["aum_lakh_crore"], color=BLUE, alpha=0.12)
    ax1.set_ylabel("AUM (lakh crore)", color=MUTED)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    ax2 = fig.add_subplot(gs[:, 1])
    style_axes(ax2, "AUM by AMC")
    bars = ax2.barh(latest["fund_house"], latest["aum_lakh_crore"], color=BLUE, alpha=0.9)
    ax2.set_xlabel("AUM (lakh crore)", color=MUTED)
    ax2.bar_label(bars, fmt="%.1f", padding=4, color=MUTED, fontsize=8)

    path = PNG_DIR / "01_industry_overview.png"
    fig.savefig(path, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return path


def page_2(con: sqlite3.Connection) -> Path:
    perf = read_sql(con, "select * from fact_performance")
    perf["score"] = (
        perf["return_3yr_pct"].rank(pct=True) * 35
        + perf["sharpe_ratio"].rank(pct=True) * 30
        + perf["alpha"].rank(pct=True) * 20
        + (1 - perf["expense_ratio_pct"].rank(pct=True)) * 15
    ).round(1)
    top = perf.sort_values("score", ascending=False).head(10)
    fund_code = int(top.iloc[0]["amfi_code"])
    fund_name = top.iloc[0]["scheme_name"]
    benchmark = read_sql(
        con,
        """
        select n.date, n.nav, b.close_value
        from fact_nav n
        join dim_fund f on f.amfi_code = n.amfi_code
        join fact_benchmark b on date(b.date) = date(n.date) and b.index_name = 'NIFTY50'
        where n.amfi_code = ?
        order by n.date
        """,
        (fund_code,),
    )
    benchmark["date"] = pd.to_datetime(benchmark["date"])
    benchmark["nav_index"] = benchmark["nav"] / benchmark["nav"].iloc[0] * 100
    benchmark["nifty_index"] = benchmark["close_value"] / benchmark["close_value"].iloc[0] * 100

    fig = plt.figure(figsize=(16, 9), dpi=150)
    add_header(fig, "Fund Performance", "Risk-return view, scorecard and NAV comparison with NIFTY 50")
    gs = fig.add_gridspec(2, 2, left=0.055, right=0.965, bottom=0.075, top=0.84, wspace=0.22, hspace=0.34)

    ax1 = fig.add_subplot(gs[0, 0])
    style_axes(ax1, "Return vs Risk")
    sizes = 40 + (perf["aum_crore"] / perf["aum_crore"].max()) * 650
    scatter = ax1.scatter(
        perf["return_3yr_pct"],
        perf["std_dev_ann_pct"],
        s=sizes,
        c=perf["sharpe_ratio"],
        cmap="viridis",
        alpha=0.72,
        edgecolor="white",
        linewidth=0.7,
    )
    ax1.set_xlabel("3Y return (%)", color=MUTED)
    ax1.set_ylabel("StdDev annualized (%)", color=MUTED)
    cbar = fig.colorbar(scatter, ax=ax1, fraction=0.046, pad=0.04)
    cbar.set_label("Sharpe", color=MUTED)

    ax2 = fig.add_subplot(gs[0, 1])
    style_axes(ax2, "NAV vs Benchmark")
    ax2.plot(benchmark["date"], benchmark["nav_index"], label="Top fund NAV", color=BLUE, linewidth=2.4)
    ax2.plot(benchmark["date"], benchmark["nifty_index"], label="NIFTY 50", color=ORANGE, linewidth=2.2)
    ax2.legend(frameon=False, loc="upper left", fontsize=8)
    ax2.set_ylabel("Indexed to 100", color=MUTED)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax2.text(0.01, -0.22, fund_name[:76], transform=ax2.transAxes, color=MUTED, fontsize=8)

    ax3 = fig.add_subplot(gs[1, :])
    ax3.axis("off")
    table_cols = ["scheme_name", "fund_house", "category", "plan", "return_3yr_pct", "std_dev_ann_pct", "aum_crore", "score"]
    table_df = top[table_cols].copy()
    table_df["scheme_name"] = table_df["scheme_name"].str.replace(" - Growth", "", regex=False).str[:34]
    table_df["aum_crore"] = table_df["aum_crore"].map(lambda x: f"{x:,.0f}")
    table_df[["return_3yr_pct", "std_dev_ann_pct", "score"]] = table_df[["return_3yr_pct", "std_dev_ann_pct", "score"]].round(1)
    table = ax3.table(
        cellText=table_df.values,
        colLabels=["Fund", "House", "Category", "Plan", "3Y %", "Risk %", "AUM Cr", "Score"],
        loc="center",
        cellLoc="left",
        colLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.55)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(GRID)
        if row == 0:
            cell.set_facecolor(NAVY)
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor(CARD if row % 2 else "#F1F6FF")
    ax3.set_title("Sortable Fund Scorecard (ranked by composite score)", loc="left", fontsize=13, fontweight="bold", color=INK, pad=12)

    path = PNG_DIR / "02_fund_performance.png"
    fig.savefig(path, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return path


def page_3(con: sqlite3.Connection) -> Path:
    tx = read_sql(con, "select * from fact_transactions")
    tx["transaction_date"] = pd.to_datetime(tx["transaction_date"])
    by_state = tx.groupby("state", as_index=False)["amount_inr"].sum().sort_values("amount_inr", ascending=False).head(12)
    by_type = tx.groupby("transaction_type", as_index=False)["amount_inr"].sum()
    age_sip = tx[tx["transaction_type"].str.lower() == "sip"].groupby("age_group", as_index=False)["amount_inr"].mean()
    month_vol = tx.groupby(pd.Grouper(key="transaction_date", freq="ME")).size().reset_index(name="transactions")

    fig = plt.figure(figsize=(16, 9), dpi=150)
    add_header(fig, "Investor Analytics", "Geography, transaction mix, SIP age profile and monthly activity")
    fig.text(0.72, 0.91, "Slicers: State | Age group | City tier", fontsize=10, color=NAVY, fontweight="bold")
    gs = fig.add_gridspec(2, 2, left=0.055, right=0.965, bottom=0.075, top=0.84, wspace=0.24, hspace=0.34)

    ax1 = fig.add_subplot(gs[0, 0])
    style_axes(ax1, "Transaction Amount by State")
    state_plot = by_state.sort_values("amount_inr")
    ax1.barh(state_plot["state"], state_plot["amount_inr"] / 1e7, color=BLUE)
    ax1.set_xlabel("Amount (Rs crore)", color=MUTED)

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor(CARD)
    ax2.set_title("SIP / Lumpsum / Redemption Split", loc="left", fontsize=13, fontweight="bold", color=INK, pad=10)
    ax2.pie(
        by_type["amount_inr"],
        labels=by_type["transaction_type"],
        colors=[BLUE, CYAN, ORANGE, GREEN][: len(by_type)],
        autopct="%1.1f%%",
        startangle=100,
        wedgeprops={"width": 0.45, "edgecolor": "white"},
        textprops={"fontsize": 8, "color": INK},
    )

    ax3 = fig.add_subplot(gs[1, 0])
    style_axes(ax3, "Age Group vs Avg SIP Amount")
    order = ["18-25", "26-35", "36-45", "46-55", "56+"]
    age_sip["age_group"] = pd.Categorical(age_sip["age_group"], categories=order, ordered=True)
    age_sip = age_sip.sort_values("age_group")
    ax3.bar(age_sip["age_group"].astype(str), age_sip["amount_inr"], color=GREEN)
    ax3.set_ylabel("Avg SIP amount (Rs)", color=MUTED)

    ax4 = fig.add_subplot(gs[1, 1])
    style_axes(ax4, "Monthly Transaction Volume")
    ax4.plot(month_vol["transaction_date"], month_vol["transactions"], color=NAVY, linewidth=2.5)
    ax4.fill_between(month_vol["transaction_date"], month_vol["transactions"], color=CYAN, alpha=0.16)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax4.tick_params(axis="x", rotation=30)

    path = PNG_DIR / "03_investor_analytics.png"
    fig.savefig(path, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return path


def page_4(con: sqlite3.Connection) -> Path:
    sip = read_sql(con, "select * from fact_sip_inflows")
    sip["month_date"] = pd.to_datetime(sip["month"] + "-01")
    nifty = read_sql(con, "select date, close_value from fact_benchmark where index_name = 'NIFTY50'")
    nifty["date"] = pd.to_datetime(nifty["date"])
    nifty_month = (
        nifty.set_index("date")["close_value"]
        .resample("MS")
        .last()
        .reset_index()
    )
    combo = sip.merge(nifty_month, left_on="month_date", right_on="date", how="left")
    cat = read_sql(con, "select * from fact_category_inflows")
    cat["month_date"] = pd.to_datetime(cat["month"] + "-01")
    heat = cat.pivot_table(index="category", columns=cat["month_date"].dt.strftime("%b %Y"), values="net_inflow_crore", aggfunc="sum")
    top5 = cat[cat["month_date"].dt.year == 2025].groupby("category", as_index=False)["net_inflow_crore"].sum().sort_values("net_inflow_crore", ascending=True).tail(5)

    fig = plt.figure(figsize=(16, 9), dpi=150)
    add_header(fig, "SIP & Market Trends", "SIP inflows, market trend, category heatmap and FY25 leaders")
    gs = fig.add_gridspec(2, 2, left=0.055, right=0.965, bottom=0.075, top=0.84, wspace=0.24, hspace=0.34)

    ax1 = fig.add_subplot(gs[0, :])
    style_axes(ax1, "SIP Inflow + NIFTY 50, 2022-2025")
    ax1.bar(combo["month_date"], combo["sip_inflow_crore"], width=22, color=BLUE, alpha=0.75, label="SIP inflow")
    ax1.set_ylabel("SIP inflow (Rs crore)", color=MUTED)
    ax1b = ax1.twinx()
    ax1b.plot(combo["month_date"], combo["close_value"], color=ORANGE, linewidth=2.5, label="NIFTY 50")
    ax1b.set_ylabel("NIFTY 50", color=MUTED)
    ax1b.tick_params(colors=MUTED, labelsize=8)
    for spine in ax1b.spines.values():
        spine.set_visible(False)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor(CARD)
    ax2.set_title("Category Inflow Heatmap", loc="left", fontsize=13, fontweight="bold", color=INK, pad=10)
    im = ax2.imshow(heat.values, aspect="auto", cmap="YlGnBu")
    ax2.set_yticks(range(len(heat.index)))
    ax2.set_yticklabels(heat.index, fontsize=8, color=MUTED)
    step = max(1, len(heat.columns) // 8)
    ax2.set_xticks(range(0, len(heat.columns), step))
    ax2.set_xticklabels(heat.columns[::step], rotation=35, ha="right", fontsize=8, color=MUTED)
    for spine in ax2.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label("Net inflow (Rs crore)", color=MUTED)

    ax3 = fig.add_subplot(gs[1, 1])
    style_axes(ax3, "Top 5 Categories by Net Inflow FY25")
    bars = ax3.barh(top5["category"], top5["net_inflow_crore"], color=[BLUE, CYAN, GREEN, ORANGE, NAVY])
    ax3.set_xlabel("Net inflow (Rs crore)", color=MUTED)
    ax3.bar_label(bars, fmt="%.0f", padding=4, color=MUTED, fontsize=8)

    path = PNG_DIR / "04_sip_market_trends.png"
    fig.savefig(path, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return path


def write_powerbi_notes(con: sqlite3.Connection):
    tables = pd.read_sql_query("select name from sqlite_master where type='table' order by name", con)
    counts = []
    for name in tables["name"]:
        counts.append((name, con.execute(f"select count(*) from {name}").fetchone()[0]))
    relationship_checks = [
        ("fact_nav amfi_code -> dim_fund", "select count(*) from fact_nav n left join dim_fund f on f.amfi_code=n.amfi_code where f.amfi_code is null"),
        ("fact_transactions amfi_code -> dim_fund", "select count(*) from fact_transactions t left join dim_fund f on f.amfi_code=t.amfi_code where f.amfi_code is null"),
        ("fact_performance amfi_code -> dim_fund", "select count(*) from fact_performance p left join dim_fund f on f.amfi_code=p.amfi_code where f.amfi_code is null"),
        ("fact_portfolio amfi_code -> dim_fund", "select count(*) from fact_portfolio p left join dim_fund f on f.amfi_code=p.amfi_code where f.amfi_code is null"),
        ("fact_nav date -> dim_date", "select count(*) from fact_nav n left join dim_date d on d.date=n.date where d.date is null"),
        ("fact_transactions transaction_date -> dim_date", "select count(*) from fact_transactions t left join dim_date d on d.date=t.transaction_date where d.date is null"),
        ("fact_aum date -> dim_date", "select count(*) from fact_aum a left join dim_date d on d.date=a.date where d.date is null"),
        ("fact_benchmark date -> dim_date", "select count(*) from fact_benchmark b left join dim_date d on d.date=b.date where d.date is null"),
    ]
    lines = [
        "# Bluestock Power BI Build Notes",
        "",
        "Power BI Desktop was not available through the local command line, so the native PBIX file must be created in Desktop from this model.",
        "",
        "## Verified SQLite Tables",
        "",
    ]
    for name, count in counts:
        lines.append(f"- `{name}`: {count:,} rows")
    lines += [
        "",
        "## Required Relationships",
        "",
        "- `dim_fund[amfi_code]` 1:* `fact_nav[amfi_code]`",
        "- `dim_fund[amfi_code]` 1:* `fact_transactions[amfi_code]`",
        "- `dim_fund[amfi_code]` 1:* `fact_performance[amfi_code]`",
        "- `dim_fund[amfi_code]` 1:* `fact_portfolio[amfi_code]`",
        "- `dim_date[date]` 1:* `fact_nav[date]`",
        "- `dim_date[date]` 1:* `fact_transactions[transaction_date]`",
        "- `dim_date[date]` 1:* `fact_aum[date]`",
        "- `dim_date[date]` 1:* `fact_benchmark[date]`",
        "",
        "## Relationship Audit",
        "",
    ]
    for label, sql in relationship_checks:
        orphan_count = con.execute(sql).fetchone()[0]
        lines.append(f"- `{label}`: {orphan_count:,} orphan rows")
    lines += [
        "",
        "## Assets",
        "",
        "- Theme: `dashboard/bluestock_powerbi_theme.json`",
        "- Logo: `dashboard/bluestock_logo.png`",
        "- SQLite source: `bluestock_mf.db`",
    ]
    (OUT_DIR / "powerbi_build_notes.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    create_brand_assets()
    with sqlite3.connect(DB_PATH) as con:
        paths = [page_1(con), page_2(con), page_3(con), page_4(con)]
        write_powerbi_notes(con)

    pdf_path = ROOT / "Dashboard.pdf"
    with PdfPages(pdf_path) as pdf:
        for path in paths:
            img = plt.imread(path)
            fig = plt.figure(figsize=(16, 9), dpi=150)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.imshow(img)
            ax.axis("off")
            pdf.savefig(fig, bbox_inches="tight", pad_inches=0)
            plt.close(fig)
    print("Created:")
    print(pdf_path)
    for path in paths:
        print(path)
    print(OUT_DIR / "bluestock_powerbi_theme.json")
    print(OUT_DIR / "bluestock_logo.png")
    print(OUT_DIR / "powerbi_build_notes.md")


if __name__ == "__main__":
    main()
