# Factor exposure and risk decomposition

## What it is

**Factor exposure** measures how much a strategy or portfolio's returns move with common risk factors (e.g. market, size, value, momentum, volatility). **Risk decomposition** breaks total risk into factor contributions and idiosyncratic (residual) risk. Essential for multi-asset and factor-based strategies.

## When to use it

For **multi-asset** or **factor** strategies. To understand what drives returns and risk. To avoid unintended bets (e.g. "I thought I was market-neutral but I'm long beta"). For regulatory or risk reporting. When combining multiple strategies—see how factor exposures aggregate.

## How it works

**1. Factor model**
- Regress strategy returns on factor returns: R = α + β₁F₁ + β₂F₂ + … + ε.
- Factors: market (e.g. MKT-RF), size (SMB), value (HML), momentum (UMD), volatility (e.g. VIX change). Data: Fama-French, custom, or ETF proxies.
- Betas = factor exposures. α = alpha (factor-adjusted).

**2. Risk decomposition**
- Total variance = factor variance + idiosyncratic variance.
- Factor contribution: βᵢ² Var(Fᵢ) + covariance terms.
- Idiosyncratic: Var(ε). Tools: regression (OLS or robust); portfolio analytics libraries.

**3. Rolling exposure**
- Run regression over rolling windows to see how exposures change (e.g. beta drift).
- Regime-specific: exposures in calm vs stressed periods.

## Inputs

Strategy return series; factor return series (same frequency). Config: factors, window, regression method.

## Outputs

Factor betas (exposures); R²; alpha; risk decomposition (factor vs idiosyncratic); optional rolling plot. Location: results/, logs/.

## Interpretation

High market beta: strategy moves with market; consider hedging. Large idiosyncratic risk: strategy-specific; factors don't explain much. Rolling exposure shifting: strategy behavior changing; review or adjust.

## Related tests

Correlation breakdown; copulas (tail dependence); stress testing; VaR/CVaR; attribution (PnL decomposition); Information ratio (vs benchmark).