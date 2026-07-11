# Report generation

## What it is

Aggregates backtest and risk outputs into one report (HTML, PDF, or notebook).

## When to use it

For stakeholders. To pull together walk-forward, pseudo-live, Sharpe, drawdowns, VaR.

## How it works

Collect results from paths; render template; write report. Jinja, WeasyPrint, nbconvert, or custom.

## Inputs

Paths to backtest/risk results. Config: input paths, output path, format.

## Outputs

Report file; optionally assets. Location: results/, logs/.

## Related tests

Sharpe, drawdowns, VaR; attribution; pseudo_live_testing.
