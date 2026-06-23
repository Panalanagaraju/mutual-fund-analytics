# data_ingestion.py

import pandas as pd
import os

RAW_DATA_PATH = "data/raw"

print("=" * 100)
print("MUTUAL FUND ANALYTICS PLATFORM")
print("DAY 1 - DATA INGESTION & VALIDATION")
print("=" * 100)

# =====================================================
# LOAD ALL CSV FILES
# =====================================================

csv_files = sorted(
    [file for file in os.listdir(RAW_DATA_PATH) if file.endswith(".csv")]
)

datasets = {}

print("\nTOTAL CSV FILES FOUND:", len(csv_files))

for file in csv_files:

    print("\n" + "=" * 100)
    print(f"DATASET : {file}")
    print("=" * 100)

    file_path = os.path.join(RAW_DATA_PATH, file)

    try:
        df = pd.read_csv(file_path)

        datasets[file] = df

        print("\nShape:")
        print(df.shape)

        print("\nColumns:")
        print(df.columns.tolist())

        print("\nData Types:")
        print(df.dtypes)

        print("\nMissing Values:")
        print(df.isnull().sum())

        print("\nFirst 5 Rows:")
        print(df.head())

    except Exception as e:
        print(f"\nERROR LOADING {file}")
        print(e)

# =====================================================
# FUND MASTER EXPLORATION
# =====================================================

print("\n")
print("=" * 100)
print("FUND MASTER EXPLORATION")
print("=" * 100)

fund_master_file = None

for file in csv_files:
    if "fund" in file.lower() and "master" in file.lower():
        fund_master_file = file
        break

if fund_master_file:

    fund_master = datasets[fund_master_file]

    print("\nFund Master File:")
    print(fund_master_file)

    print("\nRows:", fund_master.shape[0])
    print("Columns:", fund_master.shape[1])

    columns = [col.lower() for col in fund_master.columns]

    # Fund Houses
    possible_cols = [
        "fund_house",
        "amc_name",
        "asset_management_company"
    ]

    for col in possible_cols:
        if col in columns:
            actual_col = fund_master.columns[columns.index(col)]

            print("\nUnique Fund Houses:")
            print(
                fund_master[actual_col]
                .dropna()
                .unique()
            )

            print(
                "\nTotal Fund Houses:",
                fund_master[actual_col].nunique()
            )
            break

    # Category
    possible_cols = [
        "category",
        "scheme_category"
    ]

    for col in possible_cols:
        if col in columns:
            actual_col = fund_master.columns[columns.index(col)]

            print("\nCategories:")
            print(
                fund_master[actual_col]
                .dropna()
                .unique()
            )
            break

    # Sub Category
    possible_cols = [
        "subcategory",
        "sub_category",
        "scheme_sub_category"
    ]

    for col in possible_cols:
        if col in columns:
            actual_col = fund_master.columns[columns.index(col)]

            print("\nSub Categories:")
            print(
                fund_master[actual_col]
                .dropna()
                .unique()
            )
            break

    # Risk Grade
    possible_cols = [
        "risk_grade",
        "risk",
        "risk_level"
    ]

    for col in possible_cols:
        if col in columns:
            actual_col = fund_master.columns[columns.index(col)]

            print("\nRisk Grades:")
            print(
                fund_master[actual_col]
                .dropna()
                .unique()
            )
            break

else:
    print("\nFund Master file not found.")

# =====================================================
# AMFI CODE VALIDATION
# =====================================================

print("\n")
print("=" * 100)
print("AMFI CODE VALIDATION")
print("=" * 100)

fund_master_file = None
nav_history_file = None

for file in csv_files:

    lower_file = file.lower()

    if "fund" in lower_file and "master" in lower_file:
        fund_master_file = file

    if "nav" in lower_file and "history" in lower_file:
        nav_history_file = file

if fund_master_file and nav_history_file:

    fund_master = datasets[fund_master_file]
    nav_history = datasets[nav_history_file]

    fund_code_col = None
    nav_code_col = None

    for col in fund_master.columns:
        if "scheme" in col.lower() and "code" in col.lower():
            fund_code_col = col
            break

    for col in nav_history.columns:
        if "scheme" in col.lower() and "code" in col.lower():
            nav_code_col = col
            break

    if fund_code_col and nav_code_col:

        master_codes = set(
            fund_master[fund_code_col]
            .dropna()
            .astype(str)
        )

        nav_codes = set(
            nav_history[nav_code_col]
            .dropna()
            .astype(str)
        )

        missing_codes = master_codes - nav_codes

        print("\nFund Master Codes :", len(master_codes))
        print("NAV History Codes :", len(nav_codes))
        print("Missing Codes :", len(missing_codes))

        if len(missing_codes) == 0:
            print("\nPASS : All AMFI Codes Exist")
        else:
            print("\nFAIL : Missing AMFI Codes Found")

            print("\nSample Missing Codes:")

            for code in list(missing_codes)[:20]:
                print(code)

    else:
        print("\nScheme Code columns not found.")

else:
    print("\nFund Master or NAV History file missing.")

# =====================================================
# DATA QUALITY SUMMARY
# =====================================================

print("\n")
print("=" * 100)
print("DATA QUALITY SUMMARY")
print("=" * 100)

for file, df in datasets.items():

    total_rows = df.shape[0]
    total_columns = df.shape[1]

    missing_values = df.isnull().sum().sum()

    duplicate_rows = df.duplicated().sum()

    print("\n" + "-" * 60)
    print(file)
    print("-" * 60)

    print("Rows:", total_rows)
    print("Columns:", total_columns)
    print("Missing Values:", missing_values)
    print("Duplicate Rows:", duplicate_rows)

print("\n")
print("=" * 100)
print("DAY 1 DATA INGESTION COMPLETED SUCCESSFULLY")
print("=" * 100)