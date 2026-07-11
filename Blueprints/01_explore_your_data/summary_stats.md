# Summary statistics (OHLCV)

## What it is

Summary statistics are numeric descriptors of each series in your dataset: count, mean, standard deviation, min, max, percentiles (e.g. 5%, 25%, 50%, 75%, 95%), skewness, and kurtosis. For OHLCV (open, high, low, close, volume) this gives a quick numeric overview of price and volume behaviour.

## When to use it

- **Before any modeling:** To see scale, spread, and obvious data issues (zeros, extreme spikes, wrong units).
- **To choose transformations:** Skew and kurtosis guide whether to use log returns, winsorization, or robust methods later.
- **To compare assets or periods:** Compare mean, std, and percentiles across symbols or windows.
- **As a baseline reference:** When you later run histograms, joint plots, or distribution fitting, you can refer back to these numbers.

## How it works

For each column (e.g. close, returns, volume): **Count**, **Mean**, **Std**, **Min/Max**, **Percentiles**, **Skewness**, **Kurtosis**. Optional: counts of missing values, zeros, or outliers.

## Inputs

Data: OHLCV (or returns, volume) in tabular form. Config: which series to summarize, how many files/symbols.

## Outputs

Tables or JSON: per-asset, per-series stats. Location: typically results/ and logs/.

## How to run / implement

Run the module that implements summary stats (e.g. summary_stats), with config pointing to your data path and output path. Implement with pandas (e.g. describe(), scipy.stats.skew, scipy.stats.kurtosis), then write JSON or tables.

## Interpretation

Similar mean/std across symbols suggests comparable scale. High skew or kurtosis in returns suggests robust methods or tail-aware risk metrics. Zeros or impossible values need fixing before downstream tests.

## Related tests

Histograms and KDE (visualize same series); joint plots (relationships between two series); distribution fitting (use summary stats to choose candidate distributions).
