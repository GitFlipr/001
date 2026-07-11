# Spread and market impact

## What it is

**Spread**: difference between best ask and best bid. **Market impact**: how much your order moves the price. Together they model execution cost for sizing and slippage assumptions.

## When to use it

When you have tick or order-book data. To set execution cost assumptions in backtests and pseudo-live. For position sizing and risk (cost per trade).

## How it works

Estimate spread (e.g. time-weighted average of best ask - best bid). Estimate impact (e.g. linear in order size or sqrt; fit from data). Output spread estimates and impact coefficients; optionally cost curves. Tools: custom from order book/tick data.

## Inputs

Tick or order-book data. Config: impact model (e.g. linear in volume), spread estimator.

## Outputs

Spread estimates, impact coefficients; optionally cost curves. Location: results/, logs/.

## Related tests

Volume profile; order_imbalance; pseudo_live_testing (slippage); VaR (execution risk).
