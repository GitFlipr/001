# Histograms and KDE (kernel density estimation)

## What it is

A **histogram** bins your data and shows how many observations fall in each bin (a step-wise approximation of the distribution). **Kernel density estimation (KDE)** smooths this into a continuous curve that estimates the probability density of the variable. Together they show the shape of the distribution of a single series (e.g. returns, volume).

## When to use it

- **After summary stats:** To see *how* the data is distributed (symmetric, skewed, heavy-tailed, multi-modal).
- **To decide on modeling assumptions:** If the distribution looks normal, normal-based tests may apply; if heavy-tailed or skewed, use robust or non-parametric methods.
- **To compare across symbols or periods:** Plot histograms/KDE for different assets or windows side by side.
- **Before distribution fitting:** Histograms and KDE suggest which parametric distributions to try (e.g. normal, t, skewed-t).

## How it works

- **Histogram:** Choose bin edges (e.g. equal width or equal count). Count observations per bin; plot as bars. Height can be count or density (so area = 1).
- **KDE:** Place a kernel (e.g. Gaussian) at each data point; sum (and scale) to get a smooth density curve. Bandwidth controls smoothness: larger = smoother, smaller = more wiggly.

Common tools: matplotlib `hist`, seaborn `histplot`, seaborn `kdeplot`, or `scipy.stats.gaussian_kde`.

## Inputs

- **Data:** One or more series (e.g. returns, volume, close) from OHLCV or derived data.
- **Config:** Which series to plot, number of bins or KDE bandwidth, per-symbol or combined.

## Outputs

- **Plots:** PNG/PDF (and optionally displayed). One plot per series or per symbol, with optional KDE overlay on the histogram.
- **Optional:** Paths or summaries in JSON/logs.
- **Location:** Typically `results/` (and logs in `logs/`).

## How to run / implement

- **From a pipeline:** Run the module that produces histograms and KDE (e.g. `histograms_kde`), with config for data path, series, and output path.
- **Implement:** Load series, call `sns.histplot(..., kde=True)` or separate `hist` + `kdeplot`, save figure to results folder.

## Interpretation

- **Roughly bell-shaped** — normal-based methods may be reasonable; check kurtosis for tail heaviness.
- **Skewed** — use robust methods or skewed distributions; consider tail risk in risk metrics.
- **Heavy tails** — more extremes than normal; use robust stats, bootstrap, or tail-focused risk (VaR/CVaR).
- **Multi-modal** — may indicate regimes or mixtures; consider regime detection or mixture models.

## Related tests

- **Summary stats** — numeric summary of the same series; skew and kurtosis should match the visual shape.
- **KDE with hue** — same idea but split by category (e.g. regime, symbol).
- **Distribution fitting** — fit parametric distributions to the same series; compare fitted density to the histogram/KDE.
