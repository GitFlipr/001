# Stress testing and scenarios

## What it is

Evaluate strategy or portfolio under extreme but plausible scenarios: historical (e.g. 2008, COVID), hypothetical (rate shock, vol spike), or Monte Carlo tail events.

## When to use it

Before live deployment; for risk limits and capital; when regulators or internal policy require stress tests.

## How it works

Define scenarios (shocks to prices, vol, rates, correlations). Revalue positions or replay backtest under shocked data. Report PnL, drawdown, breach of limits. Combine with price models for custom paths.

## Inputs

Positions or strategy; scenario definitions (shock sizes, correlations); historical or synthetic data.

## Outputs

PnL and risk metrics per scenario; max drawdown; breach flags. Location: results/, logs/.

## Interpretation

Identify which scenarios hurt most. If drawdown exceeds tolerance, reduce size or add hedges. Use with VaR/CVaR and Monte Carlo.

## Related tests

VaR/CVaR; Monte Carlo; price models; drawdowns; copulas and tail dependence.
