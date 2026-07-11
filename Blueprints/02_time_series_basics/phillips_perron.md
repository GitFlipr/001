# Phillips–Perron test (unit root)

## What it is

The Phillips–Perron (PP) test is another unit root test. Like ADF, it tests for stationarity vs non-stationarity but uses a different correction for serial correlation and heteroskedasticity.

## When to use it

Alongside ADF and KPSS for a fuller view. When the series may have serial correlation; PP's correction can be more appropriate in some cases.

## How it works

Based on a Dickey–Fuller type regression with a non-parametric (Phillips–Perron) adjustment to the statistic. Low p-value means reject unit root (treat as stationary). Tools: e.g. statsmodels PhillipsPerron.

## Inputs

Data: one or more time series. Config: optional lags or kernel.

## Outputs

Per series: PP statistic, p-value, critical values, conclusion. Location: results/, logs/.

## Interpretation

Reject unit root: consistent with stationarity. Do not reject: consider differencing. Use with ADF and KPSS.

## Related tests

ADF test, KPSS; ACF/PACF; changepoint detection, HMM regime.
