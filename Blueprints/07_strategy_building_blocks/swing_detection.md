# Swing detection (swing highs and lows)

## What it is

Finds local highs and lows in price (swing highs/lows). Used for structure and for Fibonacci and Gann tools.

## When to use it

To feed Fibonacci retracements, extensions, Gann. To define trend/range structure. For technical strategies.

## How it works

Lookback window; swing high = bar with highest high in window; swing low = lowest low. Output indices and prices. Tools: custom or zigzag.

## Inputs

Price (high, low). Config: lookback, min swing size.

## Outputs

Swing indices and prices; optionally plots. Location: results/, logs/.

## Related tests

Fibonacci retracements, extensions; Gann angles; statistical significance.
