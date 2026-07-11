# Ulcer index

## What it is

The **Ulcer Index** measures the depth and duration of drawdowns as a single statistic. It is the root-mean-square of drawdown percentages over time. Unlike max drawdown (one number), it penalizes long, shallow drawdowns and rewards quick recoveries.

## When to use it

When **drawdown duration and path** matter more than a single worst drop. For strategies where sustained underwater periods are unacceptable. Complements max drawdown and Calmar ratio.

## How it works

1. Compute drawdown at each time: DD_t = (peak_t − price_t) / peak_t × 100.
2. Ulcer Index = sqrt(mean(DD_t²)). Units: percentage (like drawdown).
3. Lower is better. A strategy with one sharp drawdown that recovers fast has lower Ulcer than one with a long, shallow drawdown.
4. Can be used in a ratio: return / Ulcer (Ulcer-performance ratio). Tools: custom or pandas.

## Inputs

Equity curve or price series. Config: period (e.g. daily); optional annualization.

## Outputs

Ulcer index (percentage); optionally Ulcer-performance ratio. Location: results/, logs/.

## Interpretation

Lower Ulcer = less prolonged pain. Compare strategies: similar Sharpe but different Ulcer suggests different drawdown profiles. Useful for risk-averse investors focused on time underwater.

## Related tests

Drawdowns (max, average, duration); Calmar ratio (return/max drawdown); Sharpe/Sortino (other risk-adjusted metrics).