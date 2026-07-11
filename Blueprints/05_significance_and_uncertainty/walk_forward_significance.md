# Walk-forward significance (rolling windows)

## What it is

When you run **rolling origin** or **rolling window backtests**, you get many out-of-sample metrics (one per window). Walk-forward significance tests whether the *aggregate* of these OOS results is better than random—accounting for the fact that windows overlap and metrics are correlated.

## When to use it

After rolling_origin_validation or rolling_window_backtests. When you want to know: "Across all my OOS windows, is the strategy genuinely better than random?" Standard significance tests (permutation on a single series) may not apply directly because windows are not independent.

## How it works

1. **Collect OOS metrics** from each walk-forward window (e.g. Sharpe, hit rate per window).
2. **Null:** Under random, each window's metric would follow a null distribution. Options:
   - **Permutation per window:** Shuffle returns in each window; recompute metric; repeat. Compare observed to null.
   - **Block permutation:** Permute entire windows (preserve within-window structure).
   - **Bootstrap of window metrics:** Resample windows with replacement; get distribution of mean Sharpe (or median, etc.); check if observed mean is in tail.
3. **Aggregate test:** E.g. one-sided test on mean(metric across windows) vs null distribution of that mean.
4. Adjust for multiple comparisons if testing many strategies or levels.

## Inputs

Results from rolling origin or rolling window backtests (metrics per window). Config: metric, null construction (permutation vs bootstrap), N simulations.

## Outputs

P-value for "aggregate OOS result better than random"; optional distribution of null mean; conclusion. Location: results/, logs/.

## Interpretation

Low p-value: strategy performs better than random across OOS windows. High p-value: OOS performance could be luck; don't rely on the edge. Critical: use proper null that respects window structure (overlap, correlation).

## Related tests

Rolling origin validation; rolling window backtests; permutation test; bootstrap; block bootstrap; statistical significance.