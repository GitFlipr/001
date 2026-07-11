# Basic metrics (accuracy, MAE, RMSE)

## What it is

A single place to report **accuracy** (classification), **MAE** (mean absolute error), **RMSE** (regression), and optionally precision, recall, hit rate, per-symbol or per-model. Used to compare and rank baseline models and to set a benchmark for ML.

## When to use it

After running linear regression, logistic regression, Markov, or other baseline models. To document baselines for reports and for robustness tests (e.g. permutation: is improvement over this baseline significant?). To set a bar for ML models to beat.

## How it works

Aggregate metrics from individual model runs: accuracy (for classification), MAE, RMSE (for regression), optionally precision/recall, hit rate. Tabulate per model and optionally per symbol. Tools: sklearn metrics, pandas.

## Inputs

Data: predictions and actuals from one or more models. Config: which models, which metrics.

## Outputs

Tables or JSON: accuracy, MAE, RMSE (and optionally more) per model/symbol. Location: results/, logs/.

## Interpretation

Pick the best baseline; use its setup as default for ML. Document metrics for permutation and bootstrap. If baselines are weak, improve data or features before heavy ML/DL.

## Related tests

Linear_model, logistic_regression, markov_chains (sources of predictions); mean_squared_error, r_squared; permutation, bootstrap (validate that gains over baseline are significant).
