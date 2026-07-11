# Markov chains (state transition probabilities)

## What it is

A Markov chain models the probability of moving from one state to another; next state depends only on current state. You estimate a transition matrix and optionally steady-state distribution.

## When to use it

To model state transitions (e.g. regime persistence). As a baseline for state-based prediction. For steady-state long-run probabilities.

## How it works

Define states; estimate P(i→j) from counts. Optionally compute steady-state. Evaluate accuracy or log-likelihood. Tools: custom or numpy.

## Inputs

Data: sequence of states (or series to discretize). Config: number of states.

## Outputs

Transition matrix, steady-state; optionally accuracy. Location: results/, logs/.

## Interpretation

High diagonal: states persist. Use for state-based strategies or as features. Compare with HMM (latent vs observed states).

## Related tests

HMM regime; logistic regression; basic_metrics; changepoint detection.
