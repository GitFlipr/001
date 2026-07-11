# Omega ratio

## What it is

The **Omega ratio** measures the probability-weighted ratio of gains to losses relative to a threshold (often zero). It uses the full return distribution, not just mean and variance, so it accounts for skew and fat tails.

## When to use it

When returns are **non-normal** (skewed, heavy-tailed) and Sharpe may be misleading. To compare strategies where downside matters more than upside. For tail-aware risk assessment without assuming a specific distribution.

## How it works

For threshold L (e.g. 0): Ω(L) = (sum of gains above L) / (sum of losses below L), where gains/losses are weighted by their probability. Equivalently: ratio of the area under the CDF above L to the area below L. Higher Ω = more upside relative to downside. Tools: custom implementation; requires full return distribution or empirical CDF.

## Inputs

Return series (or equity curve). Config: threshold (default 0); optionally risk-free rate.

## Outputs

Omega ratio; optional plot of gains vs losses. Location: results/, logs/.

## Interpretation

Ω &gt; 1: more probability mass in gains than losses. Ω = 1: break-even. Higher Ω preferred. Useful when Sharpe is similar across strategies but distributions differ.

## Related tests

Sharpe/Sortino/Calmar (other ratios); VaR/CVaR (tail risk); drawdowns; bootstrap (to get distribution of Omega).