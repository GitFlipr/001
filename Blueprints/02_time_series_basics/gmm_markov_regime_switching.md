# Gaussian Mixture and Markov Regime Switching Model (MRSM)

## What it is

**Gaussian Mixture Model (GMM):** Unsupervised clustering assuming data comes from K Gaussians. Use AIC/BIC to choose number of components. **Markov Regime Switching Model (MRSM):** Same idea but with **temporal structure**—regimes follow a Markov chain. Returns are conditionally normal within each regime; regime persists with transition probabilities.

## When to use it

For regime detection when you expect distinct states (e.g. low vol vs high vol, bull vs bear). GMM ignores time order; MRSM respects it and gives smoother regime sequences. Compare with HMM (similar; MRSM uses statsmodels MarkovRegression).

## How it works

**GMM:** EM algorithm; fit K Gaussians; assign each point to component. **MRSM:** Fit MarkovRegression with k_regimes; switching_variance=True for vol regimes. Output: regime probabilities, state means/variances, transition matrix. Tools: sklearn GaussianMixture; statsmodels MarkovRegression.

## Inputs

Return series. Config: number of regimes (e.g. 2 for low/high vol, 3 for up/down/sideways).

## Outputs

Regime probabilities per timestamp; state parameters; transition matrix. Location: results/, logs/.

## Interpretation

High-vol regime: reduce size, hedge, or switch strategy. Use regime as filter for mean-reversion (disable in trend) or momentum (boost in trend). Compare regime labels with VIX or drawdowns.

## Related tests

[hmm_regime](hmm_regime.md) (similar latent-state idea); [regime_switching](regime_switching.md); changepoint_detection; distribution_fitting (AIC/BIC for component count).

## External reference

[Gaussian Mixture and Markov Regime Switching (letianzj)](https://letianzj.github.io/gaussian-mixture-markov-regime-switching.html).
