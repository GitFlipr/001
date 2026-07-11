# VWAP and TWAP (execution benchmarks)

## What it is

**VWAP (Volume-Weighted Average Price)** is the average price weighted by volume over a period; used as a benchmark for execution quality. **TWAP (Time-Weighted Average Price)** is the simple average price over time. Both are execution building blocks: slice orders to target VWAP/TWAP and minimize market impact.

## When to use it

For **execution algorithms** when trading large orders. As a benchmark to compare fills vs "fair" price. In backtests: simulate execution at VWAP/TWAP to approximate realistic fill prices. For reporting: "we traded at X bps better than VWAP."

## How it works

- **VWAP:** Sum(price × volume) / Sum(volume) over the period. Often computed incrementally (cumulative). Session VWAP resets at session open.
- **TWAP:** Mean(price) over the period. Simpler; no volume needed.
- **Execution:** Split order across time to match volume curve (VWAP) or evenly (TWAP). In backtest: assume fill at VWAP/TWAP for the slice; or use historical VWAP as benchmark.

## Inputs

OHLCV (for VWAP) or OHLC (for TWAP); period (e.g. session, day). Config: period start/end; session definition.

## Outputs

VWAP and TWAP series; optionally execution algo logic for slicing. Location: results/, logs/.

## Interpretation

Fill price better than VWAP: good execution. Worse: review slippage, timing, venue. In backtests, using VWAP fill assumption is more realistic than mid-price for large orders.

## Related tests

Slippage and latency testing (Phase 8); spread impact; order imbalance; report_generation; attribution (execution vs alpha).