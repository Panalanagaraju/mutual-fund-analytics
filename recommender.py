import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "processed"

RISK_MAP = {
    "Low": ["Low", "Low to Moderate", "Moderately Low"],
    "Moderate": ["Moderate", "Moderately High"],
    "High": ["High", "Very High"],
}


def recommend(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    appetite = risk_appetite.strip().title()
    if appetite not in RISK_MAP:
        valid = ", ".join(RISK_MAP)
        raise ValueError(f"Unknown risk appetite '{risk_appetite}'. Choose one of: {valid}.")

    scorecard = pd.read_csv(DATA_DIR / "fund_scorecard.csv")
    funds = pd.read_csv(DATA_DIR / "cleaned_fund_master.csv")
    scorecard["amfi_code"] = scorecard["amfi_code"].astype(int)
    funds["amfi_code"] = funds["amfi_code"].astype(int)

    table = scorecard.merge(
        funds[["amfi_code", "risk_category", "sub_category"]],
        on="amfi_code",
        how="left",
    )
    recommendations = (
        table[table["risk_category"].isin(RISK_MAP[appetite])]
        .sort_values("sharpe_ratio", ascending=False)
        .head(top_n)
        .loc[:, ["scheme_name", "fund_house", "sub_category", "risk_category", "sharpe_ratio", "fund_score"]]
        .reset_index(drop=True)
    )
    return recommendations


def main():
    parser = argparse.ArgumentParser(description="Recommend top mutual funds by Sharpe ratio for a risk appetite.")
    parser.add_argument(
        "risk_appetite",
        nargs="?",
        default="Moderate",
        choices=RISK_MAP.keys(),
        help="Investor risk appetite: Low, Moderate, or High.",
    )
    args = parser.parse_args()

    recommendations = recommend(args.risk_appetite)
    print(f"\nTop 3 {args.risk_appetite} Risk Fund Recommendations by Sharpe Ratio\n")
    print(
        recommendations.to_string(
            index=False,
            formatters={
                "sharpe_ratio": "{:.3f}".format,
                "fund_score": "{:.2f}".format,
            },
        )
    )


if __name__ == "__main__":
    main()
