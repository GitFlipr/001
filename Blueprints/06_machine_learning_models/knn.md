# k-nearest neighbours (kNN)

## What it is

Predicts from the k closest training points (by distance). Classification: vote; regression: average. Simple, no training; sensitive to scale and k.

## When to use it

As a non-linear baseline. When you want a simple, interpretable (neighbour-based) model. Compare with random forest and SVM.

## How it works

For each test point, find k nearest training points; predict by vote (class) or average (regression). Output: accuracy or regression metrics. Tools: sklearn KNeighborsClassifier/Regressor.

## Inputs

Features and target. Config: k, distance metric, target, features.

## Outputs

Metrics; optionally plots. Location: results/, logs/.

## Related tests

Random forest, SVM; time_series_cv; basic_metrics.
