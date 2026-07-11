# Concepts reference: grid search, AIC/BIC, in- and out-of-sample, lambda, OLS, VaR, portfolio optimization

Short definitions and where each concept is **used** or **not yet used** in the Individual tests.

---

## Grid search

**What it is:** Exhaustive search over a **predefined set of parameter combinations**. You define a grid (e.g. window = [5, 10, 20], threshold = [0.01, 0.02]). For each combination you train/evaluate and compute a metric (e.g. Sharpe, accuracy). The best combination is chosen by that metric.

**Where it’s used:**  
- **[grid_search.md](grid_search.md)** — dedicated test.  
- **Lasso/Ridge** — grid search (or random search) is the standard way to tune the regularization strength (alpha).  
- **Rolling window backtests** — best params from grid search are often used as inputs.

**Related:** [04_baselines_tuning_validation/bayesian_optimization.md](04_baselines_tuning_validation/bayesian_optimization.md) — Bayesian optimization is a sample-efficient alternative when each evaluation is expensive (e.g. full rolling backtest).

**Not yet used:** Grid search is not yet implemented as a shared “tune any module’s params” step in the pipeline; it’s referenced as the way to tune alpha in Lasso/Ridge and params for strategies.

---

## AIC and BIC

**What they are:**  
- **AIC (Akaike Information Criterion)** = -2×log-likelihood + 2×k (k = number of parameters). Lower is better. Penalizes complexity.  
- **BIC (Bayesian Information Criterion)** = -2×log-likelihood + log(n)×k (n = sample size). Lower is better. Penalizes complexity more than AIC when n is large.

They trade off **fit** (log-likelihood) and **model complexity** (number of parameters). Used to compare models or distributions when you want a single “best” choice.

**Where they’re used:**  
- **[distribution_fitting.md](distribution_fitting.md)** — compare candidate distributions (e.g. normal vs t vs skewed-t) using AIC/BIC; pick the one with lowest AIC or BIC.

**Not yet used:**  
- AIC/BIC are **not** yet used in the Individual docs for **model selection** of regression or ML models (e.g. linear vs Lasso vs random forest). Distribution fitting is the only place they’re explicitly referenced.  
- Could be used later for: choosing number of lags in AR models, number of states in HMM, or comparing regression models.

---

## In-sample and out-of-sample

**What they mean:**  
- **In-sample:** Data used to **fit** the model (train set). Performance on in-sample data is **training** performance and can be overfit.  
- **Out-of-sample (OOS):** Data **not** used for fitting (validation or test set). Performance on OOS data is a better measure of how the model will do on new data.

**Where they’re used:**  
- **[time_series_cv.md](time_series_cv.md)** — train on past, validate on future; validation is out-of-sample.  
- **[rolling_window_backtests.md](rolling_window_backtests.md)**, **[rolling_origin_validation.md](rolling_origin_validation.md)**, **[pseudo_live_testing.md](pseudo_live_testing.md)** — backtests and pseudo-live are evaluated out-of-sample (data the strategy wasn’t trained on in that window).  
- **Train/val split** in linear_model, random_forest, SVM, kNN, LSTM, etc. — val is out-of-sample.  
- **Bias–variance** — in-sample vs out-of-sample error is what you decompose.

**Not yet used:**  
- The phrases “in-sample” and “out-of-sample” are not used in every relevant Individual doc; the idea is there (train/val, backtest on unseen period), but a single shared “in-sample vs out-of-sample” report or glossary entry was not there before this concepts doc.

---

## What is lambda (λ)?

**Lambda** is used in different ways; the meaning depends on context.

### 1. Regularization strength (Ridge / Lasso)

In math, the penalty is often written as **λ × penalty**:  
- Ridge: minimize MSE + **λ** × (sum of squared coefficients).  
- Lasso: minimize MSE + **λ** × (sum of absolute coefficients).

**In code (e.g. sklearn):** the same thing is usually called **`alpha`**, not `lambda` (because `lambda` is a reserved word in Python). So: **lambda (math) = alpha (sklearn)**. Larger λ (or alpha) = stronger regularization = smaller or sparser coefficients.

**Where it’s used:**  
- **[lasso_ridge_regression.md](lasso_ridge_regression.md)** — “alpha” is the regularization strength; that’s lambda. Tuning alpha (e.g. via grid search) is tuning lambda.

**Not yet used:**  
- The Individual doc doesn’t use the symbol “λ” or the word “lambda”; it uses “alpha”. So “lambda” is **related but not used by name** in the docs.

### 2. Poisson rate (count data)

In **Poisson** distribution, **λ (lambda)** is the **rate** (average number of events per period). Mean = variance = λ.

**Where it’s used:**  
- **[bernoulli_poisson.md](bernoulli_poisson.md)** — when fitting a Poisson model, you estimate λ from data. The doc doesn’t explicitly say “lambda” but the fitted parameter is the rate (λ).

**Not yet used:**  
- The symbol “λ” or the name “lambda” is not used in the Poisson doc; “rate” is used. So again, **related but not used by name**.

### Summary for lambda

| Context        | Meaning              | In Individual docs      |
|----------------|----------------------|-------------------------|
| Ridge/Lasso    | Regularization strength | Called **alpha**; λ not used by name. |
| Poisson        | Rate (mean = variance)   | Fitted parameter; λ not used by name. |

---

## Related and not yet used (summary)

| Concept            | Used in Individual tests? | Not yet used / only partly used? |
|--------------------|----------------------------|-----------------------------------|
| **Grid search**    | Yes (grid_search; tuning alpha in Lasso/Ridge) | Not as a generic “tune any module” pipeline step. |
| **AIC/BIC**        | Yes (distribution_fitting) | Not for regression/ML model selection in other docs. |
| **In-sample / out-of-sample** | Yes (train/val, backtests, time_series_cv) | Not spelled out in every doc; this concepts doc clarifies. |
| **Lambda (λ)**     | Same idea, different name  | **Lambda** as a word/symbol not used: Ridge/Lasso use **alpha**; Poisson uses **rate**. |

So: **grid search**, **AIC/BIC**, and **in/out-of-sample** are all related and used in at least one place; **lambda** is related but appears in the docs only as “alpha” or “rate”, not as “lambda”.

---

## Permutation test

**What it is:** Non-parametric test that builds a null distribution by **shuffling** (e.g. returns, labels, or strategy assignment) many times. Compare the observed metric to the null; p-value = proportion of null outcomes as or more extreme. No distributional assumption.

**Where it’s used:**  
- **[permutation_test.md](permutation_test.md)** — dedicated test.  
- **[statistical_significance.md](statistical_significance.md)** — “Custom or permutation test” as a way to validate levels/strategies vs random.  
- **[bootstrap.md](bootstrap.md)**, **[block_bootstrap.md](block_bootstrap.md)** — listed as related (other resampling).

**Not yet used:** Permutation is not yet spelled out as the default “strategy vs random” test in every doc that needs significance; the new Individual doc makes it a first-class option alongside bootstrap.

---

## OLS and normal equation (classical linear regression)

**What it is:** Ordinary Least Squares (OLS) estimates β in y = Xβ + ε by minimizing squared residuals. The closed-form solution (normal equation) is \(\hat{\beta} = (X^TX)^{-1}X^Ty\). R² = fraction of variance explained. In simple linear regression, √R² = Pearson correlation between x and y.

**Where it's used:**  
- **[linear_model.md](04_baselines_tuning_validation/linear_model.md)** — baseline regression; sklearn LinearRegression, statsmodels OLS.  
- **Lasso/Ridge** — OLS plus regularization; alpha/lambda tunes penalty.

**External reference:** [Classical linear regression (letianzj)](https://letianzj.github.io/classical-linear-regression.html).

---

## VaR methods (historical, parametric, Monte Carlo)

**What they are:**  
- **Historical VaR** — percentile of empirical return distribution (e.g. 1st percentile).  
- **Parametric (delta-normal) VaR** — VaR = z × σ × V, assuming normal returns; for portfolios σ_p² = w^T Σ w.  
- **Monte Carlo VaR** — simulate many paths from fitted model; VaR = percentile of simulated losses.  
**Marginal VaR** = ∂VaR_p/∂V_i; **Component VaR** = MVaR_i × V_i, summing to VaR_p.

**Where it's used:**  
- **[var_cvar.md](03_performance_and_risk_metrics/var_cvar.md)** — all methods; Marginal and Component VaR for portfolios.  
- **report_generation**, **attribution** — risk reporting.

**External reference:** [Value at Risk (letianzj)](https://letianzj.github.io/value-at-risk-one.html).

---

## Portfolio optimization (MPT, efficient frontier, GMV, tangency)

**What it is:** Mean-variance optimization: maximize return for given risk (or minimize risk for given return). **GMV** = minimum-variance portfolio; **Tangency** = max-Sharpe portfolio; **Efficient frontier** = set of optimal risk–return combinations. Two-fund theorem: frontier = linear combo of GMV and max-return portfolios.

**Where it's used:**  
- **[portfolio_optimization.md](09_advanced_and_specialty/portfolio_optimization.md)** — dedicated test.

**External reference:** [Portfolio management (letianzj)](https://letianzj.github.io/portfolio-management-one.html).

---

## Bayesian regression, MCMC, Kalman filter

**Bayesian regression:** Prior on β, likelihood, posterior via Bayes' theorem. Conjugate prior (normal-inverse-gamma) gives closed-form posterior. Recursive updates for online learning. **MCMC regression:** When conjugate unavailable, Metropolis–Hastings samples from posterior. **Kalman filter regression:** Dynamic Linear Model—β evolves (e.g. random walk); recursive state update. Used for time-varying hedge ratios, pairs trading.

**Where used:** bayesian_regression.md, mcmc_regression.md, kalman_filter_regression.md; kalman_filter_pairs_trading.md.

**External references:** [Bayesian](https://letianzj.github.io/bayesian-linear-regression.html), [MCMC](https://letianzj.github.io/mcmc-linear-regression.html), [Kalman filter](https://letianzj.github.io/kalman-filter-linear-regression.html).

---

## Mean reversion, cointegration, pairs trading

**Mean reversion:** Price reverts to mean (Ornstein–Uhlenbeck). Half-life = ln(2)/θ. Z-score strategy: trade size ∝ −z. **Cointegration:** Linear combo of non-stationary series is stationary. Pairs trading: trade spread when it deviates (Bollinger bands). Tests: ADF on residuals (CADF), Johansen. **Kalman pairs:** Dynamic hedge ratio via Kalman filter.

**Where used:** mean_reversion.md, cointegration_pairs_trading.md, kalman_filter_pairs_trading.md.

**External references:** [Mean reversion](https://letianzj.github.io/mean-reversion.html), [Cointegration pairs](https://letianzj.github.io/cointegration-pairs-trading.html), [Kalman pairs](https://letianzj.github.io/kalman-filter-pairs-trading.html).

---

## Event-driven backtest

**What it is:** Backtest architecture where events (bar, tick, order, fill) are dispatched by an event engine to handlers. Strategy reacts to data; order manager and brokerage simulate execution. Same structure can extend to live trading.

**Where used:** event_driven_backtest.md.

**External reference:** [quanttrading backtest](https://letianzj.github.io/quanttrading-backtest.html).

---

## ARIMA and GARCH

**What they are:** **ARIMA** models returns (or levels) with AR(p), integration I(d), MA(q). **GARCH** models conditional variance (volatility clustering): σ²_t = ω + Σ βᵢσ²_{t-i} + Σ αⱼε²_{t-j}. Combined ARIMA-GARCH: mean and variance both modeled.

**Where used:** arima_garch.md.

**External reference:** [ARIMA GARCH (letianzj)](https://letianzj.github.io/arima-garch-model.html).

---

## Risk parity and maximum diversification

**What they are:** **Risk parity** — equal risk contribution per asset; MRC_i = (Σw)_i/σ_p; solve for w s.t. RC_i equal. **Maximum diversification** — maximize w^T σ / √(w^T Σ w). Both avoid return estimates; use covariance structure. Compare in monthly rebalance backtest (GMV, max Sharpe, risk parity, max diversified, equal weights).

**Where used:** portfolio_optimization.md.

**External reference:** [Portfolio management two (letianzj)](https://letianzj.github.io/portfolio-management-two.html).

---

## Reinforcement learning for option pricing

**What it is:** American option = MDP; state (price, time); action (exercise/hold). DQN learns optimal policy; price = expected discounted payoff. Baseline: QuantLib (Baw, binomial).

**Where used:** reinforcement_learning_options.md.

**External reference:** [Option pricing with RL (letianzj, Medium)](https://medium.com/@letian.zj/option-pricing-using-reinforcement-learning-ad2ddca7735b). Code: [american_option.ipynb](https://github.com/letianzj/QuantResearch/blob/master/ml/american_option.ipynb), [reinforcement_trader.ipynb](https://github.com/letianzj/QuantResearch/blob/master/ml/reinforcement_trader.ipynb).

---

## GMM and Markov Regime Switching (MRSM)

**What they are:** **GMM** — mixture of Gaussians; no temporal structure. **MRSM** — Markov chain governs regime; returns conditionally normal within regime. Both use EM. MRSM captures persistence (regimes persist); GMM ignores sequence.

**Where used:** gmm_markov_regime_switching.md.

**External reference:** [Gaussian Mixture and Markov Regime Switching (letianzj)](https://letianzj.github.io/gaussian-mixture-markov-regime-switching.html).
