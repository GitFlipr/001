# Order imbalance

## What it is

Measures buy vs sell pressure: e.g. difference between buy and sell volume (from order book or delta volume). Can be correlated with forward returns.

## When to use it

With tick or order-book data (or proxy like delta volume). To see buy/sell pressure and its relationship to price. For execution and strategy logic.

## How it works

Define imbalance (e.g. bid volume - ask volume, or delta volume over window). Compute series; optionally correlate with forward returns. Tools: custom from order book or tape.

## Inputs

Tick or order-book data; or OHLCV with proxy. Config: window, definition of imbalance.

## Outputs

Imbalance series; optionally correlation with forward returns and plots. Location: results/, logs/.

## Related tests

Volume profile; spread_impact; rolling window backtests.
