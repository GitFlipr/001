# Grid search

## What it is

Exhaustive search over a predefined set of parameter combinations (e.g. window size, threshold). Finds which combination gives the best metric on the data.

## When to use it

When the search space is small enough to enumerate. To establish a baseline of achievable performance before random search or Bayesian methods. For clear ranking of parameter combos for reporting.

## How it works

Define a grid (list of values per parameter). For each combination, train/evaluate and compute metric (e.g. Sharpe, hit rate). Rank; output best params and full table. Tools: sklearn GridSearchCV or custom loop.

## Inputs

Data; parameter grid; metric. Config: grid definition, data path.

## Outputs

Table or JSON of each combo and metric; best params; optionally plots. Location: results/, logs/.

## Related tests

Random search; Monte Carlo; rolling window backtests (use best params); Sharpe, drawdowns.
