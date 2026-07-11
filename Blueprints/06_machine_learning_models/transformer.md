# Transformer (time series)

## What it is

Architecture using attention over sequences (no recurrence). For long-context time series when you need to weight which past inputs matter for the current step.

## When to use it

For long sequences when LSTM is slow or limited. When you want to inspect attention (interpretability). Compare with LSTM on the same data.

## How it works

Encode sequence with self-attention layers; decode or pool to prediction. Train by minimizing loss. Output: train/val metrics, optionally attention plots and forecasts. Tools: PyTorch, TensorFlow. GPU with enough VRAM recommended.

## Inputs

Sequence data; target. Config: sequence length, attention heads, layers, target.

## Outputs

Train/val metrics; optionally attention plots and forecasts. Location: results/, logs/; weights in save_dir.

## Related tests

LSTM, MLP; time_series_cv; rolling window backtests; Sharpe, drawdowns.
