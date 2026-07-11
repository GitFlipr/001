# Rolling window backtests

## What it is

Backtest a strategy over many fixed-length windows that roll through time. Shows how performance changes across periods and whether the strategy is stable.

## When to use it

To avoid overfitting to one long backtest. To detect regime sensitivity (e.g. works in bull but not bear). To produce a distribution of outcomes (e.g. Sharpe per window) for risk and reporting.

## How it works

Define window length and step. For each window: run backtest; compute metrics (return, Sharpe, max DD). Aggregate (mean, median, percentiles) across windows. Tools: custom backtester.

## Inputs

Price/return data; strategy; config: window length, step, strategy params.

## Outputs

Metrics per window; aggregate stats; optionally plots. Location: results/, logs/.

## Related tests

Rolling origin validation; pseudo_live_testing; Sharpe, drawdowns, VaR/CVaR; changepoint, HMM (regime).
