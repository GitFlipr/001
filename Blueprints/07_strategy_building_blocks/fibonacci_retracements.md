# Fibonacci retracements

## What it is

Computes retracement levels (e.g. 38.2%, 61.8%) between a swing high and swing low. Used as potential support/resistance on pullbacks.

## When to use it

To define entry zones on pullbacks. To compare price behaviour at these levels vs random (statistical significance). Use in strategy logic as levels.

## How it works

Given swing high and low, compute price levels at Fibonacci ratios of the range (e.g. 0.382, 0.5, 0.618). Output levels per swing. Tools: custom from swing_detection output.

## Inputs

Swing highs/lows (from swing_detection) or price series. Config: which levels to compute.

## Outputs

Levels per swing; optionally hit rates or plots. Location: results/, logs/.

## Related tests

Swing detection; Fibonacci extensions; Gann angles; statistical significance.
