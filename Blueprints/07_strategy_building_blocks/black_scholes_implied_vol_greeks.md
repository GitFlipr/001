# Black–Scholes: implied volatility and Greeks

## What it is

Numerical **implied volatility** (IV) from market option price (invert Black–Scholes), and **Greeks** (delta, gamma, theta, vega, rho) for risk and hedging.

## When to use it

When you have option prices and need IV for regime/filters or risk; when you need sensitivities for hedging or P&L attribution.

## How it works

- **IV**: Solve (e.g. Newton–Raphson or Brent) for σ such that BS(σ) = market price. Handle bid/ask and put/call parity.
- **Greeks**: Analytic formulas under Black–Scholes (delta, gamma, theta, vega, rho). Optionally finite-difference for non-vanilla.
- Tools: scipy.optimize, or option libraries (e.g. py_vollib, QuantLib).

## Inputs

Data: option prices (and spot, strike, expiry, rate). Config: option type (call/put), solver tolerance.

## Outputs

Implied vol per option; Greeks (and optionally vol surface). Location: results/, logs/.

## Interpretation

IV as market uncertainty; Greeks for hedge ratios and risk limits. Compare with distribution_fitting and VaR.

## Related tests

black_scholes.md (core); black_scholes_variations.md (dividends, American, binomial); var_cvar.
