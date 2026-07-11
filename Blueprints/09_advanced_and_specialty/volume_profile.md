# Volume profile

## What it is

Distribution of traded volume across price levels. **POC** = point of control (price with highest volume). **Value area** = price range containing a large fraction of volume (e.g. 70%). Used for support/resistance and entry/exit zones.

## When to use it

To identify high-volume nodes as potential S/R and breakout levels. To compare with time-based charts. As input for order_imbalance and spread_impact when you have tick data.

## How it works

Bin price range; aggregate volume per bin (from OHLCV or tick data). POC = bin with max volume. Value area = contiguous bins around POC that sum to X% of volume. Tools: custom or libraries.

## Inputs

OHLCV or tick data. Config: bin size, lookback.

## Outputs

Volume-by-price profile, POC, value area; optionally plots. Location: results/, logs/.

## Related tests

Order_imbalance; spread_impact; swing detection (levels); rolling window backtests.
