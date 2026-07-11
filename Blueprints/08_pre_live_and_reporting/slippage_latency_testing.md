# Slippage and latency testing (pre-live)

## What it is

Measures the gap between **simulated execution** (backtest/pseudo-live) and **actual execution** (paper or live). **Slippage:** difference between expected fill price and actual; **latency:** delay from signal to order to fill. Both can turn a profitable backtest into a losing live strategy.

## When to use it

Before going live. After changing execution logic or venue. To calibrate slippage and latency assumptions in pseudo-live. When backtest and paper results diverge.

## How it works

**Slippage testing:**
1. Record intended fill price (e.g. mid, VWAP) and actual fill from paper/live or exchange data.
2. Compute: (actual − intended) / intended per trade; aggregate (mean, std, percentiles).
3. By side (buy/sell), symbol, size bucket. Use to set slippage assumptions in backtest.

**Latency testing:**
1. Timestamp: signal generated, order sent, order acknowledged, fill received.
2. Compute delays: signal→send, send→ack, ack→fill. Percentiles (p50, p95, p99).
3. Identify bottlenecks (network, exchange, strategy loop). Set max latency for "fill guaranteed" logic.

**Paper trading comparison:**
- Run same strategy in backtest (with slippage/latency model) vs paper.
- Compare equity curves, fill prices, rejection rates. Tune model until backtest matches paper.

## Inputs

Paper/live trade log (timestamp, symbol, side, size, intended price, actual fill); or historical fills. Config: symbols, period, aggregation level.

## Outputs

Slippage stats (mean, std, percentiles) per symbol/side; latency percentiles; comparison backtest vs paper. Location: results/, logs/.

## Interpretation

High slippage: increase cost assumption or improve execution (TWAP, limit orders). High latency: optimize code, change venue, or avoid strategies that need sub-second fills. Backtest vs paper mismatch: revise execution model.

## Related tests

Pseudo_live_testing; VWAP/TWAP; integration_checks; kill_switch_circuit_breaker; report_generation.