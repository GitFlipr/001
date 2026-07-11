# Structural break tests (Chow, Zivot–Andrews)

## What it is

Formal **parametric tests** for a known or unknown break in regression parameters (e.g. mean, trend, variance). **Chow test:** assumes you know the break date; tests whether coefficients differ before vs after. **Zivot–Andrews:** endogenously searches for a single break in the ADF regression (unit root with structural break).

## When to use it

When you have a **candidate break date** (e.g. policy change, regime shift): use Chow to test if parameters changed. When you suspect a break but don't know when: Zivot–Andrews finds it and tests unit root allowing for that break. Complements changepoint detection (which is often non-parametric or model-free).

## How it works

- **Chow test:** Split sample at break date; estimate model on pre and post; compute F-statistic comparing restricted (no break) vs unrestricted (separate coefficients). Reject if F is large.
- **Zivot–Andrews:** For each candidate break date, run ADF-style regression with break dummies; pick break that minimizes the ADF t-statistic; compare to critical values. Tools: statsmodels (Chow), or `urca`/custom for Zivot–Andrews.

## Inputs

Data: time series (or regression data). Config: break date (Chow) or search range (Zivot–Andrews); model specification; significance level.

## Outputs

Test statistic; p-value or critical value comparison; break date (if endogenous); conclusion. Location: results/, logs/.

## Interpretation

Chow significant: parameters changed at the break; consider splitting models or using dummies. Zivot–Andrews: if unit root rejected allowing for break, series may be trend-stationary with a one-time shift.

## Related tests

Changepoint detection (non-parametric, multiple breaks); ADF test (unit root without break); HMM regime (smooth state sequence); rolling window backtests (split at breaks).