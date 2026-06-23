# live_nav_fetch.py

import requests
import pandas as pd
import os

OUTPUT_FOLDER = "data/raw"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

schemes = {
    "HDFC Top 100 Direct": 125497,
    "SBI Bluechip": 119551,
    "ICICI Bluechip": 120503,
    "Nippon Large Cap": 118632,
    "Axis Bluechip": 119092,
    "Kotak Bluechip": 120841
}

all_nav_data = []

print("=" * 100)
print("LIVE NAV FETCH STARTED")
print("=" * 100)

for fund_name, scheme_code in schemes.items():

    print(f"\nFetching NAV Data -> {fund_name}")

    url = f"https://api.mfapi.in/mf/{scheme_code}"

    try:

        response = requests.get(url, timeout=30)

        if response.status_code == 200:

            json_data = response.json()

            meta = json_data.get("meta", {})
            nav_records = json_data.get("data", [])

            print("Records Found:", len(nav_records))

            for record in nav_records:

                all_nav_data.append({
                    "scheme_code": scheme_code,
                    "fund_name": fund_name,
                    "scheme_name": meta.get("scheme_name"),
                    "fund_house": meta.get("fund_house"),
                    "scheme_type": meta.get("scheme_type"),
                    "scheme_category": meta.get("scheme_category"),
                    "date": record.get("date"),
                    "nav": record.get("nav")
                })

        else:

            print(
                f"Failed: HTTP Status {response.status_code}"
            )

    except Exception as e:

        print(
            f"Error while fetching {fund_name}"
        )

        print(e)

# =====================================================
# SAVE COMBINED NAV FILE
# =====================================================

nav_df = pd.DataFrame(all_nav_data)

combined_file = os.path.join(
    OUTPUT_FOLDER,
    "live_nav_data.csv"
)

nav_df.to_csv(
    combined_file,
    index=False
)

print("\n")
print("=" * 100)
print("COMBINED NAV FILE SAVED")
print("=" * 100)

print("\nLocation:")
print(combined_file)

print("\nShape:")
print(nav_df.shape)

print("\nSample Data:")
print(nav_df.head())

# =====================================================
# SAVE INDIVIDUAL FILES
# =====================================================

for fund_name in nav_df["fund_name"].unique():

    temp_df = nav_df[
        nav_df["fund_name"] == fund_name
    ]

    file_name = (
        fund_name
        .replace(" ", "_")
        .replace("/", "_")
        .lower()
        + ".csv"
    )

    save_path = os.path.join(
        OUTPUT_FOLDER,
        file_name
    )

    temp_df.to_csv(
        save_path,
        index=False
    )

print("\nIndividual fund files saved.")

print("\n")
print("=" * 100)
print("LIVE NAV FETCH COMPLETED")
print("=" * 100)