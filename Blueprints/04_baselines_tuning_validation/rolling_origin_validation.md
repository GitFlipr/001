# Rolling origin validation

## What it is

Train up to a point (origin), then predict the next period(s); roll the origin forward. Expanding or rolling train set; fixed or expanding forecast horizon.

## When to use it

For time-series model selection and tuning. To get honest out-of-sample metrics over many origins. Use with LSTM, Transformer, or any model that needs train/val in time.

## How it works

For each origin: train on past (expanding or rolling); predict next; compute metric. Aggregate metrics across origins. Tools: custom or sktime.

## Inputs

Data; model; config: origin step, train length, forecast horizon.

## Outputs

Metrics per origin; aggregate (mean, std, percentiles); optionally plots. Location: results/, logs/.

## Related tests

Time_series_cv; rolling window backtests; pseudo_live_testing; LSTM, Transformer.
