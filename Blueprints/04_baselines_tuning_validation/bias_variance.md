# Bias-variance decomposition

## What it is

Splits prediction error into bias (underfitting) and variance (overfitting). Total error = bias + variance + noise. Guides model choice and regularization.

## When to use it

High bias: add features or complexity. High variance: regularize or simplify. Use to set hyperparameters for ML/DL.

## How it works

Fit model many times (e.g. bootstrap); compute predictions on fixed val set. Bias = (mean pred - true)^2; variance = var(preds). Tools: custom loop.

## Inputs

Features and target. Config: model(s), number of runs.

## Outputs

Bias, variance, total error. Location: results/, logs/.

## Related tests

Linear_model, lasso_ridge_regression; random_forest, MLP; mean_squared_error.
