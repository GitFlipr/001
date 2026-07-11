# LSTM (long short-term memory)

## What it is

Recurrent neural network that can remember long-range patterns. For sequence data (e.g. price/return history). Often better than MLP when sequence length and timing matter.

## When to use it

For next-step or multi-step prediction from sequences. When order and long-range dependence matter. Use predictions as signals for backtests.

## How it works

Define LSTM layers (hidden size, number of layers); train on sequences (e.g. last N bars). Output: train/val loss and metrics, optionally forecast plots. Tools: PyTorch, TensorFlow, Keras. GPU recommended.

## Inputs

Sequence data (e.g. [batch, seq_len, features]); target. Config: sequence length, layers, hidden size, target.

## Outputs

Train/val metrics; optionally forecast plots and predictions. Location: results/, logs/; weights in save_dir.

## Related tests

MLP, Transformer; time_series_cv; rolling origin validation; rolling window backtests; Sharpe, drawdowns.

## External reference

[RNN stock prediction (LSTM/GRU) (letianzj)](https://letianzj.github.io/rnn-stock-prediction.html) — sliding window, HLC features, TensorFlow LSTM/GRU for S&P 500.
