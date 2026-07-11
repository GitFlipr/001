# Kill switch and circuit breaker (pre-live)

## What it is

**Kill switch:** manual or automatic halt of all trading (cancel open orders, flat positions or not, stop new orders). **Circuit breaker:** automatic halt when a threshold is breached (e.g. max drawdown, max loss per day, connection loss). Both protect capital when something goes wrong.

## When to use it

Before going live. Design into the system from the start. Test that they work under failure conditions (network drop, exchange error, bug). Required for responsible automated trading.

## How it works

**Kill switch:**
- Trigger: manual (button, CLI, API call) or automatic (e.g. "no heartbeat for N seconds").
- Action: cancel all open orders; optionally flatten positions (market orders); stop accepting new signals; log state; alert.
- Must work independently of main strategy process (e.g. separate monitor, broker-native kill).

**Circuit breaker:**
- Triggers: drawdown &gt; X%; daily loss &gt; Y; N consecutive errors; exchange disconnect &gt; M seconds; position limit exceeded.
- Action: same as kill switch; optionally tiered (pause vs full halt).
- Config: thresholds, cooldown before resume, who can reset.

**Testing:**
1. Simulate trigger (e.g. fake drawdown, kill network).
2. Verify: orders cancelled, no new orders, state logged, alert sent.
3. Verify recovery: after reset, system can resume or requires manual intervention (document which).

## Inputs

Config: thresholds (drawdown, loss, latency), kill switch endpoint, alert config. Runtime: equity curve, position state, error count, connection status.

## Outputs

Log of trigger events; state snapshot at halt; alert notifications. Location: logs/; alerts (email, Slack, etc.).

## Interpretation

Kill switch tested and working: you can stop quickly in an emergency. Circuit breaker tuned: avoids runaway losses. Document recovery procedure; practice it.

## Related tests

Integration_checks; pseudo_live_testing; slippage_latency_testing; report_generation; attribution (for post-mortem).