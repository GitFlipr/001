# Changepoint detection (structural breaks)

## What it is

Changepoint detection finds times when the **distribution or parameters** of the series change (e.g. mean, variance, trend). Those times are **structural breaks**. The output is a set of changepoint indices or dates.

## When to use it

To split backtests or training at break dates instead of fitting one model across the whole sample. To inform regime labeling (e.g. with HMM) or rolling windows. To align breaks with known events (e.g. policy changes) for sanity checks.

## How it works

Methods vary: e.g. binary segmentation, PELT, or Bayesian changepoint models. Many minimize a cost (e.g. negative log-likelihood) over segmentations and optionally penalize the number of changepoints. Tools: e.g. `ruptures`, or custom cost + search.

## Inputs

Data: one or more time series. Config: method (e.g. PELT, binary segmentation), penalty or number of changepoints.

## Outputs

Changepoint indices or dates per series; optionally plots. Location: results/, logs/.

## Interpretation

Use changepoints to split backtests or training; use rolling windows that respect breaks. Feed dates into HMM or regime dummies. If breaks don't align with known events, review method or hyperparameters.

## Related tests

HMM regime (smooth state sequence vs discrete breaks); rolling window backtests, rolling origin validation (windows can start/end at changepoints); ADF/KPSS (stationarity can change at breaks).
