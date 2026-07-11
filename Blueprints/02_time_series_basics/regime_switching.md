# Regime-switching (Markov-switching)

## What it is

Model where parameters (e.g. mean, vol) switch between a small number of regimes according to a Markov chain. Captures bull/bear, high/low vol, or trend/mean-reversion regimes.

## When to use it

When one set of parameters does not fit the full sample; for regime-dependent signals or position sizing; to test if strategy works in each regime.

## How it works

Fit Markov-switching model (e.g. 2 or 3 states). Estimate transition probabilities and state-dependent parameters. Filter or smooth to get regime probabilities. Libraries: statsmodels (MarkovRegression), custom EM or Bayesian.

## Inputs

Returns or price series. Config: number of regimes, model (mean, vol, or both).

## Outputs

Regime probabilities; fitted parameters per regime; transition matrix. Location: results/, logs/.

## Interpretation

High prob in high-vol regime: reduce size or use different rules. Use with HMM regime (similar idea) and stress testing.

## Related tests

hmm_regime; gmm_markov_regime_switching; changepoint detection; stress testing and scenarios; Hurst exponent; correlation breakdown.
