import pandas as pd
import os
import sqlite3

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

DB_NAME = "bluestock_mf.db"
PROCESSED_PATH = "data/processed"

conn = sqlite3.connect(DB_NAME)

print("=" * 100)
print("LOADING CLEANED DATA INTO SQLITE")
print("=" * 100)

# =============================================================================
# LOAD CLEANED CSV FILES
# =============================================================================

fund_master = pd.read_csv(
    os.path.join(PROCESSED_PATH, "cleaned_fund_master.csv")
)

nav_history = pd.read_csv(
    os.path.join(PROCESSED_PATH, "cleaned_nav_history.csv")
)

aum = pd.read_csv(
    os.path.join(PROCESSED_PATH, "cleaned_aum_by_fund_house.csv")
)

sip = pd.read_csv(
    os.path.join(PROCESSED_PATH, "cleaned_monthly_sip_inflows.csv")
)

category = pd.read_csv(
    os.path.join(PROCESSED_PATH, "cleaned_category_inflows.csv")
)

folio = pd.read_csv(
    os.path.join(PROCESSED_PATH, "cleaned_industry_folio_count.csv")
)

performance = pd.read_csv(
    os.path.join(PROCESSED_PATH, "cleaned_scheme_performance.csv")
)

transactions = pd.read_csv(
    os.path.join(PROCESSED_PATH, "cleaned_investor_transactions.csv")
)

portfolio = pd.read_csv(
    os.path.join(PROCESSED_PATH, "cleaned_portfolio_holdings.csv")
)

benchmark = pd.read_csv(
    os.path.join(PROCESSED_PATH, "cleaned_benchmark_indices.csv")
)

# =============================================================================
# DIMENSION TABLES
# =============================================================================

print("\nLoading Dimension Tables...")

dim_fund = fund_master.copy()

dim_fund.to_sql(
    "dim_fund",
    conn,
    if_exists="replace",
    index=False
)

print("OK dim_fund loaded")

# =============================================================================
# DATE DIMENSION
# =============================================================================

date_frames = []

date_sources = [
    (nav_history, "date"),
    (transactions, "transaction_date"),
    (aum, "date"),
    (benchmark, "date"),
    (portfolio, "portfolio_date"),
]

month_sources = [
    (sip, "month"),
    (category, "month"),
    (folio, "month"),
]

for frame, column in date_sources:
    if column in frame.columns:
        date_frames.append(
            pd.to_datetime(frame[column], errors="coerce")
        )

for frame, column in month_sources:
    if column in frame.columns:
        date_frames.append(
            pd.to_datetime(frame[column].astype(str) + "-01", errors="coerce")
        )

all_dates = pd.concat(
    [pd.Series(d) for d in date_frames],
    ignore_index=True
)

dim_date = pd.DataFrame({
    "date": all_dates.dropna().drop_duplicates().sort_values()
})

dim_date["date"] = pd.to_datetime(
    dim_date["date"]
).dt.strftime("%Y-%m-%d")

dim_date["year"] = pd.to_datetime(
    dim_date["date"]
).dt.year

dim_date["month"] = pd.to_datetime(
    dim_date["date"]
).dt.month

dim_date["day"] = pd.to_datetime(
    dim_date["date"]
).dt.day

dim_date["quarter"] = pd.to_datetime(
    dim_date["date"]
).dt.quarter

dim_date.to_sql(
    "dim_date",
    conn,
    if_exists="replace",
    index=False
)

print("OK dim_date loaded")

# =============================================================================
# FACT TABLES
# =============================================================================

print("\nLoading Fact Tables...")

nav_history.to_sql(
    "fact_nav",
    conn,
    if_exists="replace",
    index=False
)

print("OK fact_nav loaded")

transactions.to_sql(
    "fact_transactions",
    conn,
    if_exists="replace",
    index=False
)

print("OK fact_transactions loaded")

performance.to_sql(
    "fact_performance",
    conn,
    if_exists="replace",
    index=False
)

print("OK fact_performance loaded")

aum.to_sql(
    "fact_aum",
    conn,
    if_exists="replace",
    index=False
)

print("OK fact_aum loaded")

portfolio.to_sql(
    "fact_portfolio",
    conn,
    if_exists="replace",
    index=False
)

print("OK fact_portfolio loaded")

sip.to_sql(
    "fact_sip_inflows",
    conn,
    if_exists="replace",
    index=False
)

print("OK fact_sip_inflows loaded")

category.to_sql(
    "fact_category_inflows",
    conn,
    if_exists="replace",
    index=False
)

print("OK fact_category_inflows loaded")

folio.to_sql(
    "fact_folio_count",
    conn,
    if_exists="replace",
    index=False
)

print("OK fact_folio_count loaded")

benchmark.to_sql(
    "fact_benchmark",
    conn,
    if_exists="replace",
    index=False
)

print("OK fact_benchmark loaded")

# =============================================================================
# VERIFY ROW COUNTS
# =============================================================================

print("\n" + "=" * 100)
print("ROW COUNT VERIFICATION")
print("=" * 100)

tables = [
    "dim_fund",
    "dim_date",
    "fact_nav",
    "fact_transactions",
    "fact_performance",
    "fact_aum",
    "fact_portfolio",
    "fact_sip_inflows",
    "fact_category_inflows",
    "fact_folio_count",
    "fact_benchmark"
]

for table in tables:
    count = conn.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table:<25} {count}")

# =============================================================================
# SUCCESS MESSAGE
# =============================================================================

print("\n" + "=" * 100)
print("SQLITE DATABASE CREATED SUCCESSFULLY")
print(f"Database File: {DB_NAME}")
print("=" * 100)

conn.close()
