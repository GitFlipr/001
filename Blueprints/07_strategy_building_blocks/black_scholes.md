# Black–Scholes (option pricing and implied volatility)

## What it is

Black–Scholes gives theoretical option price and implied volatility from option prices, or you can estimate historical vol from returns. Used for volatility reference and option strategies.

## When to use it

To get implied vol for risk or regime. As benchmark for option strategies. With no options data: use returns for historical vol (sizing, filters).

## How it works

From spot, strike, expiry, rate, vol: compute option price. In reverse: from market price get implied vol. From returns: annualized std = historical vol. Optionally Greeks. Tools: scipy or option libraries.

## Inputs

Data: option prices or returns. Config: option path or use_returns.

## Outputs

Implied vol, theoretical prices; optionally Greeks. Location: results/, logs/.

## Interpretation

High vol: position sizing or regime logic. Compare with distribution_fitting and VaR.

## Related tests

**Black–Scholes variations:** [black_scholes_implied_vol_greeks.md](black_scholes_implied_vol_greeks.md) (IV and Greeks); [black_scholes_variations.md](black_scholes_variations.md) (dividends, American, binomial/trinomial).  
Distribution fitting; VaR/CVaR; HMM regime.
