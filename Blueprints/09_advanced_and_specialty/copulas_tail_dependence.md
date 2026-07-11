# Copulas and tail dependence

## What it is

Copulas model joint distribution apart from marginals. Tail dependence measures joint extremes. For multi-asset risk when correlation is not enough.

## When to use it

Portfolio risk when correlations break in crises; VaR/CVaR with correct joint tails; multi-asset strategies.

## How it works

Fit marginals and copula (Gaussian, t, Clayton, Gumbel). Tail dependence from copula. Simulate joint scenarios. scipy, statsmodels, or copulas package.

## Inputs

Multiple return or PnL series. Config: copula family.

## Outputs

Fitted copula; tail dependence; joint scenarios. results/, logs/.

## Interpretation

High tail dependence: diversification fails in stress. t-copula often fits finance. Use with VaR and stress testing.

## Related tests

VaR/CVaR; stress testing; correlation breakdown; Monte Carlo.
