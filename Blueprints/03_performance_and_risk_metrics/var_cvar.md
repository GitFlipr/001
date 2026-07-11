# VaR and CVaR (Value at Risk and Expected Shortfall)

## What it is

**VaR**: loss level exceeded with a given probability (e.g. 1% → 99% VaR). **CVaR (Expected Shortfall)**: average loss when VaR is exceeded. Both measure tail risk.

For portfolios: **Marginal VaR (MVaR)** = derivative of portfolio VaR w.r.t. dollar change in asset i; **Component VaR (CVaR_i)** = MVaR_i × V_i — components sum exactly to portfolio VaR. Useful for risk attribution.

## When to use it

To set capital and risk limits (e.g. do not risk more than X at 99% confidence). CVaR is coherent and more sensitive to tail shape; use for sizing when tails matter. For regulatory or internal risk reporting. Marginal/Component VaR for multi-asset portfolios and risk decomposition.

## How it works

Three main approaches:

1. **Historical VaR** — percentile of empirical return/PnL distribution (e.g. 1st percentile).
2. **Parametric (delta-normal / variance-covariance) VaR** — assuming normal returns: VaR_p = z × σ_p × V, where z = inverse normal of confidence level (e.g. 95% → z ≈ 1.645). Portfolio variance σ_p² = w^T Σ w. Good when correlations matter; diversification reduces portfolio VaR below sum of individual VaRs.
3. **Monte Carlo VaR** — simulate many paths from a fitted model; VaR = percentile of simulated losses.

**Marginal VaR:** MVaR_i = ∂VaR_p/∂V_i = z × (σ_ip / σ_p) = z × σ_p × β_ip (where β_ip = σ_ip/σ_p² is beta of asset i to portfolio).  
**Component VaR:** CVaR_i = MVaR_i × V_i; Σ CVaR_i = VaR_p.

**CVaR (Expected Shortfall):** mean of returns (or losses) below the VaR threshold.

Tools: custom implementation; `arch`, `quantlib`, `pyfolio`, or risk libraries.

## Inputs

Return or PnL series (e.g. from backtests); for portfolios: weights, covariance matrix, dollar values. Config: confidence level (e.g. 0.99), method (historical, parametric, Monte Carlo).

## Outputs

VaR and CVaR at chosen level(s); optionally by period or rolling. For portfolios: Marginal VaR, Component VaR per asset. Location: results/, logs/.

## Related tests

Sharpe, drawdowns, Calmar; distribution fitting (parametric VaR); report_generation; attribution (PnL/risk decomposition); [portfolio_optimization](../09_advanced_and_specialty/portfolio_optimization.md).

## External reference

[Value at Risk (letianzj)](https://letianzj.github.io/value-at-risk-one.html) — variance-covariance method, Marginal VaR, Component VaR, portfolio example.
