# Distribution fitting

## What it is

**Distribution fitting** chooses a parametric probability distribution (e.g. normal, Student’s t, skewed-t) and estimates its parameters from your data so that the fitted distribution best matches the empirical distribution. You can compare several candidate distributions using fit quality (e.g. log-likelihood, AIC, BIC) and optionally plot fitted vs empirical CDF/PDF.

## When to use it

- **After histograms/KDE:** You have a sense of shape; now formalize it with a parametric form.
- **For option pricing, VaR, or simulation:** Many methods assume a distribution (e.g. normal or t for returns); fitting justifies or challenges that assumption.
- **To compare assumptions:** e.g. normal vs t vs skewed-t; pick the best fit for downstream use.
- **For reporting:** Document “returns modeled as X with parameters Y” for reproducibility and robustness checks.

## How it works

1. **Choose candidates:** e.g. normal, t, skewed-t, or others (exponential, etc. for non-returns).
2. **Estimate parameters:** e.g. maximum likelihood (MLE) for each candidate (mean, std, degrees of freedom, skew, etc.).
3. **Compare fit:** Log-likelihood (higher = better), AIC or BIC (lower = better, penalize complexity).
4. **Optional:** Plot fitted CDF/PDF over the empirical histogram or KDE.

Tools: `scipy.stats` (e.g. `norm`, `t`, `skewnorm`), or specialized packages for skewed-t.

## Inputs

- **Data:** One or more series (e.g. returns, price changes) to fit.
- **Config:** Candidate distributions, target series, optional constraints or initial values.

## Outputs

- **Parameters:** Per-series (or per-symbol) best-fit distribution and its parameters (e.g. mean, std, df, skew).
- **Fit metrics:** Log-likelihood, AIC, BIC (and optionally per-candidate).
- **Optional:** Plots of fitted vs empirical CDF/PDF.
- **Location:** Typically `results/` (JSON or tables) and optionally plots; logs in `logs/`.

## How to run / implement

- **From a pipeline:** Run the distribution-fitting module with config for data path, candidates, and output path.
- **Implement:** For each series, fit each candidate with MLE, compute AIC/BIC, choose best; write parameters and metrics; optionally plot.

## Interpretation

- **One distribution clearly best (e.g. t over normal)** — use that for VaR, option pricing, or simulation; document it.
- **No good fit** — prefer non-parametric or robust methods (e.g. bootstrap, historical VaR, permutation tests).
- **Heavy tails (t or skewed-t better)** — use tail-aware risk metrics and avoid assuming normality in stress scenarios.

## Related tests

- **Summary stats / histograms / KDE** — inform which distributions to try and whether the fit looks plausible.
- **Bootstrap / block bootstrap** — often used when you don’t want to assume a parametric form.
- **VaR/CVaR** — parametric VaR uses the fitted distribution; if fit is poor, use historical VaR instead.
