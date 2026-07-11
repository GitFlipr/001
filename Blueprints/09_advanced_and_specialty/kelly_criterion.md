# Kelly criterion

## What it is

Optimal fraction of capital to bet to maximize long-run growth: f = (p*b - q)/b for binary bets (p win prob, q loss, b win/loss ratio). Full Kelly is aggressive; half-Kelly common for safety.

## When to use it

To size positions from edge and payoff; to test if current sizing is over/under aggressive. Uncommon in standard backtests but useful for capital allocation.

## How it works

Estimate win rate and win/loss ratio from backtest or model. Compute Kelly fraction. Compare to current allocation. Optionally run growth simulations at different fractions.

## Inputs

Backtest trades (win/loss, sizes) or assumed p, b. Config: full vs fractional Kelly.

## Outputs

Kelly fraction; suggested vs actual size; optional growth curve. Location: results/, logs/.

## Interpretation

Kelly > current size: could increase risk for growth. Kelly < current: reduce size to avoid blow-up. Always use with robust edge estimates (walk-forward, out-of-sample).

## Related tests

Basic metrics; Sharpe/Sortino/Calmar; drawdowns; rolling window backtests; bias-variance.
