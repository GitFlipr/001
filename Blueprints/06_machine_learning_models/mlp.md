# Multilayer perceptron (MLP)

## What it is

Feedforward neural network: fully connected layers of neurons with non-linear activation. For regression or classification on tabular or flattened features.

## When to use it

As a non-linear baseline when order of inputs matters less than the feature set. Faster to train than LSTM/Transformer. Use before LSTM/Transformer for explicitly sequential data.

## How it works

Define layers (e.g. [64, 32], activation ReLU); fit by backprop and optimizer (e.g. Adam). Output: train/val metrics, optionally learning curves. Tools: sklearn MLPClassifier/Regressor, or PyTorch/TensorFlow.

## Inputs

Features and target. Config: layers, activation, optimizer, target, features.

## Outputs

Train/val metrics; optionally learning curves and predictions. Location: results/, logs/.

## Related tests

Linear_model, random_forest (baselines); LSTM, Transformer (sequence models); time_series_cv; bias_variance.
