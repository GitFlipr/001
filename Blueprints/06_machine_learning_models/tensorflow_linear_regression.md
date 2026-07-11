# TensorFlow / Keras linear regression

## What it is

Linear regression implemented via **TensorFlow** (low-level API) or **Keras** (high-level): train with stochastic gradient descent and backpropagation instead of the normal equation. Minimal feed-forward network (one layer, no activation)—same output as OLS but different optimization path. Gateway to deep learning (LSTM, Transformer).

## When to use it

As a bridge to neural nets—same problem (linear regression) solved with gradient descent. Useful when you plan to extend to nonlinear or sequence models. Not needed if OLS suffices; use when learning TF/Keras pipeline or preparing for LSTM/time-series DL.

## How it works

**Low-level:** Define variables w, b; loop over batches; GradientTape for loss = MSE(y, x*w+b); tape.gradient; apply updates.  
**High-level:** tf.keras.Sequential with Dense(1); model.compile(optimizer, loss); model.fit. Batch size and learning rate affect convergence; intercept may converge more slowly than slope.

## Inputs

Data: target and features. Config: batch size, epochs, learning rate, optimizer (e.g. Adam).

## Outputs

Fitted w (slope) and b (intercept); loss curve. Location: results/, logs/.

## Related tests

[linear_model](../04_baselines_tuning_validation/linear_model.md) (OLS baseline); LSTM, MLP (Phase 6); mean_squared_error.

## External reference

[TensorFlow linear regression (letianzj)](https://letianzj.github.io/tensorflow-linear-regression.html).
