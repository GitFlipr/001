# Phase 4: Baselines, tuning, and validation

**Goal:** Build **simple models** (linear, logistic, regularized) as a benchmark, and learn **how to tune parameters** and **validate in time** so you don’t overfit.

**Why it matters:** If a fancy model can’t beat a linear regression, the extra complexity isn’t worth it. Grid/random search find good parameters; time-series CV and rolling validation give you honest out-of-sample numbers. The small amount of theory (CLT, Bayes, bias–variance) explains *why* we care about train vs validation.

**What you’ll learn:** Linear and logistic regression, Lasso/Ridge (regularization); grid search and random search; time-series cross-validation and rolling-origin/window backtests. Light theory: central limit theorem, law of large numbers, Bayes, Bernoulli/Poisson, bias–variance.

**Tests in this phase:**
- *Models:* Linear model, logistic regression, Lasso/Ridge; Bayesian regression, MCMC regression, Kalman filter regression.
- *Theory:* CLT, LLN, Bayes, Bernoulli–Poisson, bias–variance.
- *Tuning & validation:* Grid search, random search, Bayesian optimization → time_series_cv, rolling_origin_validation, rolling_window_backtests.

**Next:** Phase 5 (significance and uncertainty)—use these baselines and metrics to ask: “Is the edge real, or could it be luck?”
