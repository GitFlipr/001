# ACF and PACF (autocorrelation and partial autocorrelation)

## What it is

**ACF (autocorrelation function)** measures the correlation of a series with its past values at each lag. **PACF (partial autocorrelation function)** measures the correlation at a given lag after removing the effect of shorter lags. Together they help choose the order of AR and MA terms (e.g. for ARIMA) and spot seasonality.

## When to use it

To choose AR(p) and MA(q) orders for ARIMA-style models. To spot seasonality (e.g. spikes at lags 7, 24 for daily data). To check that residuals after fitting are roughly white noise (ACF/PACF of residuals should be near zero).

## How it works

ACF: for each lag k, compute correlation of series with series shifted by k. PACF: for each lag k, compute correlation of series with lag-k after regressing out lags 1..k-1. Plot both with confidence bands (e.g. ±1.96/sqrt(n)). Tools: statsmodels `plot_acf`, `plot_pacf`, or `acf`, `pacf`.

## Inputs

Data: one or more time series (often after differencing if needed). Config: number of lags, whether to difference.

## Outputs

Plots and/or numeric ACF/PACF values per lag. Location: results/, logs/.

## Interpretation

PACF: sharp cutoff after lag p suggests AR(p). ACF: slow decay or cutoff after lag q can suggest MA(q) or AR structure. Regular spikes (e.g. at 7, 24) suggest seasonality; consider seasonal terms (e.g. SARIMA). Use chosen lags in linear models, Markov, or feature lags for ML.

## Related tests

ADF/KPSS/PP (stationarity first); changepoint detection, HMM regime (structure); linear model, Markov chains (use lags).
