# Bernoulli and Poisson modeling

## What it is

**Bernoulli** models binary outcomes (0/1); **Poisson** models counts (e.g. number of trades per day, events). Fit parameters and optionally goodness-of-fit; use for scenario generation or risk.

## When to use it

To model trade frequency, win rate, or other count/binary metrics. As a parametric alternative to raw empirical stats; can feed into VaR or scenario generation. Validate assumptions before using in sizing.

## How it works

Fit Bernoulli (probability p) or Poisson (rate lambda) via MLE. Optionally goodness-of-fit (e.g. chi-square or visual). Predict or simulate. Tools: scipy.stats, statsmodels.

## Inputs

Data: binary or count series; optionally covariates. Config: target (count or binary).

## Outputs

Fitted parameters, goodness-of-fit; optionally predictions. Location: results/, logs/.

## Interpretation

Good fit: use for scenario generation or expected trade frequency in sizing. Poor fit: use empirical or non-parametric (bootstrap). Document for risk reports.

## Related tests

Distribution fitting; bootstrap; VaR/CVaR; basic_metrics (win rate, counts).
