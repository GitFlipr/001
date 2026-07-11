# MCMC linear regression (Metropolis–Hastings)

## What it is

When the posterior for β has no closed form (non-conjugate prior, heavy tails), **Markov Chain Monte Carlo (MCMC)** numerically samples from the posterior. **Metropolis–Hastings** constructs a Markov chain whose stationary distribution is the posterior; collect samples after burn-in for point estimates and credible intervals.

## When to use it

When conjugate Bayesian regression is not available—e.g. non-normal priors, complex likelihoods. Use when you need full posterior distribution (uncertainty bands, credible intervals) rather than a single point estimate.

## How it works

1. Propose β' from symmetric proposal (e.g. Gaussian centered at current β).
2. Compute acceptance ratio α = f(y|β')f(β') / (f(y|β)f(β)); denominator cancels.
3. Accept β' with probability min(1, α); otherwise stay.
4. Repeat; discard burn-in; remaining samples ≈ posterior.

Tools: PyMC3, PyMC, or custom Metropolis–Hastings.

## Inputs

Data: target and features. Config: prior, likelihood, proposal scale, burn-in, chain length.

## Outputs

Posterior samples of β; mean and credible intervals; optionally histogram of posterior. Location: results/, logs/.

## Related tests

bayesian_regression (conjugate case); monte_carlo (simulation); permutation_test, bootstrap (other sampling).

## External reference

[MCMC linear regression (letianzj)](https://letianzj.github.io/mcmc-linear-regression.html).
