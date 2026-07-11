# R-squared (R²)

## What it is

**R²** = fraction of variance in the target explained by the model. R² = 1 − (SS_residual / SS_total). Scale from 0 (no better than predicting the mean) to 1 (perfect fit). Used to compare linear and regularized models and to document baseline fit.

## When to use it

To compare regression models on the same data. To document how much of the variation is captured. Reported with MSE in basic_metrics and used in significance tests (e.g. permutation) to see if improvement is real.

## How it works

SS_residual = sum((y_true - y_pred)**2). SS_total = sum((y_true - y_mean)**2). R² = 1 - SS_residual/SS_total. Tools: sklearn r2_score, or manual.

## Inputs

Data: observed target and predictions. Config: which model(s) or series.

## Outputs

R² per model or per symbol. Location: results/, logs/.

## Interpretation

Strong R²: use those features in ML; consider regime splits if R² differs by regime. Weak R²: try more lags, different target, or non-linear models. High train R² but low val R²: overfitting; regularize or simplify.

## Related tests

Mean_squared_error, basic_metrics; linear_model, lasso_ridge_regression; permutation, bootstrap (test significance of improvement).
