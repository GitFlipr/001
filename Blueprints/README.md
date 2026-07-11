# Multi-phase backtesting suite (Individual tests)

This folder contains **~97 individual test specs** plus one **concepts reference**, grouped into **9 phases**. Each phase is a subfolder with a short README that explains *what* you’re learning and *why* it comes in that order. You can work through phases in order or jump to the ones you need.

**→ Master blueprint:** [BLUEPRINT.md](BLUEPRINT.md) — structure, dependencies, learning paths, and integration with external quantitative foundations (portfolio optimization, VaR, classical regression).

---

## How to use this (learning path)

If you’re **not a data scientist** and mainly know basic backtesting:

1. **Start with Phase 1** — Explore your data. Get comfortable with summary stats and simple plots before any modeling.
2. **Then Phase 2** — Time series basics. Learn whether your series is “well-behaved” (stationary, regimes) so you know what models are reasonable.
3. **Then Phase 3** — Performance and risk metrics. Define how you’ll measure every strategy (Sharpe, drawdowns, VaR, etc.) so you can compare and report.
4. **Phases 4–5** — Baselines, tuning, validation, then significance. Build simple models, tune them properly, and test whether the edge is real (permutation, bootstrap).
5. **Phase 6** — Optional. Add ML/DL when linear baselines aren’t enough.
6. **Phase 7** — Strategy building blocks (swings, Fibonacci, Gann, options) when your strategy uses levels or options.
7. **Phase 8** — Pre-live: pseudo-live testing, integration checks, reports, attribution.
8. **Phase 9** — Advanced/specialty topics (Hurst, copulas, order flow, Kelly, stress tests). Use when a specific problem needs them.

**Concepts reference:** [Concepts_reference.md](Concepts_reference.md) stays here in the root. It defines grid search, AIC/BIC, in/out-of-sample, lambda, and permutation test and points to which Individual tests use them.

---

## Phase overview

| Phase | Folder | What you learn |
|-------|--------|----------------|
| 1 | [01_explore_your_data](01_explore_your_data/) | Summary stats, histograms/KDE, distribution fitting — understand your data before modeling |
| 2 | [02_time_series_basics](02_time_series_basics/) | Stationarity (ADF, KPSS, PP), ACF/PACF, changepoints, Markov/HMM, regime-switching |
| 3 | [03_performance_and_risk_metrics](03_performance_and_risk_metrics/) | Accuracy, MAE, RMSE, R², Sharpe/Sortino/Calmar, drawdowns, VaR/CVaR |
| 4 | [04_baselines_tuning_validation](04_baselines_tuning_validation/) | Linear/logistic/Lasso/Ridge, light theory (CLT, Bayes, bias–variance), grid/random search, time-series CV, rolling validation |
| 5 | [05_significance_and_uncertainty](05_significance_and_uncertainty/) | Bootstrap, block bootstrap, permutation test, statistical significance, Monte Carlo |
| 6 | [06_machine_learning_models](06_machine_learning_models/) | Random forest, SVM, kNN, neural net, MLP, LSTM, Transformer |
| 7 | [07_strategy_building_blocks](07_strategy_building_blocks/) | Swing detection, Fibonacci, Gann, Black–Scholes (options) |
| 8 | [08_pre_live_and_reporting](08_pre_live_and_reporting/) | Pseudo-live testing, integration checks, report generation, attribution |
| 9 | [09_advanced_and_specialty](09_advanced_and_specialty/) | Hurst, entropy, copulas, correlation breakdown, order flow, volume profile, spread, Kelly, price models, stress testing, portfolio optimization |

---

## Further reading (quantitative foundations)

- [Portfolio management](https://letianzj.github.io/portfolio-management-one.html) — Mean-variance optimization, Efficient Frontier, GMV, Tangency Portfolio
- [Value at Risk](https://letianzj.github.io/value-at-risk-one.html) — Variance-covariance VaR, Marginal VaR, Component VaR
- [Classical linear regression](https://letianzj.github.io/classical-linear-regression.html) — OLS, normal equation, R² (Phase 4 baseline)
- [Bayesian linear regression](https://letianzj.github.io/bayesian-linear-regression.html) — Conjugate prior, recursive updates
- [MCMC linear regression](https://letianzj.github.io/mcmc-linear-regression.html) — Metropolis–Hastings, non-conjugate posteriors
- [Kalman filter linear regression](https://letianzj.github.io/kalman-filter-linear-regression.html) — Dynamic Linear Model, time-varying coefficients
- [TensorFlow linear regression](https://letianzj.github.io/tensorflow-linear-regression.html) — Gradient descent, bridge to DL (Phase 6)
- [Mean reversion](https://letianzj.github.io/mean-reversion.html) — OU process, ADF, Hurst, half-life, z-score strategy
- [Cointegration pairs trading](https://letianzj.github.io/cointegration-pairs-trading.html) — CADF, Johansen, Engle–Granger
- [Kalman filter pairs trading](https://letianzj.github.io/kalman-filter-pairs-trading.html) — Dynamic hedge ratio, EWA-EWC
- [Backtest (quanttrader)](https://letianzj.github.io/quanttrading-backtest.html) — Event-driven backtest framework
- [Hidden Markov Chain](https://letianzj.github.io/hidden-markov-chain.html) — HMM for regime detection (Phase 2)
- [RNN/LSTM stock prediction](https://letianzj.github.io/rnn-stock-prediction.html) — LSTM/GRU for price forecasting (Phase 6)
- [ARIMA GARCH](https://letianzj.github.io/arima-garch-model.html) — Return and volatility modeling (Phase 2)
- [Gaussian Mixture and Markov Regime Switching](https://letianzj.github.io/gaussian-mixture-markov-regime-switching.html) — GMM and MRSM (Phase 2)
- [Portfolio management two](https://letianzj.github.io/portfolio-management-two.html) — Risk parity, max diversification, monthly rebalance backtest
- [Exponential moving average](https://letianzj.github.io/exponential-moving-average.html) — EMA/EWMA for regular and irregular tick intervals (Phase 7)
- [Free historical market data (Medium)](https://medium.com/@letian.zj/free-historical-market-data-download-in-python-74e8edd462cf) — yfinance, FRED, Quandl, IB (Phase 1)
- [Option pricing with RL (Medium)](https://medium.com/@letian.zj/option-pricing-using-reinforcement-learning-ad2ddca7735b) — DQN for American option (Phase 9)
- [QuantResearch: reinforcement_trader.ipynb](https://github.com/letianzj/QuantResearch/blob/master/ml/reinforcement_trader.ipynb) — RL trading notebook

---

## Note on “Related tests” links

Inside each test doc, “Related tests” often link to other docs by filename (e.g. `bootstrap.md`). Those links work **within the same phase folder**. Links to tests in *other* phases would need a path like `../04_baselines_tuning_validation/grid_search.md` if you want them to work from a static site or file viewer; for now you can open the right phase folder and find the doc by name.
