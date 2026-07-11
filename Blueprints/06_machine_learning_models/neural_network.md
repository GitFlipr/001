# Neural network (overview)

## What it is

Layers of connected units (neurons) that learn non-linear mappings from inputs to target. Umbrella term for MLP (feedforward), LSTM (recurrent), Transformer (attention).

## When to use it

When linear or tree models are insufficient. For regression or classification with complex patterns. Validate with time_series_cv and walk-forward.

## How it works

Choose architecture: MLP (tabular), LSTM (sequences), Transformer (long sequences). Train by minimizing loss (e.g. MSE, cross-entropy). Output: train/val metrics, optionally predictions and plots. Tools: PyTorch, TensorFlow, Keras.

## Inputs

Features and target; config for layers, activation, optimizer, sequence length (if applicable).

## Outputs

Train/val loss and metrics; optionally learning curves and predictions. Location: results/, logs/; weights in save_dir.

## Related tests

MLP, LSTM, Transformer (specific architectures); time_series_cv; rolling window backtests; bias_variance.
