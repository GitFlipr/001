# Variance ratio test (random walk)

## What it is

The variance ratio test checks whether a return series behaves like a **random walk** (or martingale). Under a random walk, the variance of k-period returns should be k times the variance of 1-period returns. The test statistic measures the ratio Var(k-period) / (k × Var(1-period)); under the null of a random walk, this ratio is 1.

## When to use it

To test whether returns are predictable (mean-reverting or trending) or unpredictable (random walk). Common in finance when deciding whether to use momentum vs mean-reversion models. Complements ADF/KPSS: those test for unit roots; variance ratio tests for the specific random-walk implication on variance scaling.

## How it works

1. Compute 1-period returns and k-period overlapping (or non-overlapping) returns.
2. Compute sample variances: Var(r_1) and Var(r_k).
3. Variance ratio VR(k) = Var(r_k) / (k × Var(r_1)).
4. Under random walk, VR(k) → 1. VR &gt; 1 suggests positive autocorrelation (momentum); VR &lt; 1 suggests negative autocorrelation (mean reversion).
5. Test statistic with asymptotic normal or bootstrap null. Tools: custom implementation; some packages offer variance ratio tests (e.g. `arch`, custom).

## Inputs

Data: return series (or price series to compute returns). Config: lag k (e.g. 2, 5, 10), overlapping vs non-overlapping, significance level.

## Outputs

Variance ratio VR(k); test statistic; p-value; conclusion (random walk or not). Optional: VR for multiple k. Location: results/, logs/.

## Interpretation

VR ≈ 1: consistent with random walk (unpredictable). VR &gt; 1: positive autocorrelation; momentum strategies may work. VR &lt; 1: mean reversion; contrarian strategies may work. Small samples: use bootstrap for inference.

## Related tests

ADF, KPSS, Phillips–Perron (unit roots, stationarity); ACF/PACF (autocorrelation structure); changepoint detection (structure can change over time).