# Permutation test

## What it is

A **non-parametric** hypothesis test that builds a **null distribution** by **shuffling** labels, signals, or time order many times. You compute your metric (e.g. Sharpe, hit rate, difference between two strategies) on the real data, then on each shuffled version. The **p-value** is the proportion of null outcomes as or more extreme than the observed one. No assumption about the distribution of the metric.

## When to use it

To test whether a strategy or signal is **better than random** (e.g. "does this level beat random entries?"). To compare two strategies on the same data (e.g. strategy A vs B by Sharpe). To validate that a rule or level has predictive power before going live. When you want a distribution-free alternative to parametric tests.

## How it works

1. Define the **metric** (e.g. Sharpe of strategy returns, hit rate, or difference in Sharpe between two strategies).
2. Compute the **observed** metric on the real data.
3. For each of **N permutations**: shuffle the thing that should be random under the null (e.g. return series, signal labels, or which strategy gets which period); recompute the metric; store.
4. **P-value** = (1 + count of null ≥ observed) / (1 + N) for "better is higher"; use "≤" if lower is better. One-sided or two-sided depending on the question.
5. Optionally plot the null distribution and mark the observed value.

**Time series:** Shuffling returns destroys order; for "better than random" you often shuffle **returns** so the null is "no predictability." For strategy vs strategy, you can permute **assignment** of periods to strategies. For labels (e.g. "level hit" vs "miss"), shuffle labels. Tools: custom loop, or e.g. `scipy.stats` permutation tests where applicable.

## Inputs

Data: returns, signals, or labels (depending on null). Config: metric, number of permutations (e.g. 1_000–10_000), one- vs two-sided, seed for reproducibility.

## Outputs

P-value; optional summary of null distribution (mean, percentiles); optional plot. Location: results/, logs/.

## Interpretation

Low p-value (e.g. &lt; 0.05): observed metric is unlikely under the null (e.g. strategy is better than random). High p-value: could be luck; don't rely on the edge. For strategy comparison, p-value answers "is the difference in metric due to chance?"

## Related tests

[statistical_significance.md](statistical_significance.md) (permutation is one way to implement it); [bootstrap.md](bootstrap.md), [block_bootstrap.md](block_bootstrap.md) (other resampling; block bootstrap preserves time order); grid_search, rolling_window_backtests (params/backtests you may want to test with permutation).
