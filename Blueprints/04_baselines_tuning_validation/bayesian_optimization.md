# Bayesian optimization (hyperparameter tuning)

## What it is

A **sample-efficient** method for tuning hyperparameters: instead of random or grid search, it builds a **surrogate model** (e.g. Gaussian process) of the metric as a function of parameters, then uses an **acquisition function** (e.g. expected improvement) to choose the next point to evaluate. Typically finds good params in many fewer trials than grid or random search.

## When to use it

When each evaluation is **expensive** (e.g. full rolling backtest, long training). When you have continuous or large discrete parameter spaces. When you want to minimize the number of backtests or training runs. Complements grid search (small grids) and random search (cheap evaluations).

## How it works

1. Evaluate a few initial points (random or Latin hypercube).
2. Fit a surrogate (e.g. GP) to (params, metric).
3. Maximize acquisition function (EI, UCB) to pick next params.
4. Evaluate; add to data; repeat until budget.
5. Return best params seen. Tools: `optuna`, `scikit-optimize`, `BayesianOptimization` (GPyOpt).

## Inputs

Data; parameter bounds (continuous or discrete); metric; evaluation budget (N trials). Config: bounds, N, acquisition, surrogate type.

## Outputs

Best params; history of trials (params, metric); optional convergence plot. Location: results/, logs/.

## Interpretation

Fewer trials to reach good params than grid/random. Best when evaluations are costly. For backtesting: each trial = one backtest; Bayesian optimization reduces trials needed.

## Related tests

Grid search; random search; rolling window backtests (use tuned params); time_series_cv (evaluation scheme); Lasso/Ridge (tune alpha with Bayesian opt).