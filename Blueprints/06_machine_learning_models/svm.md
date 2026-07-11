# Support vector machines (SVM)

## What it is

Finds a boundary that maximizes the margin between classes (classification) or fits a function with support vectors (regression). Can use kernels (linear, RBF, etc.) for non-linearity.

## When to use it

For classification or regression when you want a margin-based model. Compare with random forest and kNN on the same data. Use time_series_cv for honest metrics.

## How it works

Fit SVM with chosen kernel and C/gamma. Output: accuracy or regression metrics, optionally support vector info. Tools: sklearn SVC, SVR.

## Inputs

Features and target. Config: kernel, C, gamma, target, features.

## Outputs

Metrics; optionally support vectors and plots. Location: results/, logs/.

## Related tests

Random forest, kNN; time_series_cv; rolling window backtests; basic_metrics.
