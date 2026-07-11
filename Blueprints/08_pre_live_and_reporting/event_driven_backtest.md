# Event-driven backtest framework

## What it is

**Event-driven** backtest architecture: data, orders, fills, and signals are **events** dispatched by an event engine to subscribed handlers. Strategies react to bar/tick events; order manager and brokerage handle execution. Same code structure can extend to live trading (feed live data into engine).

## When to use it

When you need a backtest system that mirrors live architecture—no rewrite for production. Enables unit testing, replay of historical tick data, and turn-key transition to live. Contrast with vectorized backtests (simpler but less realistic execution path).

## How it works

**Components:** Event engine (dispatch loop) → Data feed (bar/tick events) → Strategy (generates orders) → Order manager (tracks orders) → Backtest brokerage (simulates fills, commission, slippage) → Performance manager (metrics, pyfolio-compatible output).

**Flow:** Engine gets next bar from data feed → puts event on queue → handlers (strategy, order manager, etc.) process event → strategy may place order → brokerage fills → update positions and PnL.

## Inputs

OHLCV data; strategy class; config (commission, slippage). Optional: parameter search (grid over strategy params, e.g. MA windows).

## Outputs

Equity curve; fill log; performance stats (Sharpe, drawdown, etc.); optionally pyfolio tearsheet. Location: results/, logs/.

## Related tests

pseudo_live_testing (no-peek simulation); rolling_window_backtests (walk-forward); report_generation; grid_search (parameter optimization).

## External reference

[Backtest trading strategies (quanttrader) (letianzj)](https://letianzj.github.io/quanttrading-backtest.html). Compare: Backtrader, PyAlgoTrade, Quantopian (legacy).
