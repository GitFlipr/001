# ADF test (Augmented Dickey–Fuller)

## What it is

The Augmented Dickey–Fuller (ADF) test checks for a **unit root** in a time series. A unit root implies non-stationarity (e.g. drift, no fixed mean). Rejecting the null of a unit root suggests the series can be treated as stationary, so models that assume stationarity may be valid.

## When to use it

Before using models that assume stationarity (e.g. AR, ARIMA, many regression setups). To decide whether to use levels or differences (e.g. prices vs returns). Often run alongside KPSS and Phillips–Perron for a fuller picture.

## How it works

The test regresses the first difference of the series on its lagged level and lagged differences. The test statistic is compared to critical values; a **low p-value** means reject the null (reject unit root → treat as stationary). Tools: e.g. statsmodels `adfuller`.

## Inputs

Data: one or more time series (e.g. close, returns). Config: max lag for augmentation, significance level.

## Outputs

Per series: ADF statistic, p-value, critical values, conclusion (stationary or not). Location: results/, logs/.

## Interpretation

Reject unit root (low p-value): proceed with stationarity-based models; consider ACF/PACF and baseline models. Do not reject: try first differencing (e.g. use returns) and re-run ADF. Cross-check with KPSS and Phillips–Perron.

## Related tests

KPSS, Phillips–Perron (other unit-root views); ACF/PACF (lag structure); changepoint detection, HMM regime (structure over time).
