# Attribution (PnL breakdown)

## What it is

Breaks down PnL by regime, symbol, or strategy. Where did profit or loss come from?

## When to use it

For reporting. After trade/equity data from pseudo-live or backtests.

## How it works

Load trades/equity; group by dimensions; aggregate PnL. Table or JSON; optionally plots. Pandas or custom.

## Inputs

Trade/equity data. Config: dimensions (regime, symbol, strategy).

## Outputs

Attribution table or JSON. Location: results/, logs/.

## Related tests

Report_generation; pseudo_live; HMM regime; integration_checks.
