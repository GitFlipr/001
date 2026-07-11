# Multi-Phase Backtesting Suite — Blueprint

**Version:** 2.0  
**Purpose:** Master document for structure, dependencies, learning paths, and integration of quantitative foundations.

---

## 1. Vision and Goals

This suite trains you to **validate strategies rigorously** before live deployment. By the end you will:

- Understand your data (EDA, distributions, regimes)
- Define metrics consistently (Sharpe, drawdowns, VaR)
- Build and tune baselines (linear → regularized → ML)
- Test significance (bootstrap, permutation)
- Apply strategy building blocks (levels, execution, options)
- Run pre-live checks (pseudo-live, integration, reporting)
- Use advanced tools when needed (portfolio optimization, VaR decomposition, stress testing)

**Target audience:** Self-taught quants, algo traders, and data scientists who know basic backtesting but want a structured path to professional-grade validation.

---

## 2. Phase Structure (9 Phases)

Phases are ordered by **dependency**, not difficulty. Each phase builds on the previous.

| Phase | Name | Core question | Dependency |
|-------|------|---------------|------------|
| **1** | Explore your data | What does my data look like? | None |
| **2** | Time series basics | Is my series stationary? Are there regimes? | Phase 1 |
| **3** | Performance and risk metrics | How do I measure return and risk? | Phase 1 |
| **4** | Baselines, tuning, validation | Can a simple model beat noise? How do I avoid overfitting? | Phases 2, 3 |
| **5** | Significance and uncertainty | Is the edge real or luck? | Phases 3, 4 |
| **6** | Machine learning models | When do I need nonlinearity? | Phases 3, 4 |
| **7** | Strategy building blocks | How do I add levels, execution, options? | Phases 2, 3 |
| **8** | Pre-live and reporting | Am I ready for live? | Phases 1–7 |
| **9** | Advanced and specialty | How do I handle portfolios, VaR decomposition, stress? | Phases 3–8 |

---

## 3. Learning Paths

### 3.1 Core path (minimum viable)

```
1 → 2 → 3 → 4 → 5 → 8
```

Covers EDA, stationarity, metrics, baselines, significance, and pre-live. Enough to validate a single-strategy backtest and decide go/no-go.

### 3.2 Full path (recommended)

```
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 (as needed)
```

Adds ML models, strategy blocks (swings, Fib, VWAP), and optional advanced topics.

### 3.3 Specialized tracks

- **ML-first track:** 1 → 2 → 3 → 4 → 6 → 5 → 8 — if you plan to use ML heavily.
- **Levels-first track:** 1 → 2 → 3 → 7 → 4 → 5 → 8 — if you trade support/resistance and execution.
- **Portfolio & risk track:** 1 → 2 → 3 → (VaR expanded, portfolio optimization) → 5 → 8 — for multi-asset or institutional risk.

---

## 4. Integration: External Foundations

The suite aligns with established quantitative material. Key references:

### 4.1 Classical linear regression (Phase 4 foundation)

- **Source:** [Classical linear regression (letianzj)](https://letianzj.github.io/classical-linear-regression.html)
- **Concepts:** OLS, normal equation \( \hat{\beta} = (X^TX)^{-1}X^Ty \), R², Pearson correlation
- **Where it fits:** `linear_model.md` — use as baseline before Lasso/Ridge; R² feeds into significance tests and model comparison.

### 4.2 Portfolio management and optimization (Phase 9)

- **Source:** [Portfolio management (letianzj)](https://letianzj.github.io/portfolio-management-one.html)
- **Concepts:** Mean-variance optimization, Efficient Frontier, Global Minimum Variance (GMV), Tangency Portfolio (max Sharpe), two-fund theorem
- **Where it fits:** `09_advanced_and_specialty/portfolio_optimization.md` — multi-asset allocation and benchmark construction.

### 4.3 Value at Risk (Phase 3 expansion)

- **Source:** [Value at Risk (letianzj)](https://letianzj.github.io/value-at-risk-one.html)
- **Concepts:** Variance-covariance (delta-normal) VaR, Marginal VaR, Component VaR, portfolio VaR decomposition
- **Where it fits:** `03_performance_and_risk_metrics/var_cvar.md` — extend with parametric (delta-normal), Marginal VaR, Component VaR; use with multi-asset and risk attribution.

### 4.4 Bayesian, MCMC, Kalman regression (Phase 4)

- **Sources:** [Bayesian](https://letianzj.github.io/bayesian-linear-regression.html), [MCMC](https://letianzj.github.io/mcmc-linear-regression.html), [Kalman filter](https://letianzj.github.io/kalman-filter-linear-regression.html)
- **Concepts:** Conjugate prior, recursive posterior updates; Metropolis–Hastings MCMC; Dynamic Linear Model (DLM), state-space, time-varying coefficients
- **Where it fits:** `bayesian_regression.md`, `mcmc_regression.md`, `kalman_filter_regression.md`

### 4.5 Mean reversion and pairs trading (Phase 7)

- **Sources:** [Mean reversion](https://letianzj.github.io/mean-reversion.html), [Cointegration pairs trading](https://letianzj.github.io/cointegration-pairs-trading.html), [Kalman filter pairs trading](https://letianzj.github.io/kalman-filter-pairs-trading.html)
- **Concepts:** OU process, half-life, z-score strategy; CADF, Johansen, Engle–Granger; Bollinger bands on spread; dynamic hedge ratio via Kalman
- **Where it fits:** `mean_reversion.md`, `cointegration_pairs_trading.md`, `kalman_filter_pairs_trading.md`

### 4.6 TensorFlow linear regression and event-driven backtest

- **Sources:** [TensorFlow linear regression](https://letianzj.github.io/tensorflow-linear-regression.html), [Backtest (quanttrader)](https://letianzj.github.io/quanttrading-backtest.html)
- **Concepts:** Gradient descent, TF/Keras; event engine, data feed, order manager, brokerage simulation
- **Where it fits:** `06_machine_learning_models/tensorflow_linear_regression.md`, `08_pre_live_and_reporting/event_driven_backtest.md`

### 4.8 Data, indicators, RL (Phases 1, 7, 9)

- **Sources:** [Exponential moving average](https://letianzj.github.io/exponential-moving-average.html), [Free historical market data (Medium)](https://medium.com/@letian.zj/free-historical-market-data-download-in-python-74e8edd462cf), [Portfolio management two](https://letianzj.github.io/portfolio-management-two.html), [Option pricing with RL (Medium)](https://medium.com/@letian.zj/option-pricing-using-reinforcement-learning-ad2ddca7735b)
- **Concepts:** EMA for regular/irregular ticks; yfinance, FRED, Quandl, IB; risk parity, max diversification; DQN for American option
- **Where it fits:** `01_explore_your_data/historical_data_sources.md`, `07_strategy_building_blocks/exponential_moving_average.md`, `09_advanced_and_specialty/reinforcement_learning_options.md`

### 4.7 Time series models and regime detection (Phase 2)

- **Sources:** [Hidden Markov Chain](https://letianzj.github.io/hidden-markov-chain.html), [ARIMA GARCH](https://letianzj.github.io/arima-garch-model.html), [Gaussian Mixture and Markov Regime Switching](https://letianzj.github.io/gaussian-mixture-markov-regime-switching.html), [RNN/LSTM stock prediction](https://letianzj.github.io/rnn-stock-prediction.html)
- **Concepts:** HMM (Viterbi, Baum–Welch); ARIMA, GARCH; GMM vs MRSM; LSTM/GRU for sequences
- **Where it fits:** `hmm_regime.md`, `arima_garch.md`, `gmm_markov_regime_switching.md`; `06_machine_learning_models/lstm.md`

---

## 5. Phase Details (Condensed)

### Phase 1 — Explore your data  
Historical data sources → data quality → summary stats → histograms/KDE → joint plots → distribution fitting.  
**Output:** Data profile, chosen distribution for later risk/parametric VaR.

### Phase 2 — Time series basics  
ADF, KPSS, PP (stationarity) → variance ratio → ACF/PACF → changepoints, structural breaks → HMM, regime-switching.  
**Output:** Stationarity conclusion, regime labels or break dates for splitting backtests.

### Phase 3 — Performance and risk metrics  
Basic metrics (accuracy, MAE, RMSE, R²) → Sharpe/Sortino/Calmar → Information ratio, Omega, Ulcer index → drawdowns → VaR/CVaR (historical, parametric, marginal, component).  
**Output:** Standard metrics used by all later phases.

### Phase 4 — Baselines, tuning, validation  
Linear model (OLS) → Bayesian, MCMC, Kalman filter regression → logistic → Lasso/Ridge → grid/random/Bayesian search → time-series CV → rolling origin/window backtests.  
Theory: CLT, LLN, Bayes, Bernoulli–Poisson, bias–variance.  
**Output:** Baseline performance, tuned params, honest OOS estimates.

### Phase 5 — Significance and uncertainty  
Bootstrap → block bootstrap → permutation test → statistical significance → walk-forward significance → Monte Carlo.  
**Output:** p-values, confidence intervals, “better than random?” answers.

### Phase 6 — Machine learning models  
TensorFlow/Keras linear regression (bridge to DL) → random forest, gradient boosting, SVM, kNN → feature importance, SHAP → MLP, LSTM, Transformer.  
**Output:** When to use each model; validated ML benchmarks vs Phase 4 baselines.

### Phase 7 — Strategy building blocks  
Exponential moving average → swing detection → Fibonacci retracements/extensions → Gann angles → VWAP/TWAP → Black–Scholes, IV, Greeks → mean reversion, cointegration pairs trading, Kalman filter pairs.  
**Output:** Levels and execution benchmarks for strategy logic.

### Phase 8 — Pre-live and reporting  
Event-driven backtest framework → pseudo-live testing → integration checks → slippage/latency testing → kill switch → paper trading reconciliation → report generation → attribution.  
**Output:** Go/no-go decision, final report, PnL attribution.

### Phase 9 — Advanced and specialty  
Hurst, entropy, copulas, correlation breakdown, factor exposure → order flow, order imbalance, volume profile, spread impact → Kelly, price models, stress testing → portfolio optimization (risk parity, max diversification) → reinforcement learning for option pricing.  
**Output:** Specialized tools for multi-asset, risk decomposition, and tail/stress scenarios.

---

## 6. Dependency Graph (Simplified)

```
Phase 1 (EDA)
    ├── Phase 2 (Time series)
    └── Phase 3 (Metrics)
           ├── Phase 4 (Baselines)
           │      ├── Phase 5 (Significance)
           │      └── Phase 6 (ML)
           ├── Phase 7 (Strategy blocks)
           └── Phase 8 (Pre-live)
                  └── Phase 9 (Advanced)
```

Phase 8 can start once you have usable results from Phases 1–7. Phase 9 is optional and can be cherry-picked by topic.

---

## 7. Concepts Reference (Expanded)

| Concept | Phase | Where used | External ref |
|---------|-------|------------|--------------|
| OLS / normal equation | 4 | linear_model, Lasso/Ridge | [Classical linear regression](https://letianzj.github.io/classical-linear-regression.html) |
| Bayesian regression | 4 | bayesian_regression | [Bayesian linear regression](https://letianzj.github.io/bayesian-linear-regression.html) |
| MCMC (Metropolis–Hastings) | 4 | mcmc_regression | [MCMC linear regression](https://letianzj.github.io/mcmc-linear-regression.html) |
| Kalman filter / DLM | 4, 7 | kalman_filter_regression, kalman_filter_pairs_trading | [Kalman filter regression](https://letianzj.github.io/kalman-filter-linear-regression.html), [Kalman pairs](https://letianzj.github.io/kalman-filter-pairs-trading.html) |
| VaR (historical, parametric, delta-normal) | 3 | var_cvar, report_generation | [Value at Risk](https://letianzj.github.io/value-at-risk-one.html) |
| Marginal VaR, Component VaR | 3 | var_cvar, attribution | [Value at Risk](https://letianzj.github.io/value-at-risk-one.html) |
| Efficient Frontier, GMV, Tangency | 9 | portfolio_optimization | [Portfolio management](https://letianzj.github.io/portfolio-management-one.html) |
| Mean reversion, OU, half-life | 2, 7 | mean_reversion, adf_test, hurst_exponent | [Mean reversion](https://letianzj.github.io/mean-reversion.html) |
| Cointegration, pairs trading | 7 | cointegration_pairs_trading | [Cointegration pairs](https://letianzj.github.io/cointegration-pairs-trading.html) |
| Event-driven backtest | 8 | event_driven_backtest | [quanttrading backtest](https://letianzj.github.io/quanttrading-backtest.html) |
| Grid search, AIC/BIC | 4 | grid_search, distribution_fitting | Concepts_reference.md |
| In-sample / out-of-sample | 4, 5 | time_series_cv, rolling_* | Concepts_reference.md |
| Permutation test | 5 | permutation_test, statistical_significance | Concepts_reference.md |
| ARIMA, GARCH | 2 | arima_garch | [ARIMA GARCH](https://letianzj.github.io/arima-garch-model.html) |
| HMM (Viterbi, Baum–Welch) | 2 | hmm_regime | [Hidden Markov Chain](https://letianzj.github.io/hidden-markov-chain.html) |
| GMM, MRSM | 2 | gmm_markov_regime_switching | [GMM and Markov regime switching](https://letianzj.github.io/gaussian-mixture-markov-regime-switching.html) |
| RNN/LSTM stock prediction | 6 | lstm | [RNN stock prediction](https://letianzj.github.io/rnn-stock-prediction.html) |
| Risk parity, max diversification | 9 | portfolio_optimization | [Portfolio management two](https://letianzj.github.io/portfolio-management-two.html) |
| EMA (regular/irregular ticks) | 7 | exponential_moving_average | [Exponential moving average](https://letianzj.github.io/exponential-moving-average.html) |
| Historical data (yfinance, FRED, etc.) | 1 | historical_data_sources | [Free historical market data (Medium)](https://medium.com/@letian.zj/free-historical-market-data-download-in-python-74e8edd462cf) |
| RL for option pricing (DQN) | 9 | reinforcement_learning_options | [Option pricing with RL (Medium)](https://medium.com/@letian.zj/option-pricing-using-reinforcement-learning-ad2ddca7735b) |

---

## 8. Test Count Summary

| Phase | Test count (approx) | Key specs |
|-------|---------------------|-----------|
| 1 | ~6 | historical_data_sources, data_quality_checks, distribution_fitting |
| 2 | ~11 | ADF, KPSS, ARIMA/GARCH, HMM regime, GMM/MRSM, changepoint |
| 3 | ~9 | Sharpe, drawdowns, VaR/CVaR |
| 4 | ~18 | linear_model, Bayesian/MCMC/Kalman regression, Lasso/Ridge, grid_search |
| 5 | ~6 | bootstrap, permutation_test, Monte Carlo |
| 6 | ~10 | tensorflow_linear_regression, random_forest, LSTM, feature_importance |
| 7 | ~14 | EMA, swing, Fibonacci, VWAP, Black–Scholes, mean_reversion, cointegration, Kalman pairs |
| 8 | ~8 | event_driven_backtest, pseudo_live_testing, report_generation |
| 9 | ~16 | Hurst, copulas, Kelly, stress_testing, portfolio_optimization, RL options |

**Total:** ~97 individual test specs plus Concepts_reference.md.

---

## 9. How to Use This Blueprint

1. **Start** — Read the main [README](README.md) and pick a learning path (3.1–3.3).
2. **Work through phases** — Each phase folder has a README; open individual .md files for specific tests.
3. **Concepts** — Use [Concepts_reference.md](Concepts_reference.md) for definitions and where concepts are used.
4. **External material** — Use the links in Section 4 and Section 7 for deeper math and code.
5. **Track progress** — Run tests, log outputs to results/ and logs/, and reference specs when building pipelines.
