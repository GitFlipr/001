# Pseudo-live testing

## What it is

Simulated live evaluation: at each step use only past data, generate signal, simulate execution (with latency and slippage), update equity. No future data; as close to live as possible on historical data.

## When to use it

Before going live. To get equity curve, trades, and metrics (return, Sharpe, max DD, hit rate) under realistic execution assumptions.

## How it works

Loop over time; at each step: compute signal from past data; simulate order (limit/market, slippage, latency); update positions and equity. Record trades and equity. Compute final metrics. Tools: custom backtester with execution layer.

## Inputs

Data; strategy; config: execution assumptions (latency, slippage), data path.

## Outputs

Equity curve, trades, metrics (return, Sharpe, max DD, hit rate); optionally trade list and plots. Location: results/, logs/.

## Related tests

Rolling window backtests; rolling origin validation; Sharpe, drawdowns, VaR/CVaR; integration_checks.
