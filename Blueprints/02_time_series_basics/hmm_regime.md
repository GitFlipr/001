# HMM regime detection (Hidden Markov Model)

## What it is

A **Hidden Markov Model (HMM)** assigns each time point to a **latent state** (e.g. high/low volatility, trend/mean-reversion) and estimates **transition probabilities** between states. You get a regime label per observation and a transition matrix.

## When to use it

To get a probabilistic regime label per timestamp for regime-dependent strategies or position sizing. To compare with changepoint detection: HMM gives smooth state sequences; changepoints give break dates. To support regime-aware backtests and live routing (e.g. different rules per regime).

## How it works

Assume a fixed number of states (e.g. 2 or 3). Each state has an emission distribution (e.g. Gaussian on returns). Fit the HMM (e.g. Baum–Welch / EM) to get transition matrix and state parameters; then infer the most likely state sequence (Viterbi) or state probabilities per time. Tools: e.g. `hmmlearn` GaussianHMM.

## Inputs

Data: time series (e.g. returns, optionally volatility). Config: number of states, optional constraints.

## Outputs

Regime index (or probabilities) per timestamp; transition matrix; state means/variances; optionally plots. Location: results/, logs/.

## Interpretation

Use regime labels as features or filters (e.g. train only in "high vol" regime). Use for position sizing (e.g. reduce size in high-vol regime). Validate regime switches against changepoint detection and known events.

## Related tests

Changepoint detection (discrete breaks vs smooth regimes); rolling window backtests (by regime); linear model, random forest (regime as feature or filter); gmm_markov_regime_switching.

## External reference

[Hidden Markov Chain and stock market regimes (letianzj)](https://letianzj.github.io/hidden-markov-chain.html) — evaluation (forward/backward), decoding (Viterbi), learning (Baum–Welch).
