"""Pull a sample of card trips from BigQuery and run every comparison.

Usage:
    gcloud auth application-default login
    export GOOGLE_CLOUD_PROJECT=your-project-id
    python src/run_analysis.py --year 2022 --sample-rows 200000
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.stats_utils import bonferroni, compare, describe  # noqa: E402


def load_sample(year: int, sample_rows: int):
    from google.cloud import bigquery  # imported here so tests don't need it

    base = (ROOT / "sql" / "02_analysis_table.sql").read_text().format(year=year)
    query = f"SELECT * FROM ({base}) ORDER BY RAND() LIMIT {sample_rows}"
    client = bigquery.Client()
    return client.query(query).to_dataframe()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2022)
    parser.add_argument("--sample-rows", type=int, default=200_000)
    args = parser.parse_args()

    df = load_sample(args.year, args.sample_rows)
    df["tip_pct"] = df["tip_pct"].astype(float) * 100
    print(f"loaded {len(df):,} card trips")
    print("overall:", describe(df["tip_pct"]))

    tests = [
        ("airport vs non-airport", "is_airport"),
        ("weekend vs weekday", "is_weekend"),
        ("night vs day", "is_night"),
    ]
    results = [
        compare(df.loc[df[col], "tip_pct"], df.loc[~df[col], "tip_pct"], label=label)
        for label, col in tests
    ]
    for r in bonferroni(results):
        print(
            f"{r.label:<24} mean {r.mean_a:6.2f}% vs {r.mean_b:6.2f}%  "
            f"diff {r.diff:+.2f} pp (95% CI {r.ci_low:+.2f} to {r.ci_high:+.2f})  "
            f"d={r.cohens_d:+.3f}  p_adj={r.p_adjusted:.2e}"
        )

    print("\nmean tip % by pickup borough:")
    print(df.groupby("pickup_borough")["tip_pct"].agg(["count", "mean", "median"]).round(2))


if __name__ == "__main__":
    main()
