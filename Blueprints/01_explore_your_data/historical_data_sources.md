# Historical market data sources

## What it is

Free and low-cost sources for OHLCV and related data: Yahoo Finance (yfinance), Pandas DataReader (Alpha Vantage, FRED), Quandl, Interactive Brokers (conditional). Covers stocks, indices, FX, crypto, futures, intraday.

## When to use it

Before Phase 1 EDA: you need data to explore. Choose source by asset class (stocks: yfinance; rates: FRED; commodities: Quandl; futures/intraday: IB). Persist immediately—historical APIs may change or limit retention.

## How it works

**yfinance:** Daily and intraday (1m up to ~10 days); stocks, indices, FX (EURUSD=X), crypto (BTC-USD). **pandas_datareader:** Alpha Vantage, FRED (macro, yield curves). **Quandl:** Commodities (e.g. CME_CL1), many asset classes. **IB:** One-second bars, 180 days; requires funded account. Aggregate: resample 1m → 5m, etc.

## Inputs

Symbols; date range; interval (1d, 1m). Config: API keys (Alpha Vantage, Quandl); output path.

## Outputs

OHLCV CSV or DataFrame; optionally fundamentals. Location: data/, configurable.

## Related tests

data_quality_checks (validate after load); data loader in backtest pipeline.

## External references

[Free historical market data (letianzj, Medium)](https://medium.com/@letian.zj/free-historical-market-data-download-in-python-74e8edd462cf) — yfinance, pandas_datareader, Quandl, IB. Code: [hist_downloader.py](https://github.com/letianzj/QuantResearch/blob/master/backtest/hist_downloader.py).
