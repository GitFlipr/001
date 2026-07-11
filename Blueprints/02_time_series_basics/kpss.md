# KPSS test (trend stationarity)

## What it is

The KPSS test checks whether a series is **trend-stationary** (fluctuates around a trend). The null is stationarity (or trend-stationarity); **rejecting** the null means the series has a unit root or is otherwise non-stationary. It is often used as the opposite view to the ADF test.

## When to use it

Alongside ADF and Phillips–Perron to get a fuller picture of stationarity. When you want to test "is it trend-stationary?" rather than "is there a unit root?".

## How it works

The test builds a statistic from the residuals of a regression of the series on a constant (and optionally a trend). The statistic is compared to critical values; a **high** value (or low p-value depending on implementation) leads to rejection of the null of stationarity. Config: regression type (constant, or constant + trend). Tools: e.g. statsmodels `kpss`.

## Inputs

Data: one or more time series. Config: regression type (c or ct), optional lags.

## Outputs

Per series: KPSS statistic, p-value (or critical value comparison), conclusion. Location: results/, logs/.

## Interpretation

Reject null: series is not trend-stationary; consider differencing or other treatment. Do not reject: consistent with trend-stationarity. Use with ADF/PP: if ADF says "no unit root" and KPSS says "stationary", you have stronger evidence.

## Related tests

ADF test, Phillips–Perron (unit-root and stationarity); ACF/PACF; changepoint detection, HMM regime.
