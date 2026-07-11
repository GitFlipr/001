# Sharpe, Sortino, and Calmar ratios

## What it is

Risk-adjusted return ratios. **Sharpe**: (return - risk-free rate) / volatility (total risk). **Sortino**: same but uses downside deviation. **Calmar**: return / max drawdown (often annualized).

## When to use it

To compare strategies on a risk-adjusted basis. Sharpe for total risk; Sortino for downside; Calmar for drawdown. Standard inputs for reporting and capital allocation.

## How it works

From equity curve or return series: compute return, volatility (or downside deviation), max drawdown; apply risk-free rate if needed. Annualize if desired. Tools: custom or pandas.

## Inputs

Equity curve or return series (e.g. from backtests). Config: risk-free rate, period for annualization.

## Outputs

Sharpe, Sortino, Calmar (and often annualized); optionally plots. Location: results/, logs/.

## Related tests

Drawdowns; VaR/CVaR; rolling window backtests; report_generation.
