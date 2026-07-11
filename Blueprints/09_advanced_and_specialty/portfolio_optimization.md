# Portfolio optimization (mean-variance, efficient frontier)

## What it is

**Modern Portfolio Theory (MPT)** trades off return and risk. For n assets with expected return vector μ and covariance matrix Σ, portfolio return μ_p = w^T μ and variance σ_p² = w^T Σ w. Risk depends on variance **and** correlations—diversification matters.

Key portfolios:
- **Global Minimum Variance (GMV)** — lowest risk; closed form: w* = Σ⁻¹ 1 / (1^T Σ⁻¹ 1).
- **Efficient frontier** — set of portfolios that maximize return for each risk level (or minimize risk for each return level).
- **Tangency portfolio** — maximizes Sharpe ratio (μ_p − r_f) / σ_p; closed form: w* = Σ⁻¹(μ − r_f 1) / (1^T Σ⁻¹(μ − r_f 1)).
- **Risk parity** — equal risk contribution (ERC); MRC_i = (Σw)_i/σ_p; RC_i = w_i·MRC_i. Solve to minimize Σ_i Σ_j (w_i(Σw)_i − w_j(Σw)_j)².
- **Maximum diversification** — maximize w^T σ / √(w^T Σ w).

**Two-fund theorem:** The efficient frontier is a linear combination of GMV and max-return portfolios. Monthly rebalance backtests compare GMV, max Sharpe, risk parity, max diversified, equal weights.

## When to use it

To allocate across multiple assets or strategies; to construct benchmarks; to test whether a strategy improves the efficient frontier. Use when you have multiple uncorrelated or negatively correlated return streams (e.g. strategies, symbols) and want optimal weights.

## How it works

1. Estimate μ and Σ from historical returns (or use shrinkage, factor models).
2. Solve quadratic programs: minimize w^T Σ w subject to w^T 1 = 1 and optionally w^T μ = μ_o (target return).
3. GMV: closed form or cvxopt/scipy QP. Tangency: maximize (w^T μ − r_f) / √(w^T Σ w) subject to w^T 1 = 1.
4. Efficient frontier: sweep target returns and solve min-variance for each; plot risk vs return.

Tools: numpy for closed form; cvxopt, scipy.optimize, or PyPortfolioOpt for constrained optimization.

## Inputs

Historical returns (or precomputed μ, Σ); optional risk-free rate r_f for tangency. Config: short-selling allowed or not; target return range for frontier.

## Outputs

Optimal weights (GMV, tangency, efficient frontier points); plot of efficient frontier and candidate portfolios; allocation transition across return levels. Location: results/, logs/.

## Interpretation

GMV: defensive allocation. Tangency: aggressive if r_f is low; useful as benchmark. Frontier: identify where your strategy sits vs optimal. Negative weights imply short sales; add constraints if not allowed.

## Related tests

Sharpe/Sortino/Calmar (tangency uses Sharpe); VaR/CVaR (portfolio risk); var_cvar (Component VaR for attribution); factor_exposure; correlation_breakdown.

## External references

[Portfolio management one (letianzj)](https://letianzj.github.io/portfolio-management-one.html) — GMV, efficient frontier, tangency portfolio, Python/cvxopt implementation.

[Portfolio management two (letianzj)](https://letianzj.github.io/portfolio-management-two.html) — Risk parity, maximum diversification portfolio, monthly rebalance backtest (GMV, max Sharpe, risk parity, max diversified, equal weights).
