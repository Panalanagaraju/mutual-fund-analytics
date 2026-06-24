import pandas as pd
import os

# =============================================================================
# PATHS
# =============================================================================

RAW_PATH = "data/raw"
PROCESSED_PATH = "data/processed"

os.makedirs(PROCESSED_PATH, exist_ok=True)

print("=" * 100)
print("MUTUAL FUND ANALYTICS PLATFORM")
print("DAY 2 - DATA CLEANING")
print("=" * 100)

# =============================================================================
# 1. FUND MASTER
# =============================================================================

print("\nCleaning Fund Master...")

fund_master = pd.read_csv(
    os.path.join(RAW_PATH, "01_fund_master.csv")
)

fund_master = fund_master.drop_duplicates()

fund_master.to_csv(
    os.path.join(PROCESSED_PATH, "cleaned_fund_master.csv"),
    index=False
)

print(f"Rows: {len(fund_master)}")


# =============================================================================
# 2. NAV HISTORY
# =============================================================================

print("\nCleaning NAV History...")

nav_history = pd.read_csv(
    os.path.join(RAW_PATH, "02_nav_history.csv")
)

# Convert date
nav_history["date"] = pd.to_datetime(
    nav_history["date"],
    errors="coerce"
)

# Remove duplicates
nav_history = nav_history.drop_duplicates()

# Sort
nav_history = nav_history.sort_values(
    ["amfi_code", "date"]
)

# Forward fill NAV
nav_history["nav"] = (
    nav_history.groupby("amfi_code")["nav"]
    .ffill()
)

# Remove invalid NAV
nav_history = nav_history[
    nav_history["nav"] > 0
]

nav_history.to_csv(
    os.path.join(PROCESSED_PATH, "cleaned_nav_history.csv"),
    index=False
)

print(f"Rows: {len(nav_history)}")


# =============================================================================
# 3. AUM BY FUND HOUSE
# =============================================================================

print("\nCleaning AUM By Fund House...")

aum = pd.read_csv(
    os.path.join(RAW_PATH, "03_aum_by_fund_house.csv")
)

aum = aum.drop_duplicates()

aum["date"] = pd.to_datetime(
    aum["date"],
    errors="coerce"
)

aum.to_csv(
    os.path.join(PROCESSED_PATH, "cleaned_aum_by_fund_house.csv"),
    index=False
)

print(f"Rows: {len(aum)}")


# =============================================================================
# 4. SIP INFLOWS
# =============================================================================

print("\nCleaning SIP Inflows...")

sip = pd.read_csv(
    os.path.join(RAW_PATH, "04_monthly_sip_inflows.csv")
)

sip = sip.drop_duplicates()

# Fill YoY growth missing values
sip["yoy_growth_pct"] = sip["yoy_growth_pct"].fillna(0)

sip.to_csv(
    os.path.join(PROCESSED_PATH, "cleaned_monthly_sip_inflows.csv"),
    index=False
)

print(f"Rows: {len(sip)}")


# =============================================================================
# 5. CATEGORY INFLOWS
# =============================================================================

print("\nCleaning Category Inflows...")

category = pd.read_csv(
    os.path.join(RAW_PATH, "05_category_inflows.csv")
)

category = category.drop_duplicates()

category.to_csv(
    os.path.join(PROCESSED_PATH, "cleaned_category_inflows.csv"),
    index=False
)

print(f"Rows: {len(category)}")


# =============================================================================
# 6. INDUSTRY FOLIO COUNT
# =============================================================================

print("\nCleaning Industry Folio Count...")

folio = pd.read_csv(
    os.path.join(RAW_PATH, "06_industry_folio_count.csv")
)

folio = folio.drop_duplicates()

folio.to_csv(
    os.path.join(PROCESSED_PATH, "cleaned_industry_folio_count.csv"),
    index=False
)

print(f"Rows: {len(folio)}")


# =============================================================================
# 7. SCHEME PERFORMANCE
# =============================================================================

print("\nCleaning Scheme Performance...")

performance = pd.read_csv(
    os.path.join(RAW_PATH, "07_scheme_performance.csv")
)

performance = performance.drop_duplicates()

return_cols = [
    "return_1yr_pct",
    "return_3yr_pct",
    "return_5yr_pct",
]

for col in return_cols:
    performance[col] = pd.to_numeric(
        performance[col],
        errors="coerce"
    )

# Flag abnormal returns
anomalies = performance[
    (performance["return_1yr_pct"] > 100)
    |
    (performance["return_1yr_pct"] < -100)
]

print(f"Return Anomalies Found: {len(anomalies)}")

# Validate expense ratio
expense_issues = performance[
    (performance["expense_ratio_pct"] < 0.1)
    |
    (performance["expense_ratio_pct"] > 2.5)
]

print(f"Expense Ratio Issues: {len(expense_issues)}")

performance.to_csv(
    os.path.join(PROCESSED_PATH, "cleaned_scheme_performance.csv"),
    index=False
)

print(f"Rows: {len(performance)}")


# =============================================================================
# 8. INVESTOR TRANSACTIONS
# =============================================================================

print("\nCleaning Investor Transactions...")

transactions = pd.read_csv(
    os.path.join(RAW_PATH, "08_investor_transactions.csv")
)

transactions = transactions.drop_duplicates()

# Standardize transaction type
transactions["transaction_type"] = (
    transactions["transaction_type"]
    .astype(str)
    .str.strip()
    .str.title()
)

# Validate amount
transactions = transactions[
    transactions["amount_inr"] > 0
]

# Convert date
transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"],
    errors="coerce"
)

# Validate KYC status
valid_kyc = ["Verified", "Pending"]

invalid_kyc = transactions[
    ~transactions["kyc_status"].isin(valid_kyc)
]

print(f"Invalid KYC Records: {len(invalid_kyc)}")

transactions.to_csv(
    os.path.join(PROCESSED_PATH, "cleaned_investor_transactions.csv"),
    index=False
)

print(f"Rows: {len(transactions)}")


# =============================================================================
# 9. PORTFOLIO HOLDINGS
# =============================================================================

print("\nCleaning Portfolio Holdings...")

portfolio = pd.read_csv(
    os.path.join(RAW_PATH, "09_portfolio_holdings.csv")
)

portfolio = portfolio.drop_duplicates()

portfolio.to_csv(
    os.path.join(PROCESSED_PATH, "cleaned_portfolio_holdings.csv"),
    index=False
)

print(f"Rows: {len(portfolio)}")


# =============================================================================
# 10. BENCHMARK INDICES
# =============================================================================

print("\nCleaning Benchmark Indices...")

benchmark = pd.read_csv(
    os.path.join(RAW_PATH, "10_benchmark_indices.csv")
)

benchmark = benchmark.drop_duplicates()

benchmark["date"] = pd.to_datetime(
    benchmark["date"],
    errors="coerce"
)

benchmark.to_csv(
    os.path.join(PROCESSED_PATH, "cleaned_benchmark_indices.csv"),
    index=False
)

print(f"Rows: {len(benchmark)}")


# =============================================================================
# DATA QUALITY SUMMARY
# =============================================================================

print("\n" + "=" * 100)
print("DATA CLEANING SUMMARY")
print("=" * 100)

processed_files = os.listdir(PROCESSED_PATH)

for file in processed_files:

    file_path = os.path.join(
        PROCESSED_PATH,
        file
    )

    df = pd.read_csv(file_path)

    print("\n" + "-" * 60)
    print(file)
    print("-" * 60)

    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])
    print("Missing Values:", df.isnull().sum().sum())
    print("Duplicates:", df.duplicated().sum())

print("\n" + "=" * 100)
print("DAY 2 DATA CLEANING COMPLETED SUCCESSFULLY")
print("=" * 100)