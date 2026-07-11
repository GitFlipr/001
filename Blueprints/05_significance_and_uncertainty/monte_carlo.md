# Monte Carlo simulation

## What it is

Simulates many random paths (e.g. returns, equity curves) from a model or resampled data. Answers: how much variance and tail risk do we get under this strategy or distribution?

## When to use it

To see the distribution of outcomes (e.g. final PnL, max drawdown, Sharpe) across many paths. For risk and capital sizing. When you have a model or resampling scheme.

## How it works

Define model or resampling (e.g. from fitted distribution or block bootstrap). For each path: simulate forward; compute metric. Report distribution (mean, std, percentiles) of metrics. Tools: custom loop, numpy/scipy for random.

## Inputs

Data or fitted model; number of paths; seed. Config: paths, seed, model.

## Outputs

Distribution of key metrics across paths; percentiles; optionally plots. Location: results/, logs/.

## Related tests

Bootstrap, block bootstrap; grid search (params to simulate); Sharpe, drawdowns, VaR/CVaR (metrics).
