# Lasso and Ridge regression

## What it is

**Ridge** (L2) adds a penalty on the sum of squared coefficients; it shrinks coefficients but keeps all features. **Lasso** (L1) adds a penalty on the sum of absolute coefficients; it can shrink some coefficients to exactly zero (feature selection). Both reduce overfitting when you have many or correlated features.

## When to use it

When plain linear regression is unstable or overfits. Lasso when you want automatic feature selection (sparse model). Ridge when many features are correlated and you want to keep all but shrink them.

## How it works

Minimize: MSE + alpha * penalty. Ridge: penalty = sum of squared coefficients. Lasso: penalty = sum of absolute coefficients. Tune alpha (e.g. via cross-validation or grid search). Tools: sklearn Ridge, Lasso.

## Inputs

Data: target and features. Config: model type (ridge/lasso), alpha, target, features.

## Outputs

Coefficients (possibly sparse for Lasso), R² or MSE, chosen alpha if tuned. Location: results/, logs/.

## Interpretation

Lasso zeros: use non-zero features in simpler models or ML. Ridge: use all coefficients; compare R² with plain linear. Tune alpha via grid search or random search.

## Related tests

Linear regression (no penalty); basic_metrics, r_squared; grid_search, random_search (tune alpha); random_forest, SVM (non-linear baselines).
