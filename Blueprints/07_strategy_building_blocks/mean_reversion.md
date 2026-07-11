# Mean reversion (single-series)

## What it is

**Time-series mean reversion:** price tends to revert to a long-term mean. Modeled by Ornstein–Uhlenbeck (OU) process: dx_t = θ(μ − x_t)dt + σ dW_t. Discrete analogue: AR(1). **Half-life** = ln(2)/θ measures speed of reversion.

**Z-score strategy:** trade size negatively proportional to z-score = (price − rolling_mean) / rolling_std. Scale in/out as price deviates.

## When to use it

When a single series (e.g. FX rate, spread) is statistically mean-reverting. Requires ADF test (reject unit root), Hurst < 0.5, or variance ratio supporting mean reversion. Use half-life for lookback window. Fails in trending regimes—combine with regime detection (HMM).

## How it works

1. **Test:** ADF, Hurst exponent, variance ratio (Phase 2).
2. **Estimate half-life:** Regress Δx_t on x_{t-1}; θ ≈ −coef; half-life = −ln(2)/coef.
3. **Strategy:** Rolling mean and std over half-life window; z-score = (price − mean)/std; target_size = −z × scale.
4. **Entry/exit:** Scale in when |z| large; scale out when z crosses zero.

Tools: statsmodels ADF; custom Hurst; sklearn for half-life regression.

## Inputs

Price or spread series. Config: lookback (e.g. half-life), scale factor, regime filter (optional).

## Outputs

Half-life; z-score series; position sizes; backtest PnL. Location: results/, logs/.

## Related tests

adf_test; hurst_exponent; variance_ratio_test; cointegration_pairs_trading (multi-series); hmm_regime.

## External reference

[Mean reversion (letianzj)](https://letianzj.github.io/mean-reversion.html).
