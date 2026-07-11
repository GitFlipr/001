# Order flow toxicity (VPIN-style)

## What it is

Measures informed or aggressive order flow that may precede moves. VPIN uses order imbalance and volume to estimate toxicity. Needs tick or trade data.

## When to use it

Execution timing; avoid trading when toxicity is high; microstructure or HFT-style filters. Uncommon in standard backtests.

## How it works

Partition volume into buys and sells. Imbalance over volume buckets. VPIN: cumulative imbalance over total volume in window. High VPIN suggests informed flow.

## Inputs

Trade data: price, size, side. Config: bucket size, window.

## Outputs

Toxicity series; optional signals. results/, logs/.

## Interpretation

Spike: possible adverse selection; consider delaying or reducing size. Use with order imbalance and spread.

## Related tests

Order imbalance; spread and impact; volume profile; pseudo-live.
