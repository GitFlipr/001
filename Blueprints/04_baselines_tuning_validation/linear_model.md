# Linear regression

## What it is

Linear regression predicts a target (e.g. next return, price) as a weighted sum of features plus a constant. It establishes a baseline for predictability and identifies which features have linear signal.

## When to use it

As a baseline before more complex models. To see which features have linear relationship with the target. Results feed into robustness tests (e.g. permutation, bootstrap) and into ML as a benchmark to beat.

## How it works

Fit: target = b0 + b1*x1 + b2*x2 + ... by least squares (minimize MSE). Closed form: \(\hat{\beta} = (X^TX)^{-1}X^Ty\) (normal equation). Output: coefficients, R², residuals. Tools: sklearn LinearRegression, statsmodels OLS. See [Concepts_reference.md](../Concepts_reference.md) (OLS) and [classical linear regression](https://letianzj.github.io/classical-linear-regression.html).

## Inputs

Data: table with target and feature columns (e.g. lags, volume). Config: target, features, optional per-symbol.

## Outputs

Coefficients, R², residuals; optionally per-symbol. Location: results/, logs/.

## Interpretation

Strong R²: use those features in ML; consider regime splits if results differ by regime. Weak fit: try more lags, different target, or focus on risk. Save metrics for basic_metrics and significance tests.

## Related tests

Lasso/Ridge (regularized); logistic regression (binary target); basic_metrics, mean_squared_error, r_squared; permutation, bootstrap (validate significance).
