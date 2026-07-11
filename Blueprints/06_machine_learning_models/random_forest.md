# Random forest

## What it is

Ensemble of decision trees (classification or regression); predictions are averaged or voted. Captures non-linear and interaction effects; gives feature importance.

## When to use it

For non-linear prediction of direction, returns, or volatility. As a baseline before LSTM/Transformer for sequence-heavy problems. For interpretable feature importance.

## How it works

Train many trees on bootstrap samples and random feature subsets; aggregate predictions. Output: metrics (accuracy, MAE, RMSE), feature importances. Tools: sklearn RandomForestClassifier/Regressor.

## Inputs

Features and target. Config: target, features, train/val split or time_series_cv.

## Outputs

Metrics, feature importances; optionally plots. Location: results/, logs/.

## Related tests

Linear_model, logistic_regression (baselines); SVM, kNN; time_series_cv; rolling window backtests; Sharpe, drawdowns.
