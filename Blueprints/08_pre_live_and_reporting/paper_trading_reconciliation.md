# Paper trading reconciliation (pre-live)

## What it is

Audit that **paper trading** matches expectations: positions, PnL, and trades reconcile with strategy logic and data. Catches bugs (wrong sizing, wrong symbol, double fills) before they happen in live.

## When to use it

During and after paper trading. Before promoting a strategy to live. When paper results diverge from backtest. As a periodic integrity check.

## How it works

**1. Position reconciliation**
- Strategy's internal position state vs broker/exchange reported positions.
- Match symbol, size, side. Flag any discrepancy (e.g. orphaned position, sync bug).

**2. Trade reconciliation**
- Every fill from broker has a matching strategy-generated order (or expected fill).
- Check: symbol, side, size, timestamp (within tolerance). Flag duplicates, missing fills, wrong sizes.

**3. PnL reconciliation**
- Mark-to-market PnL from positions + realized PnL from closed trades.
- Compare to broker PnL report. Investigate differences (fees, corporate actions, timing).

**4. Data alignment**
- Bars used for signals align with bars used for backtest (same source, same timing).
- No future leakage: signal at time T uses only data up to T.

**5. Audit trail**
- Log: every signal, every order, every fill with timestamps. Reproducible from logs.

## Inputs

Paper trade log; broker position and PnL reports; strategy state logs; config (symbols, data source).

## Outputs

Reconciliation report: pass/fail per check; list of discrepancies; matched vs unmatched trades; PnL diff. Location: results/, logs/.

## Interpretation

All reconciled: paper is trustworthy; proceed to live with caution. Discrepancies: fix before live; may indicate logic bug, feed bug, or timing issue.

## Related tests

Pseudo_live_testing; integration_checks; slippage_latency_testing; attribution (PnL breakdown); report_generation.