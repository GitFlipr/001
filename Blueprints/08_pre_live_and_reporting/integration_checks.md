# Integration checks (pre-live)

## What it is

Pre-live checklist to verify all systems are ready: **API connectivity**, **config validity**, **data freshness**, **credentials**, and **environment**. Pass/fail summary per check with actionable failure messages.

## When to use it

Before going live. Before each pseudo-live run. As part of a CI/CD or daily health check. To catch misconfig, stale data, or auth failures before they cause live losses.

## How it works

Run a suite of checks; each outputs pass/fail and optional details. Failures block or warn depending on severity.

**1. API connectivity**
- Ping exchange/broker API (e.g. REST health endpoint).
- Verify WebSocket connection (if used).
- Check latency (round-trip time).
- Verify auth (API key valid, permissions correct).
- Rate limit: confirm within limits; test that 429 is handled.

**2. Config schema and validity**
- Validate config file against schema (YAML/JSON).
- Required keys present: symbols, data path, credentials path, risk params.
- Sensible ranges: position limits, max drawdown threshold, etc.
- No placeholder values (e.g. "REPLACE_ME") in production config.

**3. Data freshness**
- Last timestamp of each data feed; flag if older than threshold (e.g. 1 hour for real-time).
- Check for gaps (missing bars) in recent history.
- Verify symbol list matches available data.

**4. Credentials and secrets**
- API keys/ secrets load without error.
- No secrets in logs or stdout.
- Permissions: read/write as required; sandbox vs live environment correct.

**5. Environment**
- Python/package versions match expected.
- Required env vars set (e.g. API_URL, LOG_LEVEL).
- Disk space, memory sufficient.
- Log directory writable.

**6. Risk and circuit breakers**
- Max position, max drawdown, kill switch config present and loaded.
- Dry-run / paper mode flag set correctly for pre-live.

## Inputs

Paths to config; checklist definition (which checks to run); thresholds (e.g. max data age). Config: paths, checklist items, failure action (block/warn).

## Outputs

Pass/fail summary per check; failed checks with details; warnings; optional JSON report. Location: results/, logs/.

## How to run / implement

Run the integration_check module before pseudo-live or live. Implement: config loader + schema validator; API client for ping/auth; data loader for freshness; env checker. Output to stdout and file.

## Interpretation

All pass: proceed with caution. Any critical fail: do not go live; fix and re-run. Warnings: investigate; may proceed if understood. Re-run after any config or env change.

## Related tests

Pseudo_live_testing; slippage_latency_testing; kill_switch_circuit_breaker; paper_trading_reconciliation; report_generation; attribution.