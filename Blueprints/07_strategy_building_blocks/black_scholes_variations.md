# Black–Scholes variations (dividends, American, binomial)

## What it is

Extensions of the basic Black–Scholes setting: **continuous or discrete dividends**, **American-style** exercise (early exercise), and **binomial/trinomial trees** as discrete-time alternatives that handle Americans and path-dependence.

## When to use it

- **Dividends**: When the underlying pays dividends; use continuous yield or discrete dividend schedule and adjust spot/forward.
- **American**: When the option is American (e.g. listed US equity options); use closed-form approximations (e.g. Bjerksund–Stensland, Barone-Adesi–Whaley) or trees.
- **Binomial/trinomial**: When you need American pricing, path-dependent payoffs, or a simple teaching benchmark; trees converge to BS for European under appropriate limits.

## How it works

- **Dividends**: In BS, replace spot S by S minus PV(dividends), or use continuous yield q in the formula. Same formula, adjusted spot or cost-of-carry.
- **American approximation**: Bjerksund–Stensland or Barone-Adesi–Whaley give closed-form approximations for American put/call; compare to binomial for sanity check.
- **Binomial**: Build a recombining tree (risk-neutral probabilities, up/down from vol and step); back-induce option value; early exercise = max(hold, exercise) at each node. Trinomial: similar with three branches.
- Tools: scipy, optional QuantLib or py_vollib for American/dividends.

## Inputs

Data: spot, strike, expiry, rate, vol; optionally dividend schedule or yield. Config: style (European/American), tree steps (if binomial).

## Outputs

Theoretical price and optionally Greeks for European-with-dividends; American price (and early-exercise boundary if desired); binomial/trinomial price for comparison. Location: results/, logs/.

## Interpretation

American ≥ European for call on non-dividend stock (often equal); American put often strictly greater. Binomial should match BS for European as steps increase. Use for option strategies and stress tests that need American or dividends.

## Related tests

black_scholes.md; black_scholes_implied_vol_greeks.md; price_models.md (jump-diffusion, stochastic vol); monte_carlo.md.
