# Reinforcement learning for option pricing

## What it is

**American option pricing as MDP:** State = (price, time to maturity); action = exercise or hold. Optimal exercise boundary learned via **DQN (Deep Q-Network)** or similar. Baseline from QuantLib (Black–Scholes, Barone–Adesi–Whaley, binomial tree). RL agent learns Q-table/policy; price = expected discounted payoff under optimal policy.

## When to use it

When classical methods (binomial, Longstaff–Schwartz) are costly or when extending to exotics, stochastic vol, or path-dependent options. Research application; validate against QuantLib or analytic benchmarks first.

## How it works

1. **Gym environment:** State = (S_t, τ); step() simulates GBM; reward = exercised payoff (discounted) or 0 if hold.
2. **Train DQN:** TF-Agents or custom; episodes = simulated paths; learn Q(S, exercise vs hold).
3. **Price:** Run many paths with learned policy; average discounted payoff. Use control variates (European) to reduce variance.

Tools: OpenAI Gym; TensorFlow TF-Agents; QuantLib for baseline.

## Inputs

Option params (K, T, r, σ); GBM or other process. Config: network size, episodes, batch size.

## Outputs

Learned policy; option price estimate; comparison to baseline (Baw, binomial). Location: results/, logs/.

## Related tests

[black_scholes](../07_strategy_building_blocks/black_scholes.md); [monte_carlo](../05_significance_and_uncertainty/monte_carlo.md); LSTM, Transformer (other DL).

## External references

[Option pricing using RL (letianzj, Medium)](https://medium.com/@letian.zj/option-pricing-using-reinforcement-learning-ad2ddca7735b) — DQN, AmeriOption gym env, TF-Agents. Code: [american_option.ipynb](https://github.com/letianzj/QuantResearch/blob/master/ml/american_option.ipynb), [reinforcement_trader.ipynb](https://github.com/letianzj/QuantResearch/blob/master/ml/reinforcement_trader.ipynb).
