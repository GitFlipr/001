# Logistic regression

## What it is

Logistic regression models a **binary outcome** (e.g. direction: up/down, or hit a threshold) using a linear combination of features passed through a logistic function. Output is a probability; you classify by threshold (e.g. >0.5 = up).

## When to use it

For direction or binary classification as a baseline. To get interpretable coefficients (log-odds). Often compared with linear regression (continuous target) and with random forest/SVM (non-linear classification).

## How it works

Model: P(y=1) = 1 / (1 + exp(-(b0 + b1*x1 + ...))). Fit by maximizing log-likelihood (or minimizing cross-entropy). Output: coefficients, accuracy, precision, recall, confusion matrix. Tools: sklearn LogisticRegression.

## Inputs

Data: binary target (0/1 or label) and features. Config: target, features, C (regularization), optional class weight.

## Outputs

Accuracy, precision, recall, coefficients; optionally confusion matrix. Location: results/, logs/.

## Interpretation

Strong accuracy: use as baseline; consider regime splits. Weak: try more features or non-linear models. Use with basic_metrics for comparison across models.

## Related tests

Linear regression (continuous target); basic_metrics; random_forest, SVM, kNN (other classifiers); permutation (test significance).
