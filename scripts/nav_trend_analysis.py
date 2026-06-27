import pandas as pd
import plotly.express as px
import glob
import os

# Folder containing NAV CSV files
folder = "data/raw"

# Read all CSV files
files = glob.glob(os.path.join(folder, "*.csv"))

all_data = []

for file in files:

    df = pd.read_csv(file)

    if {'date','nav','scheme_name'}.issubset(df.columns):

        df['date'] = pd.to_datetime(df['date'], dayfirst=True)

        all_data.append(df)

# Merge all datasets
nav_df = pd.concat(all_data)

print(nav_df.head())

fig = px.line(
    nav_df,
    x='date',
    y='nav',
    color='scheme_name',
    title="Daily NAV Trend (2022-2026)"
)

fig.add_vrect(
    x0="2023-01-01",
    x1="2023-12-31",
    fillcolor="green",
    opacity=0.15,
    annotation_text="2023 Bull Run"
)

fig.add_vrect(
    x0="2024-01-01",
    x1="2024-12-31",
    fillcolor="red",
    opacity=0.15,
    annotation_text="2024 Correction"
)

fig.show()

fig.write_html("charts/nav_trend.html")