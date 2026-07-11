# Phase 5: Significance and uncertainty

**Goal:** Answer “Is this strategy or level **better than random**?” and “How **uncertain** is my result?” using resampling and simulation—**without assuming a normal distribution**.

**Why it matters:** A good backtest can be luck. Permutation tests and bootstrap give you p-values and confidence intervals even when your metric (e.g. Sharpe) isn’t normally distributed. Block bootstrap respects time-series structure; Monte Carlo simulates many paths for risk.

**What you’ll learn:** Bootstrap (resample with replacement → get a distribution of your metric); block bootstrap (for time series); permutation test (shuffle to test “better than random”); statistical significance (the big idea); Monte Carlo (simulate many paths for risk and sizing).

**Tests in this phase:** Bootstrap → block bootstrap → permutation test → statistical significance → walk-forward significance → Monte Carlo.

**Next:** Phase 6 (ML models) when you’re ready for more complex models, or Phase 7 (strategy building blocks) when you want levels and options.
