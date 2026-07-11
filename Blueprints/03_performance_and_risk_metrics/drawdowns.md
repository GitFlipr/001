# Drawdowns

## What it is

Peak-to-trough decline in equity: **max drawdown (MDD)**, average drawdown, duration (how long underwater). Answers: how bad can losses get and how long do they last?

## When to use it

To size positions and set stop-outs so max drawdown stays within tolerance. To compare strategies by worst drawdown and time underwater. Input for Calmar ratio and risk narratives.

## How it works

From equity curve: track running peak; drawdown at each time = (peak - current) / peak (or in currency). Max drawdown = max of that. Duration = length of contiguous underwater period. Tools: custom or pandas.

## Inputs

Equity curve or return series (e.g. from backtests). Config: window or reporting format.

## Outputs

Max drawdown, average drawdown, duration stats; optionally drawdown-over-time plot. Location: results/, logs/.

## Related tests

Sharpe, Sortino, Calmar; VaR/CVaR; pseudo_live_testing; report_generation.
