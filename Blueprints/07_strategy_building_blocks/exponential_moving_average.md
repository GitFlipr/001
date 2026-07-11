# Exponential moving average (EMA / EWMA)

## What it is

**Exponentially weighted moving average (EWMA or EWA):** Smoothing where recent observations get more weight. Y_n = α X_n + (1−α) Y_{n-1} = Y_{n-1} + α(X_n − Y_{n-1}). For regular intervals: α = 2/(1+days). Related to **half-life** H: α ≈ −ln(0.5)·Δt/H.

**Irregular tick intervals:** α = 1 − exp(−Δt/G) where G is decay timescale. EWA decays at same rate regardless of path (one tick at 1s or two ticks at 400ms+600ms).

## When to use it

For prices and volatilities; golden/death cross strategies; intraday when ticks arrive irregularly. Use half-life or G to tune responsiveness vs smoothness.

## How it works

**Regular:** Standard EMA with α = 2/(span+1). **Irregular:** Compute α per tick from time elapsed since last update; apply same update formula. Tools: pandas ewm; custom for irregular ticks.

## Inputs

Price or volatility series; optional span/half-life. For irregular: timestamps + values.

## Outputs

EMA series; optionally dual EMA for crossover signals. Location: results/, logs/.

## Related tests

mean_reversion (half-life); cointegration_pairs_trading (Bollinger uses rolling mean); VWAP/TWAP (execution).

## External reference

[Exponential moving average (letianzj)](https://letianzj.github.io/exponential-moving-average.html) — regular and irregular intervals, half-life, intraday.
