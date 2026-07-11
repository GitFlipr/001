# Gradient boosting (XGBoost, LightGBM, CatBoost)

## What it is

**Gradient boosting** builds an ensemble by sequentially adding trees that correct the errors of the previous ensemble. **XGBoost**, **LightGBM**, and **CatBoost** are efficient implementations widely used in quant finance. Often outperform random forest when tuned; handle mixed and categorical features well.

## When to use it

For **non-linear prediction** of returns, direction, or volatility. When you have tabular features (not just sequences). As a step up from random forest when you need higher accuracy. Common in Kaggle and production quant systems. Handle categorical features natively (CatBoost, LightGBM).

## How it works

1. Start with initial prediction (e.g. mean).
2. For each tree: fit residuals (gradient of loss); add tree with shrinkage (learning rate); update ensemble.
3. Repeat for N trees. Prediction = sum of tree outputs.
4. Hyperparameters: n_estimators, max_depth, learning_rate, subsample, colsample. Tools: `xgboost`, `lightgbm`, `catboost`.

## Inputs

Features and target. Config: target, features, train/val split or time_series_cv; hyperparameters or tuned via grid/Bayesian.

## Outputs

Metrics; feature importances (gain, split count); optionally SHAP values. Location: results/, logs/.

## Interpretation

Often beats random forest on structured tabular data. LightGBM faster for large datasets; XGBoost robust default; CatBoost best for categoricals. Use with time-series CV; avoid leakage from future data.

## Related tests

Random forest (alternative ensemble); feature_importance_shap (interpretability); time_series_cv; grid search, Bayesian optimization; linear_model (baseline).