# Random search

## What it is

Samples random parameter combinations from ranges instead of a full grid. Good when the grid is too large to enumerate.

## When to use it

When grid search is too expensive. For wider exploration of the parameter space. Often comparable or better than grid search for the same budget of trials.

## How it works

Define ranges per parameter. For N trials: sample one value per parameter; train/evaluate; store metric. Rank; output best params and list of combos. Tools: sklearn RandomizedSearchCV or custom.

## Inputs

Data; parameter ranges; number of samples; metric. Config: ranges, N, data path.

## Outputs

List of sampled combos and metrics; best params; optionally plots. Location: results/, logs/.

## Related tests

Grid search; Monte Carlo; rolling window backtests; Sharpe, drawdowns.
