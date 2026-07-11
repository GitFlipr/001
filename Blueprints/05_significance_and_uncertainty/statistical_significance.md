# Statistical significance (vs random baseline)

## What it is

Tests whether a rule or level beats a random baseline (permutation or simulation).

## When to use it

To validate levels or strategies are not luck. After Fibonacci or Gann. Before going live.

## How it works

Metric on real data; simulate random; compare; p-value. Custom or permutation test.

## Inputs

Price/level data; strategy or level. Config: metric, N simulations.

## Outputs

P-value or comparison. Location: results/, logs/.

## Related tests

[permutation_test.md](permutation_test.md); [bootstrap.md](bootstrap.md); swing detection; Fibonacci; Gann.
