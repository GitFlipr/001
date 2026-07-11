# Hurst exponent

## What it is

Measure of long-memory or mean reversion in a series. Values above 0.5 suggest trending; below 0.5 mean-reverting; near 0.5 random walk. Estimated via rescaled range or DFA.

## When to use it

To test if returns or volatility are persistent or mean-reverting. Informs trend-following vs mean-reversion strategy choice.

## How it works

Rescaled range: range of cumulative deviations over windows, scaled by std; fit log range vs log window to get exponent. Alternatives: DFA, wavelet. Use arch, nolds, or custom code.

## Inputs

Time series. Config: window sizes, method.

## Outputs

Hurst exponent and optional confidence interval. results/, logs/.

## Interpretation

Above 0.5: momentum filters may help. Below 0.5: mean-reversion or shorter horizon. Cross-check with ADF and ACF.

## Related tests

ADF test; KPSS; ACF/PACF; regime-switching; entropy.
