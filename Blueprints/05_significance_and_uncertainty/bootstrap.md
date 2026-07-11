# Bootstrap resampling

## What it is

Resample data **with replacement** many times; compute your metric (e.g. Sharpe, accuracy, mean) on each sample. Get a distribution of the metric and confidence intervals (e.g. 5% and 95% bounds) without assuming a distribution.

## When to use it

To quantify uncertainty in any metric. To compare strategies: overlapping CIs mean the difference may not be significant. When you don't want to assume normality.

## How it works

For b in 1..B: draw n rows with replacement; compute metric; store. Report mean, std, and percentiles (e.g. 5%, 95%) of the bootstrap distribution. Tools: custom loop or sklearn resample.

## Inputs

Data: series or table. Config: number of samples, metric(s).

## Outputs

CI bounds (e.g. 5% and 95%), mean, std of bootstrap distribution. Location: results/, logs/.

## Interpretation

Narrow CI: result is stable. Wide CI or CI includes zero: be cautious; try block bootstrap for time series. Overlapping CIs across strategies: prefer simpler strategy.

## Related tests

[block_bootstrap.md](block_bootstrap.md) (time-series); [permutation_test.md](permutation_test.md); bias_variance; Sharpe, drawdowns (metrics to bootstrap).
