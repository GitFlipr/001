# Data quality checks (OHLCV)

## What it is

Automated checks for common data issues before any analysis: missing values, duplicates, impossible OHLC relationships, outliers, and basic sanity checks. Ensures data is ready for downstream tests.

## When to use it

- **First step before any modeling or backtesting:** Catch bad data early so summary stats and plots reflect reality.
- **After loading new data sources:** Validate schema, completeness, and physical constraints.
- **As part of a pipeline:** Run before summary_stats and histograms; fail fast if checks fail.
- **When debugging strange results:** Quick audit to rule out data issues.

## How it works

1. **Missing values:** Count and percentage of NaN/null per column; flag columns above a threshold.
2. **Duplicates:** Detect duplicate timestamps or full-row duplicates; report count and examples.
3. **OHLC sanity:** For each row, check High ≥ Low, High ≥ Open, High ≥ Close, Low ≤ Open, Low ≤ Close; flag violations.
4. **Volume:** Non-negative; flag zeros or negative values.
5. **Outlier detection (optional):** Simple z-score or IQR-based flags for extreme values; report count.
6. **Timestamp order:** Check that index/date is monotonically increasing (no gaps or reversals unless expected).

Output: pass/fail per check; list of failures; optional summary JSON.

## Inputs

Data: OHLCV (or returns, volume) in tabular form. Config: thresholds (e.g. max % missing), which checks to run, output path.

## Outputs

Pass/fail summary per check; list of violated rows or timestamps; optional JSON report. Location: results/, logs/.

## How to run / implement

Run the data_quality module with config pointing to data path and checklist. Implement with pandas (isna, duplicated, boolean masks for OHLC), then write report.

## Interpretation

Any failing check should be investigated before proceeding. OHLC violations suggest bad feed or parsing. High missingness may require forward-fill, drop, or different data source. Duplicates need deduplication logic.

## Related tests

Summary stats (next step after clean data); histograms/KDE (visualize distributions); distribution fitting (use clean series).