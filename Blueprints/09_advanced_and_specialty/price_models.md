# Price models (GBM, jump-diffusion, stochastic vol)

## What it is

Models for how prices evolve: geometric Brownian motion (GBM), jump-diffusion, stochastic volatility, local volatility. Used to simulate paths, value derivatives, or test strategy behavior under different price dynamics.

## When to use it

When you need path simulation (Monte Carlo), option pricing beyond Black-Scholes, or stress tests with fat tails and vol clustering. Use GBM for simple log-normal; jump-diffusion for rare large moves; stochastic vol for time-varying vol.

## How it works

GBM: dS = mu*S*dt + sigma*S*dW. Jump-diffusion adds Poisson jumps. Stochastic vol: separate process for variance (e.g. Heston). Local vol: sigma(S,t) from surface. Implement with scipy, QuantLib, or custom SDE solvers.

## Inputs

Returns or price series; parameters (drift, vol, jump intensity, mean reversion). Optionally implied vol surface for local vol.

## Outputs

Simulated paths; option prices or Greeks; distribution of outcomes. Location: results/, logs/.

## Interpretation

Compare simulated PnL vs historical. Fat tails from jumps; vol clustering from stochastic vol. Use with Monte Carlo and stress testing.

## Related tests

Black-Scholes; Monte Carlo; stress testing and scenarios; distribution fitting; VaR/CVaR.
