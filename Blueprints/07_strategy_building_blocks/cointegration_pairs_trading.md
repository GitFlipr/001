# Cointegration and pairs trading

## What it is

**Cointegration:** two (or more) non-stationary series share a common trend; a linear combination (spread) is stationary. **Pairs trading:** trade the spread when it deviates from mean. Hedge ratio from OLS (Engle–Granger) or Johansen test.

**Statistical tests:** CADF (cointegrated ADF on residuals) or Johansen (joint estimation of rank and eigenvectors as hedge ratios).

## When to use it

When two correlated assets (e.g. EWA–EWC, sector ETFs) are cointegrated. Spread is mean-reverting even when each price is not. Use rolling window or walk-forward to avoid look-ahead bias; alternatively Kalman filter for online hedge ratio.

## How it works

1. **Identify pairs:** correlation, economic rationale (e.g. EWA/EWC both commodity-driven).
2. **Cointegration test:** Regress A on B (or both ways); ADF on residuals. Or Johansen test for rank and hedge ratios.
3. **Spread:** spread_t = price_A − hedge_ratio × price_B (price spread) or return spread.
4. **Trading:** Bollinger bands on spread—short when spread > upper band, long when < lower band; flat when crosses mean.

## Inputs

Two price series. Config: test (CADF/Johansen), rolling window, Bollinger params (e.g. 2σ).

## Outputs

Hedge ratio; spread series; ADF/Johansen stats; backtest PnL. Location: results/, logs/.

## Related tests

mean_reversion (spread strategy); kalman_filter_pairs_trading (dynamic hedge); linear_model (hedge ratio); adf_test, variance_ratio_test.

## External reference

[Cointegration pairs trading (letianzj)](https://letianzj.github.io/cointegration-pairs-trading.html).
