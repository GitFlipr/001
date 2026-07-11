# Entropy (sample and information-theoretic)

## What it is

Measures randomness: Shannon entropy, sample entropy, approximate entropy. Higher means more unpredictable; lower can mean structure or regimes.

## When to use it

To quantify predictability; compare regimes; feature or regime detection. Uncommon but useful for non-linear structure.

## How it works

Shannon: -sum(p*log(p)) over bins. Sample entropy: pattern repetition over embedding; no binning. Use numpy or antropy.

## Inputs

Time series. Config: embedding dimension, tolerance, bins.

## Outputs

Entropy value(s); optional rolling entropy. results/, logs/.

## Interpretation

Drop in entropy: more structure. Rise: more noise. Use with HMM and changepoint.

## Related tests

Hurst; HMM regime; changepoint detection; distribution fitting.
