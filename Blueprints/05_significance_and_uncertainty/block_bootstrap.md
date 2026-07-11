# Block bootstrap (time series)

## What it is

Bootstrap that resamples in blocks of consecutive observations to preserve time order and autocorrelation. Used for time-series metrics.

## When to use it

When data is a time series and you need confidence intervals for a metric (e.g. Sharpe). Standard bootstrap breaks dependence; block bootstrap keeps it.

## How it works

Choose block length. Sample blocks with replacement; concatenate; compute metric; repeat. Report CI. Try several block lengths. Tools: custom or ruptures/block bootstrap libs.

## Inputs

Time series data. Config: block length, number of samples, metric.

## Outputs

CI bounds, bootstrap summary. Location: results/, logs/.

## Related tests

[bootstrap.md](bootstrap.md); [permutation_test.md](permutation_test.md); Sharpe, drawdowns.
