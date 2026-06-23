import pandas as pd

print("=" * 100)
print("AMFI CODE VALIDATION")
print("=" * 100)

try:
    # Load datasets
    fund_master = pd.read_csv("data/raw/01_fund_master.csv")
    nav_history = pd.read_csv("data/raw/02_nav_history.csv")

    # Basic info
    print("\nFund Master Shape :", fund_master.shape)
    print("NAV History Shape :", nav_history.shape)

    # Check required columns
    if "amfi_code" not in fund_master.columns:
        print("\nERROR: 'amfi_code' column not found in 01_fund_master.csv")
        exit()

    if "amfi_code" not in nav_history.columns:
        print("\nERROR: 'amfi_code' column not found in 02_nav_history.csv")
        exit()

    # Extract unique AMFI codes
    fund_codes = set(fund_master["amfi_code"].dropna().unique())
    nav_codes = set(nav_history["amfi_code"].dropna().unique())

    print(f"\nUnique AMFI Codes in Fund Master : {len(fund_codes)}")
    print(f"Unique AMFI Codes in NAV History : {len(nav_codes)}")

    # Missing in NAV History
    missing_in_nav = fund_codes - nav_codes

    # Extra in NAV History
    extra_in_nav = nav_codes - fund_codes

    print("\n" + "-" * 60)

    if len(missing_in_nav) == 0:
        print("✅ All Fund Master AMFI codes exist in NAV History")
    else:
        print(f"❌ Missing Codes in NAV History: {len(missing_in_nav)}")
        print(sorted(missing_in_nav))

    print("\n" + "-" * 60)

    if len(extra_in_nav) == 0:
        print("✅ No extra AMFI codes found in NAV History")
    else:
        print(f"ℹ Extra Codes in NAV History: {len(extra_in_nav)}")
        print(sorted(extra_in_nav))

    print("\n" + "-" * 60)

    # Validation Summary
    total_fund_codes = len(fund_codes)
    matched_codes = len(fund_codes.intersection(nav_codes))

    print("VALIDATION SUMMARY")
    print(f"Total Fund Master Codes : {total_fund_codes}")
    print(f"Matched Codes           : {matched_codes}")
    print(f"Missing Codes           : {len(missing_in_nav)}")
    print(f"Extra Codes             : {len(extra_in_nav)}")

    if len(missing_in_nav) == 0:
        print("\n🎉 DATA QUALITY CHECK PASSED")
        print("All AMFI codes are properly mapped between Fund Master and NAV History.")
    else:
        print("\n⚠ DATA QUALITY ISSUE DETECTED")
        print("Some AMFI codes are missing from NAV History.")

except FileNotFoundError as e:
    print(f"\nFile Not Found Error: {e}")

except Exception as e:
    print(f"\nUnexpected Error: {e}")

print("\n" + "=" * 100)
print("AMFI VALIDATION COMPLETED")
print("=" * 100)