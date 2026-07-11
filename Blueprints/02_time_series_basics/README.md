# Phase 2: Time series basics

**Goal:** Check whether your series is **stationary** (stable mean/variance over time) and whether it has **structure** (regimes, breaks). Many models assume stationarity; if your data drifts or switches behaviour, you need to know.

**Why it matters:** Backtests and ML often assume “today is like the past.” Unit-root tests (ADF, KPSS, Phillips–Perron) tell you if you should use levels or differences (e.g. returns). ACF/PACF show lag structure. Changepoint and regime tools (Markov, HMM) find when the “rules” change—so you can split backtests or use rolling windows.

**What you’ll learn:** What “stationary” means in plain language; how to test for it; how to spot structural breaks and regimes so you don’t overfit one period.

**Tests in this phase:** ADF, KPSS, Phillips–Perron (unit roots) → variance ratio (random walk) → ACF/PACF (autocorrelation) → ARIMA and GARCH → changepoint detection, structural break tests (Chow, Zivot–Andrews) → Markov chains, HMM regime, regime-switching, GMM and Markov regime switching.

**Next:** Phase 3 (performance and risk metrics)—once you know your data is (or isn’t) well-behaved, you define how you’ll measure strategy performance and risk.
