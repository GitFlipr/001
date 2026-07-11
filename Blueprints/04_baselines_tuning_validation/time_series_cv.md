# Time-series cross-validation

## What it is

Cross-validation that respects time order: train on past, validate on future. Uses purge and optionally embargo so the model does not see the future and train/val are not too dependent.

## When to use it

For any ML/DL model (random forest, SVM, kNN, LSTM) to get realistic out-of-sample estimates. Avoids leakage from future data. Use for comparable, honest metrics across models.

## How it works

Split data in time; for each fold: train on past, validate on future. Optionally purge (drop overlapping samples) and add embargo (gap between train and val). Aggregate metrics across folds. Tools: custom or sklearn TimeSeriesSplit with purge/embargo.

## Inputs

Features and target; time index. Config: purge window, embargo, number of splits (rolling or expanding).

## Outputs

Per-fold and aggregate metrics (e.g. accuracy, Sharpe); optionally fold boundary plots. Location: results/, logs/.

## Related tests

Random forest, SVM, kNN, LSTM (models to validate); rolling origin validation; rolling window backtests.
