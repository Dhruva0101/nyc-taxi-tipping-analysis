# What drives NYC taxi tipping? A statistical analysis on BigQuery

[![CI](https://github.com/Dhruva0101/nyc-taxi-tipping-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/Dhruva0101/nyc-taxi-tipping-analysis/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Tech:** Python · Google BigQuery (SQL) · pandas · SciPy · pytest · GitHub Actions

> **Status: in progress.** Step 0 is done: the BigQuery SQL, a tested statistics module (Welch's t-test, effect size, confidence intervals, multiple-comparison correction), and the analysis script. Results go in the table below once the analysis runs.

## Questions

1. Do tip rates differ by **payment type**, **airport vs non-airport**, **weekday vs weekend**, and **day vs night**? Are the differences statistically significant, and how big are they?
2. When the average tip rate moves month over month, **what caused it**: a real change in tipping behavior, or a change in the mix of trips (more airport or cash trips)?

## Data

Google's public dataset `bigquery-public-data.new_york_taxi_trips` (NYC TLC yellow taxi trips). The free BigQuery sandbox is enough. No credit card needed.

**Known limitation:** card tips are recorded automatically, but **cash tips are usually not recorded**. Cash trips therefore look like they tip ~0%. The analysis restricts tip comparisons to card payments and calls this out.

## Repo layout

| Path | What it is |
|---|---|
| `sql/01_tips_by_payment_type.sql` | First look: trips and average tip % by payment type. |
| `sql/02_analysis_table.sql` | Cleaned, analysis-ready table with derived features. |
| `src/stats_utils.py` | Descriptive stats, Welch's t-test, Cohen's d, 95% CI, Bonferroni. Unit-tested. |
| `src/run_analysis.py` | Pulls a sample from BigQuery and runs every comparison. |
| `tests/` | pytest tests for the statistics module. |

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q                                   # stats module tests

# BigQuery (one-time): create a Google Cloud project, then
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project-id
python src/run_analysis.py --year 2022 --sample-rows 200000
```

You can also paste the files in `sql/` straight into the BigQuery console.

> The SQL was written against the documented schema of the public `tlc_yellow_trips_<year>` and `taxi_zone_geom` tables but has not been run yet. If a column name errors, open the table's **Schema** tab in the BigQuery console and adjust the query; that's part of Step 1.

## Results

| Comparison (card trips) | Mean tip % A | Mean tip % B | Difference (95% CI) | Cohen's d | p (Bonferroni) |
|---|---|---|---|---|---|
| Airport vs non-airport | _tbd_ | _tbd_ | _tbd_ | _tbd_ | _tbd_ |
| Weekend vs weekday | _tbd_ | _tbd_ | _tbd_ | _tbd_ | _tbd_ |
| Night vs day | _tbd_ | _tbd_ | _tbd_ | _tbd_ | _tbd_ |

## Roadmap

- [x] **Step 0:** SQL, statistics module + tests, analysis script, CI
- [ ] **Step 1:** run `02_analysis_table.sql`, descriptive stats per segment, fill in data-quality notes
- [ ] **Step 2:** run the t-tests on real data; fill in the results table; add a chi-square test (tipped vs not, by borough)
- [ ] **Step 3:** root-cause a real month-over-month change in tip %: mix effect vs rate effect
- [ ] **Step 4:** Looker Studio dashboard (tip %, volume, segment breakdowns), link it here

## Method notes / interview prep

- **Why Welch's t-test?** It does not assume the two groups have equal variance, which is rarely true for real segments.
- **Tip % is skewed** (lots of exactly 0%, 20%, 25%, 30%). With huge samples the t-test is still valid on means (central limit theorem), but report a Mann-Whitney U test as a robustness check.
- **Significance vs importance:** with 100k+ rows almost everything is "significant". Report **effect size** (Cohen's d) and the **confidence interval** of the difference, not just p-values.
- **Multiple comparisons:** several tests at once inflate false positives, so p-values are Bonferroni-adjusted.
- **Mix vs rate (Simpson's paradox):** an overall average can drop even if every segment's rate is flat, purely because the mix of trips shifted. Step 3 decomposes the change into both effects.

## License

[MIT](LICENSE)
