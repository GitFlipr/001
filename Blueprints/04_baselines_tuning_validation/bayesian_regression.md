# Bayesian linear regression

## What it is

Linear regression from a Bayesian perspective: prior on β, likelihood from data, posterior via Bayes' theorem. With conjugate prior (normal-inverse-gamma), the posterior is closed-form normal. Supports **recursive/online updates** as new observations arrive—posterior becomes new prior.

## When to use it

When you want priors on coefficients, posterior uncertainty (credible intervals), or incremental learning. Alternative to OLS when you need to incorporate prior belief or update estimates in real time. Good for adaptive strategies and risk updates.

## How it works

Prior β ~ N(β₀, Σ_{β,0}); likelihood y|β,X ~ N(Xβ, σ_e I). Posterior β ~ N(β₁, Σ_{β,1}) with closed-form update. Iterate: observe (x,y) pairs, update β₁ and Σ_{β,1}, set as new prior. Tools: custom implementation; PyMC3 for generic cases.

## Inputs

Data: target and features. Config: prior (β₀, Σ₀), observation noise σ_e. Optional: batch size for recursive updates.

## Outputs

Posterior mean and covariance of β; evolution of β over updates; optionally credible intervals. Location: results/, logs/.

## Related tests

linear_model (OLS baseline); bayes_theorem; mcmc_regression (when conjugate prior unavailable); kalman_filter_regression (time-varying β).

## External reference

[Bayesian linear regression (letianzj)](https://letianzj.github.io/bayesian-linear-regression.html).
