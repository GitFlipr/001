# Kalman filter pairs trading

## What it is

Pairs trading with **dynamic hedge ratio** estimated online via Kalman filter. State θ = [intercept, slope] evolves (random walk); observation y_t = [1, x_t] θ + v_t. The spread = y_t − F_t θ_{t|t-1}; its variance gives Bollinger band width. Avoids look-ahead bias from rolling OLS.

## When to use it

When the cointegration relationship (hedge ratio) **changes over time**—e.g. EWA–EWC slope drifts. Kalman provides step-by-step updates; no need to re-estimate on rolling window. Superior to static OLS when regime shifts.

## How it works

1. **State:** θ_t = [a_t, b_t] (intercept, slope); transition θ_t = θ_{t-1} + w_t.
2. **Observation:** y_t (e.g. EWC) = [1, x_t] θ_t + v_t where x_t = EWA.
3. **Filter:** Predict θ_{t|t-1}, P_{t|t-1}; observe (x_t, y_t); residual = spread; update θ_{t|t}, P_{t|t}.
4. **Bollinger:** Band = spread ± δ√S_t (S_t from Kalman residual covariance).
5. **Trading:** Same logic as cointegration_pairs_trading—short/long spread at bands.

Tools: PyKalman, filterpy, or custom. Use kf.filter_update for step-by-step.

## Inputs

Two price series (e.g. EWA, EWC). Config: initial state, transition/observation covariances.

## Outputs

Dynamic hedge ratio (slope) over time; spread; backtest PnL. Location: results/, logs/.

## Related tests

cointegration_pairs_trading (static version); [kalman_filter_regression](../04_baselines_tuning_validation/kalman_filter_regression.md); mean_reversion.

## External reference

[Kalman filter pairs trading (letianzj)](https://letianzj.github.io/kalman-filter-pairs-trading.html).
