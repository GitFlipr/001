# Information ratio

## What it is

The **Information Ratio (IR)** measures active return per unit of active risk: (portfolio return − benchmark return) / tracking error. It answers: "How much excess return do I get per unit of deviation from the benchmark?"

## When to use it

For **active strategies** with a defined benchmark (e.g. S&P 500, risk-free rate, or custom index). To compare managers or strategies on consistency of alpha. Standard in active management and hedge fund reporting.

## How it works

IR = (R_portfolio − R_benchmark) / σ(R_portfolio − R_benchmark). The denominator is the standard deviation of active returns (tracking error). Higher IR = more excess return per unit of tracking error. Often annualized. Tools: custom or pandas.

## Inputs

Portfolio and benchmark return series (or equity curves). Config: period for annualization; alignment (same frequency).

## Outputs

Information ratio; optionally annualized; tracking error; active return. Location: results/, logs/.

## Interpretation

IR &gt; 0.5 is often considered strong; IR &gt; 1 very strong. Negative IR: underperforming the benchmark on a risk-adjusted basis. Compare to Sharpe when benchmark is risk-free: IR uses benchmark as reference, Sharpe uses risk-free rate.

## Related tests

Sharpe/Sortino/Calmar (other risk-adjusted ratios); drawdowns; VaR/CVaR; report_generation; attribution (decompose active return).