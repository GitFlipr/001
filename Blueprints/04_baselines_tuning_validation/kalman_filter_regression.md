# Kalman filter linear regression (Dynamic Linear Model)

## What it is

**Dynamic Linear Model (DLM):** regression coefficients β (intercept, slope) evolve over time via state transition (e.g. random walk). Kalman filter recursively updates the state as new observations arrive. State-space: θ_k = θ_{k-1} + w_t (transition); y_t = F_t θ_t + v_t (measurement).

## When to use it

When the relationship between X and y **changes over time**—e.g. pairs trading hedge ratio, rolling beta, cointegration spread. Avoids look-ahead bias; provides online/recursive estimates. Used in EWA-EWC pairs (Ernie Chan), equilibrium price estimation.

## How it works

Predict: θ_{k|k-1}, P_{k|k-1}. Update: residual ỹ_k = y_k − F_k θ_{k|k-1}; Kalman gain K_k; posterior θ_{k|k}, P_{k|k}. Repeat. F_t = [1, x_t] for simple regression. Tools: PyKalman, filterpy, or custom.

## Inputs

Data: target and feature over time. Config: initial state θ_{0|0}, P_{0|0}; transition covariance W; observation covariance V.

## Outputs

State estimates θ_{k|k} over time; evolution of intercept and slope; optionally prediction intervals. Location: results/, logs/.

## Related tests

bayesian_regression (recursive updates); linear_model (OLS baseline); [cointegration_pairs_trading](../07_strategy_building_blocks/cointegration_pairs_trading.md), [kalman_filter_pairs_trading](../07_strategy_building_blocks/kalman_filter_pairs_trading.md).

## External reference

[Kalman filter linear regression (letianzj)](https://letianzj.github.io/kalman-filter-linear-regression.html).
