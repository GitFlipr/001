# Correlation breakdown

## What it is

Test if correlations between assets or factors are stable or break in stress. Rolling correlation; correlation in calm vs stressed periods; tail correlation.

## When to use it

Multi-asset or factor strategies; when diversification may fail in crises. Complements copulas and stress tests.

## How it works

Rolling correlation; split sample by vol and compare; tail correlation of exceedances; structural break tests. pandas, statsmodels.

## Inputs

Two or more return series. Config: window, stress threshold.

## Outputs

Rolling correlation; correlation by regime; tail correlation. results/, logs/.

## Interpretation

Correlation rising in stress: diversification fails when needed. Adjust limits or stress scenarios.

## Related tests

Copulas; stress testing; VaR/CVaR; regime-switching.
